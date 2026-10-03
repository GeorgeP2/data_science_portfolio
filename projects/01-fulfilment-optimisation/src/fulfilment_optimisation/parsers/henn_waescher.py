"""Parser for the Henn & Wäscher order batching instances (OBSP distribution).

The archive holds 96 instances in two folders, ``MTCR_05_06_07`` and ``MTCR_055_065_075``. MTCR
only changes the due dates. Each instance ``<N>[s|l]-<orders>-<capacity>-0.txt`` comes with a
``sett<N>.txt`` in the same folder that describes the layout. Setting numbers are local to a
folder, so an instance is named ``<folder>/<stem>``.

Instance files list each order and then its articles::

    Order 0<TAB>number of articles 16<TAB>due date 198.542
    0<TAB>Aisle 1<TAB>Location 42

The aisle index counts each side of an aisle separately (0-19 for 10 aisles), so the real aisle is
``index // 2`` and the side is ``index % 2``. ``Location`` is the position along the aisle (0-44).

The settings give the geometry: aisle spacing is ``2 * cell_width + aisle_widt`` (5 LU), and the
depot is ``dis_ais_wa`` (1 LU) in front of the front cross aisle. The paper says 0.5 LU for the
depot, and T15's reproduction of published results decides which one is right. The 1 LU between
the cross aisles and the first and last positions isn't in the settings; it comes from the paper
(section 6.1).

Run from the project folder to summarise the downloaded instances::

    PYTHONPATH=src python -m fulfilment_optimisation.parsers.henn_waescher
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from fulfilment_optimisation.domain import Instance, Layout, Location, Order
from portfolio import ProjectPaths, load_config

END_OFFSET = 1.0  # LU between a cross aisle and the nearest pick position (paper, section 6.1)

_NAME = re.compile(
    r"(?P<setting>\d+)(?P<routing>[sl])-(?P<orders>\d+)-(?P<capacity>\d+)-(?P<rep>\d+)"
)
_SETTING = re.compile(r"(\w+):\s*(\S+)")
_ORDER = re.compile(r"Order (\d+)\tnumber of articles (\d+)\tdue date (\S+)")
_ARTICLE = re.compile(r"\d+\tAisle (\d+)\tLocation (\d+)")


@dataclass(frozen=True, slots=True)
class InstanceName:
    setting: int
    routing: str  # "s" (S-shape) or "l" (largest gap): the policy the reference results used
    n_orders: int
    capacity: int


def parse_name(stem: str) -> InstanceName:
    match = _NAME.fullmatch(stem)
    if match is None:
        raise ValueError(f"not a Henn & Wäscher instance name: {stem!r}")
    return InstanceName(
        setting=int(match["setting"]),
        routing=match["routing"],
        n_orders=int(match["orders"]),
        capacity=int(match["capacity"]),
    )


def read_settings(path: Path) -> dict[str, str]:
    """Read the ``key: value`` header of a ``sett<N>.txt``, stopping at the random-seed block."""
    settings = {}
    for line in path.read_text().splitlines():
        match = _SETTING.fullmatch(line.strip())
        if match is None:
            break
        settings[match[1]] = match[2]
    return settings


def layout_from_settings(settings: dict[str, str]) -> Layout:
    return Layout(
        n_aisles=int(settings["no_aisles_"]),
        n_positions=int(settings["no_cells__"]),
        location_length=float(settings["cell_lengt"]),
        aisle_spacing=2 * float(settings["cell_width"]) + float(settings["aisle_widt"]),
        end_offset=END_OFFSET,
        depot_offset=float(settings["dis_ais_wa"]),
    )


def load_henn_waescher(path: Path) -> Instance:
    name = parse_name(path.stem)
    settings = read_settings(path.parent / f"sett{name.setting}.txt")
    capacity = int(settings["m_no_a_p_b"])
    if (int(settings["no_orders_"]), capacity) != (name.n_orders, name.capacity):
        raise ValueError(f"{path.name}: file name disagrees with sett{name.setting}.txt")

    orders: list[Order] = []
    header: tuple[int, int, float] | None = None
    locations: list[Location] = []

    def close() -> None:
        if header is None:
            return
        order_id, expected, due_date = header
        if len(locations) != expected:
            raise ValueError(
                f"{path.name}: order {order_id} lists {len(locations)} articles,"
                f" header says {expected}"
            )
        orders.append(Order(order_id, tuple(locations), due_date))

    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        if order := _ORDER.fullmatch(line):
            close()
            header = (int(order[1]), int(order[2]), float(order[3]))
            locations = []
        elif (article := _ARTICLE.fullmatch(line)) and header is not None:
            aisle = int(article[1])
            locations.append(Location(aisle // 2, int(article[2]), side=aisle % 2))
        else:
            raise ValueError(f"{path.name}:{lineno}: unexpected line {line!r}")
    close()

    if len(orders) != name.n_orders:
        raise ValueError(f"{path.name}: {len(orders)} orders, file name says {name.n_orders}")
    return Instance(
        name=f"{path.parent.name}/{path.stem}",
        layout=layout_from_settings(settings),
        orders=tuple(orders),
        capacity=capacity,
    )


def instance_paths(root: Path) -> list[Path]:
    """Instance files under ``root``, sorted by folder and then setting number."""
    paths = [p for p in root.glob("*/*.txt") if _NAME.fullmatch(p.stem)]
    return sorted(paths, key=lambda p: (p.parent.name, parse_name(p.stem).setting))


def load_all(root: Path) -> list[Instance]:
    return [load_henn_waescher(path) for path in instance_paths(root)]


def main() -> None:
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    root = paths.data / cfg.data["henn_waescher"] / "obsp_instances"
    instances = load_all(root)

    classes: Counter[tuple[int, int, str]] = Counter()
    lines: Counter[tuple[int, int, str]] = Counter()
    for instance in instances:
        name = parse_name(instance.name.split("/")[1])
        key = (len(instance.orders), instance.capacity, name.routing)
        classes[key] += 1
        lines[key] += sum(order.size for order in instance.orders)

    print(f"{'orders':>6} {'capacity':>8} {'routing':>7} {'instances':>9} {'lines/inst':>10}")
    for key in sorted(classes):
        n_orders, capacity, routing = key
        print(
            f"{n_orders:>6} {capacity:>8} {routing:>7} {classes[key]:>9}"
            f" {lines[key] / classes[key]:>10.1f}"
        )
    n_orders = sum(len(i.orders) for i in instances)
    n_lines = sum(lines.values())
    print(f"\n{len(instances)} instances, {n_orders} orders, {n_lines} lines")


if __name__ == "__main__":
    main()
