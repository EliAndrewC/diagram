#!/usr/bin/env python3
"""The cells feature 419's notes quote, by sheet and address, for source-reader and quote-check (a bundle cannot decode
.xls or .xlsx, so the checks read these dumps instead; each line is `<sheet>!<address>=<value>`).

    python3 -I cells.py <boe.xlsx> <clark.xls> > cells_by_address.txt

The Bank of England file: sheet "A47. Wages and prices", columns A, D (the CPI, preferred measure) and BG (the sheet's
Clark consumer price column), every row, and column B's head (rows 1-6, the sheet's title in B1). The Clark file: its "Sources and notes" sheet whole, and on its "main data sheet"
column A (the year) and the eleven columns england.py reads, every row. Written 2026-10-25 from the copies fetched that day.
"""

from __future__ import annotations

import sys

import openpyxl
import xlrd
from openpyxl.utils import get_column_letter

GOODS = ["Wheat", "Barley", "Oats", "Peas", "Salt", "Charcoal", "Firewood", "Oil-lamp", "Woolcloth", "Wage, bldg laborer", "Wage, farm"]


def boe(path: str) -> None:
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["A47. Wages and prices"]
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=830, max_col=59, values_only=True), start=1):
        for c in (1, 2, 4, 59) if i <= 6 else (1, 4, 59):
            v = row[c - 1] if len(row) >= c else None
            if v is not None:
                print(f"A47. Wages and prices!{get_column_letter(c)}{i}={v!r}")


def clark(path: str) -> None:
    book = xlrd.open_workbook(path)
    notes = book.sheet_by_name("Sources and notes")
    for r in range(notes.nrows):
        for c in range(notes.ncols):
            v = notes.cell_value(r, c)
            if v != "":
                print(f"Sources and notes!{get_column_letter(c + 1)}{r + 1}={v!r}")
    main = book.sheet_by_name("main data sheet")
    names = [str(v) for v in main.row_values(5)]
    cols = [0] + [names.index(g) for g in GOODS]
    for r in range(main.nrows):
        for c in cols:
            v = main.cell_value(r, c)
            if v != "":
                print(f"main data sheet!{get_column_letter(c + 1)}{r + 1}={v!r}")


if __name__ == "__main__":
    boe(sys.argv[1])
    clark(sys.argv[2])
