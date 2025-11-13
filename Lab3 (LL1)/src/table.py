import csv
from dataclasses import dataclass


@dataclass
class Line:
    number: int
    symbol: str
    first_set: list[str]
    shift: bool
    error: bool
    pointer: int | None
    stack: bool
    end: bool


def write_table(table: list[Line]) -> None:
    with open("table.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for line in table:
            writer.writerow([line.number, line.symbol, " ".join(sorted(line.first_set)), "+" if line.shift else "-",
                "+" if line.error else "-", line.pointer, "+" if line.stack else "-", "+" if line.end else "-"])


def read_table() -> list[Line]:
    with open("table.csv", "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        table = []
        for row in reader:
            pointer_str = row[5].strip()
            pointer = int(pointer_str) if pointer_str else None

            table.append(
                Line(number=int(row[0]), symbol=row[1], first_set=row[2].split() if row[2] else [], shift=row[3] == "+",
                    error=row[4] == "+", pointer=pointer, stack=row[6] == "+", end=row[7] == "+"))
        return table
