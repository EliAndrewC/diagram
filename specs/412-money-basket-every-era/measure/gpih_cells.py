"""Every non-empty cell of a GPIH spreadsheet, by sheet and address, for the checks of feature 412 session 2.

A bundle cannot decode .xls or .xlsx, so source-reader and quote-check read these dumps instead; each line is
`<address>=<value>`, and in an .xlsx a cell with a yellow fill (Kumon's mark of an IMPUTED figure, "yellow highlight
indicates years where there are no underlying data and it is imputed", sheet "Sources & Notes" row 9) ends with
` [yellow]`. A formula cell shows its formula.

  python3 -I specs/412-money-basket-every-era/measure/gpih_cells.py <file> [maxcol=<N>] [sheet ...] > <dump>

(maxcol=13 keeps columns A-M only: Kumon's "Japan" sheet, year to cloth, without its basket formulas.)

Dumps written 2026-10-24 from the copies downloaded that day: kumon_cells_by_address.txt (Japanese Wages.xlsx,
sheets "Sources & Notes" and "Japan"), kimura_cells_by_address.txt (Osaka_1600-1650.xls, every sheet) and
iwahashi_cells_by_address.txt (Japan_rice_P_1620-1867.xls, sheets "Sources and notes" and "koku of rice").
"""

from __future__ import annotations

import sys

import openpyxl
import xlrd
from openpyxl.utils import get_column_letter


def dump_xls(path, sheets):
    book = xlrd.open_workbook(path)
    for sh in book.sheets():
        if sheets and sh.name not in sheets:
            continue
        print(f"=== sheet {sh.name!r}")
        for r in range(sh.nrows):
            cells = [f"{get_column_letter(c + 1)}{r + 1}={v!r}" for c, v in enumerate(sh.row_values(r)) if v != ""]
            if cells:
                print(" | ".join(cells))


def dump_xlsx(path, sheets):
    book = openpyxl.load_workbook(path)
    for ws in book.worksheets:
        if sheets and ws.title not in sheets:
            continue
        print(f"=== sheet {ws.title!r}")
        for row in ws.iter_rows():
            cells = []
            for c in row:
                if c.value is None or c.column > MAXCOL:
                    continue
                fill = c.fill.fgColor.rgb if c.fill and c.fill.fill_type else None
                yellow = isinstance(fill, str) and fill.upper().endswith("FFFF00")
                cells.append(f"{c.coordinate}={c.value!r}" + (" [yellow]" if yellow else ""))
            if cells:
                print(" | ".join(cells))


MAXCOL = 10**6

if __name__ == "__main__":
    path, rest = sys.argv[1], sys.argv[2:]
    for a in [a for a in rest if a.startswith("maxcol=")]:
        MAXCOL = int(a.split("=")[1])
        rest.remove(a)
    sheets = set(rest)
    (dump_xlsx if path.endswith(".xlsx") else dump_xls)(path, sheets)
