# Copyright (c) 2025 Hayato Yamamoto
# SPDX-License-Identifier: MIT
"""Minimal reading of the comma-separated timing data used by pydomino tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

# A timing row has a label, a start time and an end time.
TIMING_ROW_FIELD_COUNT = 3


def split_csv_lines(csv_text: str) -> list[str]:
    """Split CSV text into lines after removing surrounding whitespace.

    Args:
        csv_text: CSV text.

    Returns:
        The lines of the text.

    """
    return csv_text.strip().split("\n")


def read_header_columns(header_line: str) -> list[str]:
    """Return the lower-cased column names of a header line.

    Args:
        header_line: The first line of the CSV text.

    Returns:
        Column names without surrounding whitespace.

    """
    return [
        column_name.strip() for column_name in header_line.lower().strip().split(",")
    ]


def find_column_index(
    header_columns: list[str],
    column_name: str,
    default_index: int,
) -> int:
    """Return the position of ``column_name``, or ``default_index`` if absent.

    Args:
        header_columns: Column names read by ``read_header_columns``.
        column_name: Column to look for.
        default_index: Position used when the column is not found.

    Returns:
        The position of the first column with the given name.

    """
    if column_name in header_columns:
        return header_columns.index(column_name)
    return default_index


def iterate_row_fields(data_lines: list[str]) -> Iterator[list[str]]:
    """Yield the comma-separated fields of each non-empty line.

    Args:
        data_lines: Lines without the header.

    Yields:
        Fields of one line. Fields are not stripped.

    """
    for line in data_lines:
        stripped_line = line.strip()
        if stripped_line:
            yield stripped_line.split(",")
