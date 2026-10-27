"""Трекер деталей LEGO с использованием list / tuple / dict / set / enum."""

from __future__ import annotations

from enum import Enum, unique

@unique
class LegoColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"
    WHITE = "white"

Part = tuple[int, str, LegoColor]

class LegoCollection:
    """Коллекция деталей LEGO."""

    def __init__(self) -> None:
        self._parts: list[Part] = []
        self._by_id: dict[int, Part] = {}
        self._colors: set[LegoColor] = set()
        self._ids: set[int] = set()

    def add_part(
        self, part_id: int, name: str, color: LegoColor) -> bool:
        """Добавить деталь. Возвращает False, если id уже занят."""
        if part_id in self._ids:
            return False

        part: Part = (part_id, name, color)
        self._parts.append(part)
        self._by_id[part_id] = part
        self._ids.add(part_id)
        self._colors.add(color)
        return True

    # ---------- Поиск ----------
    def find_by_id(self, part_id: int) -> Part | None:
        return self._by_id.get(part_id)

    def find_by_color(self, color: LegoColor) -> list[Part]:
        return [p for p in self._parts if p[2] is color]

    def all_colors(self) -> set[LegoColor]:
        return set(self._colors)

    def all_ids(self) -> set[int]:
        return set(self._ids)

    def __len__(self) -> int:
        return len(self._parts)

    def __repr__(self) -> str:
        return f"LegoCollection({len(self._parts)} parts, {len(self._colors)} colors)"


def main() -> None:
    coll = LegoCollection()

    coll.add_part(1, "Brick 2x4", LegoColor.RED)
    coll.add_part(2, "Plate 1x2", LegoColor.BLUE)
    coll.add_part(3, "Tile 2x2", LegoColor.RED)

    print(coll)
    print("По id=2:", coll.find_by_id(2))
    print("Красные:", coll.find_by_color(LegoColor.RED))
    print("Цвета:", coll.all_colors())
    print("id:", coll.all_ids())

    # Enum можно получить из строки, если данные приходят извне (JSON, CLI):
    incoming = "blue"
    color = LegoColor(incoming)
    print("Из строки:", color, "->", color.value)


if __name__ == "__main__":
    main()