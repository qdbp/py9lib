from typing import Any, Dict


def mk_column_spec(d: Dict[str, Any]) -> str:
    """
    Generates a SQL INSERT columns and VALUES string.

    Maps every key to a column by the same name.

    Args:
        d: the dictionary to map
    """

    keys = list(d.keys())

    return f"""
    ( {",".join(keys)} )
    VALUES ( {",".join(f":{key}" for key in keys)} )
    """
