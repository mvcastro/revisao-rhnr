from typing import Any, Sequence
import pandas as pd

def highlight_rows_by_category(
    row: pd.Series, column: str, match_values: Sequence[Any], colors: Sequence[str]
) -> list[str]:
    if len(match_values) != len(colors):
        raise ValueError("match_values and colors must have the same length")

    for match_value, color in zip(match_values, colors):
        if row[column] == match_value:
            return [f"background-color: {color}"] * len(row)

    return [""] * len(row)  # No styling for other categories