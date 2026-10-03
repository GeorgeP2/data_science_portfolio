import copy

import numpy as np
import pytest
from fulfilment_optimisation.domain import DEPOT, Layout, distance
from fulfilment_optimisation.generator import describe, generate_instance, is_held_out
from fulfilment_optimisation.generator.order_arrivals import arrival_times, due_dates, line_counts
from fulfilment_optimisation.generator.sku_affinity import build_catalogue, draw_lines
from fulfilment_optimisation.registry import ROUTERS, SOLVERS
from fulfilment_optimisation.solvers import Deadline, check_feasible

from portfolio import ProjectPaths, load_config

GENERATOR = load_config(ProjectPaths.from_file(__file__).config).generator
LAYOUT = Layout(n_aisles=10, n_positions=20, location_length=1.0, aisle_spacing=5.0,
                end_offset=1.0, depot_offset=1.0)  # fmt: skip


def small(generator, orders: int):
    """The config with every scenario's order volume scaled down, for fast solver tests."""
    out = copy.deepcopy(dict(generator))
    out["scenarios"] = {name: dict(s or {}) for name, s in generator["scenarios"].items()}
    for settings in out["scenarios"].values():
        settings["orders_per_shift"] = orders
    return out


def test_same_seed_same_instance():
    a = generate_instance(GENERATOR, "baseline", 7)
    b = generate_instance(GENERATOR, "baseline", 7)
    assert a == b
    assert generate_instance(GENERATOR, "baseline", 8).orders != a.orders


def test_orders_are_in_arrival_order_and_fit_a_tour():
    instance = generate_instance(GENERATOR, "henn_waescher_like", 3)
    arrivals = [o.arrival_time for o in instance.orders]
    assert arrivals == sorted(arrivals)
    assert all(o.size <= instance.capacity for o in instance.orders)
    assert all(len(set(o.locations)) == o.size for o in instance.orders)  # distinct picks


@pytest.mark.parametrize("scenario", ["baseline", "high_affinity", "henn_waescher_like"])
@pytest.mark.parametrize("solver", sorted(SOLVERS))
def test_every_solver_is_feasible_on_generated_instances(scenario, solver):
    if solver == "cp_sat":
        pytest.importorskip("ortools")
    instance = generate_instance(small(GENERATOR, 40), scenario, 11)
    params = {"alns": {"max_iterations": 200}, "cp_sat": {"pool_iterations": 200}}.get(solver, {})
    for router in ("s_shape", "optimal"):
        solution = SOLVERS[solver](0, params).solve(instance, ROUTERS[router](), Deadline.after(2))
        check_feasible(instance, solution)


def mean_stats(name: str, seeds=range(6)) -> dict[str, float]:
    stats = [describe(generate_instance(GENERATOR, name, s)) for s in seeds]
    return {k: float(np.mean([s[k] for s in stats])) for k in stats[0]}


def test_presets_differ_measurably_from_baseline():
    base = mean_stats("baseline")
    assert mean_stats("peak_day")["peak_orders_per_hour"] > 2 * base["peak_orders_per_hour"]
    assert mean_stats("high_affinity")["multi_line_single_aisle_share"] > (
        base["multi_line_single_aisle_share"] + 0.4
    )
    assert mean_stats("tight_due_dates")["median_slack_s"] == pytest.approx(600)
    assert base["median_slack_s"] > 10_000
    hw = mean_stats("henn_waescher_like")
    assert 13 < hw["mean_lines"] < 17  # uniform 5-25
    assert 1.2 < base["mean_lines"] < 1.3  # KIT's 0.8 / 0.15 / 0.05 over 1-3


def interarrival_cv(times: np.ndarray) -> float:
    gaps = np.diff(times)
    return float(gaps.std() / gaps.mean())


@pytest.mark.parametrize(
    ("stochasticity", "kit_cv", "tolerance"), [(0.0, 0.99, 0.05), (1.0, 2.78, 0.3)]
)
def test_wave_calibration_matches_kit(stochasticity, kit_cv, tolerance):
    cvs = [
        interarrival_cv(
            arrival_times(1000, np.random.default_rng(k), "waves", stochasticity=stochasticity)
        )
        for k in range(40)
    ]
    assert np.mean(cvs) == pytest.approx(kit_cv, abs=tolerance)


def test_abc_popularity_shares():
    rng = np.random.default_rng(0)
    catalogue = build_catalogue(LAYOUT, rng, popularity="abc")
    drawn = np.concatenate([draw_lines(catalogue, 1, 0.0, rng) for _ in range(20000)])
    shares = np.bincount(catalogue.abc_class[drawn], minlength=3) / len(drawn)
    assert shares == pytest.approx([0.8, 0.15, 0.05], abs=0.02)


def test_class_based_storage_puts_a_articles_in_the_best_slots():
    rng = np.random.default_rng(1)
    near = build_catalogue(LAYOUT, rng, storage_policy="A_closest_to_depot")
    walk = np.array([distance(DEPOT, loc, LAYOUT) for loc in near.locations])
    assert walk[near.abc_class == 0].max() <= walk[near.abc_class == 2].min()
    by_aisle = build_catalogue(LAYOUT, rng, storage_policy="A_to_X")
    aisles = np.array([loc.aisle for loc in by_aisle.locations])
    assert aisles[by_aisle.abc_class == 0].max() <= aisles[by_aisle.abc_class == 1].min()


def test_clustered_storage_keeps_clusters_in_one_aisle():
    rng = np.random.default_rng(2)
    catalogue = build_catalogue(LAYOUT, rng, storage_policy="clustered", cluster_size=8)
    aisles_per_cluster = [
        len({catalogue.locations[a].aisle for a in members})
        for members in catalogue.cluster_members
    ]
    # 8 articles fill 4 positions x 2 sides; a cluster spans 2 aisles only at an aisle boundary.
    assert np.mean([n == 1 for n in aisles_per_cluster]) > 0.7


def test_due_date_rules():
    rng = np.random.default_rng(3)
    arrivals = np.array([0.0, 100.0, 28000.0])
    assert list(due_dates(arrivals, rng, {"rule": "relative", "offset_seconds": 600})) == [
        600,
        700,
        28600,
    ]
    assert set(due_dates(arrivals, rng, {"rule": "shift_end"})) == {28800}
    options = [{"rule": "shift_end"}, {"rule": "relative", "offset_seconds": 1}]
    mixed = {"rule": "mixed", "weights": [1.0, 0.0], "options": options}
    assert set(due_dates(arrivals, rng, mixed)) == {28800}
    with pytest.raises(ValueError, match="unknown due-date rule"):
        due_dates(arrivals, rng, {"rule": "whenever"})


def test_line_counts_follow_weights():
    counts = line_counts(50_000, np.random.default_rng(4), [1, 2, 3], [0.8, 0.15, 0.05])
    assert np.bincount(counts, minlength=4)[1:] / len(counts) == pytest.approx(
        [0.8, 0.15, 0.05], abs=0.01
    )


def test_seed_ranges_are_disjoint():
    dev, held = GENERATOR["development_seeds"], GENERATOR["held_out_seeds"]
    assert dev[1] < held[0]
    assert is_held_out(GENERATOR, held[0]) and not is_held_out(GENERATOR, dev[1])
    assert "held-out" in generate_instance(GENERATOR, "baseline", held[0]).name


def test_unknown_scenario():
    with pytest.raises(ValueError, match="unknown scenario"):
        generate_instance(GENERATOR, "black_friday", 0)
