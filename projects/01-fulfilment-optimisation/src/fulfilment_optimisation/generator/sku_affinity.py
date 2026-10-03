"""Articles, their popularity and co-purchase clusters, and where they are stored.

There is one article per storage slot (aisle, position, side), as in the KIT suite.

- **Popularity** is ``uniform``, ``abc`` (KIT's classes: the most popular 20% of articles take 80%
  of demand, the next 30% take 15% and the last 50% take 5%; T17), ``henn_waescher`` (what the
  benchmark files contain: A is 10% of articles with 52% of demand, B 20% with 36%, C 70% with
  12%) or ``henn_waescher_paper`` (their section 6.1 says B is 30% and C 60%; T20 found the files
  differ). Within a class, articles are equally popular.
- **Affinity** groups articles into clusters of ``cluster_size`` (within a popularity class, so
  clustering doesn't change popularity). When an order draws its next line, with probability
  ``affinity`` it takes it from the cluster of the line before. KIT orders show no affinity, so
  its scenarios use 0; the ``high_affinity`` preset raises it.
- **Storage** assigns articles to slots by popularity rank: ``random``, or one of KIT's class-based
  policies: ``A_closest_to_depot`` (shortest walk from the depot), ``A_to_X`` (lowest aisle
  numbers) and ``A_to_Y`` (closest to the front cross aisle). Under a class-based policy the classes
  fill the best slots in order, and articles are placed randomly within their class's slots.
  ``clustered`` (not in KIT) is correlated storage: classes fill slots aisle by aisle as in
  ``A_to_X``, but each cluster takes consecutive slots, so related articles share an aisle.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fulfilment_optimisation.domain import DEPOT, Layout, Location, distance

# Article share and demand share per class (A, B, C).
CLASS_PRESETS = {
    "abc": ((0.2, 0.3, 0.5), (0.8, 0.15, 0.05)),  # KIT
    "henn_waescher": ((0.1, 0.2, 0.7), (0.52, 0.36, 0.12)),  # the benchmark files (T20)
    "henn_waescher_paper": ((0.1, 0.3, 0.6), (0.52, 0.36, 0.12)),  # their section 6.1
}
STORAGE_POLICIES = ("random", "A_closest_to_depot", "A_to_X", "A_to_Y", "clustered")


@dataclass(frozen=True)
class Catalogue:
    """Articles 0..n-1 with their slot, demand probability, class and affinity cluster."""

    locations: tuple[Location, ...]
    popularity: np.ndarray  # sums to 1
    abc_class: np.ndarray  # 0 = A, 1 = B, 2 = C (all 0 under uniform popularity)
    cluster: np.ndarray  # cluster id per article
    cluster_members: tuple[np.ndarray, ...]
    cumulative: np.ndarray  # cumulative popularity, for drawing by binary search


def _slots(layout: Layout) -> list[Location]:
    return [
        Location(aisle, position, side)
        for aisle in range(layout.n_aisles)
        for position in range(layout.n_positions)
        for side in (0, 1)
    ]


def _classes(n: int, popularity: str) -> np.ndarray:
    if popularity == "uniform":
        return np.zeros(n, dtype=int)
    if popularity not in CLASS_PRESETS:
        choices = ["uniform", *CLASS_PRESETS]
        raise ValueError(f"unknown popularity {popularity!r}; choose from {choices}")
    bounds = np.round(np.cumsum(CLASS_PRESETS[popularity][0]) * n).astype(int)
    classes = np.empty(n, dtype=int)
    start = 0
    for c, end in enumerate(bounds):
        classes[start:end] = c
        start = end
    return classes


def _slot_order(slots: list[Location], layout: Layout, policy: str) -> list[int]:
    """Slot indices from best to worst under ``policy`` (ties broken by slot order)."""
    keys = {
        "A_closest_to_depot": lambda s: distance(DEPOT, s, layout),
        "A_to_X": lambda s: (s.aisle, s.position),
        "clustered": lambda s: (s.aisle, s.position),
        "A_to_Y": lambda s: (s.position, s.aisle),
    }
    if policy not in keys:
        raise ValueError(f"unknown storage policy {policy!r}; choose from {STORAGE_POLICIES}")
    key = keys[policy]
    return sorted(range(len(slots)), key=lambda i: (key(slots[i]), i))


def build_catalogue(
    layout: Layout,
    rng: np.random.Generator,
    popularity: str = "abc",
    storage_policy: str = "random",
    cluster_size: int = 8,
) -> Catalogue:
    slots = _slots(layout)
    n = len(slots)
    classes = _classes(n, popularity)  # article i's class; articles are ranked A first
    if popularity == "uniform":
        weights = np.full(n, 1 / n)
    else:
        demand = CLASS_PRESETS[popularity][1]
        weights = np.array([demand[c] / np.count_nonzero(classes == c) for c in classes])

    # Clusters of related articles, within each popularity class.
    cluster = np.empty(n, dtype=int)
    next_id = 0
    for c in np.unique(classes):
        articles = rng.permutation(np.flatnonzero(classes == c))
        for i in range(0, len(articles), cluster_size):
            cluster[articles[i : i + cluster_size]] = next_id
            next_id += 1
    members = tuple(np.flatnonzero(cluster == k) for k in range(next_id))

    # Assign articles to slots.
    if storage_policy == "random":
        slot_of = rng.permutation(n)
    else:
        ordered = _slot_order(slots, layout, storage_policy)
        slot_of = np.empty(n, dtype=int)
        for c in np.unique(classes):
            articles = np.flatnonzero(classes == c)
            start = int(articles[0])  # classes are contiguous in rank order
            class_slots = np.array(ordered[start : start + len(articles)])
            if storage_policy == "clustered":
                # Clusters in a random order, each taking consecutive slots.
                groups = rng.permutation(np.unique(cluster[articles]))
                in_order = np.concatenate([members[g] for g in groups])
                slot_of[in_order] = class_slots
            else:
                slot_of[articles] = rng.permutation(class_slots)

    popularity_ = weights / weights.sum()
    return Catalogue(
        locations=tuple(slots[s] for s in slot_of),
        popularity=popularity_,
        abc_class=classes,
        cluster=cluster,
        cluster_members=members,
        cumulative=np.cumsum(popularity_),
    )


def draw_lines(
    catalogue: Catalogue, n_lines: int, affinity: float, rng: np.random.Generator
) -> list[int]:
    """``n_lines`` distinct articles for one order."""
    n = len(catalogue.locations)
    n_lines = min(n_lines, n)
    chosen: list[int] = []
    taken: set[int] = set()
    while len(chosen) < n_lines:
        article = -1
        if chosen and rng.random() < affinity:
            members = catalogue.cluster_members[catalogue.cluster[chosen[-1]]]
            free = [m for m in members if m not in taken]
            if free:
                article = int(rng.choice(free))
        if article < 0:
            u = rng.random() * catalogue.cumulative[-1]
            article = int(np.searchsorted(catalogue.cumulative, u, side="right"))
            if article in taken:
                continue
        chosen.append(article)
        taken.add(article)
    return chosen
