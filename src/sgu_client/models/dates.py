"""Parsing of date and datetime values from the SGU API."""

import logging
import re
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, BeforeValidator, ValidationInfo

from sgu_client.utils.pandas_helpers import get_pandas

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)

# a date with a timezone but no time, e.g. "1996-04-29Z"
_DATE_ONLY = re.compile(r"^(\d{4}-\d{2}-\d{2})(Z|[+-]\d{2}:\d{2})$")


def _parse_api_datetime(value: Any, info: ValidationInfo) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            match = _DATE_ONLY.match(value)
            parsed = datetime.fromisoformat(
                f"{match[1]}T00:00:00{match[2]}" if match else value
            )
        except (TypeError, ValueError):
            parsed = None
    # never guess a timezone the API didn't give us
    if parsed is None or parsed.tzinfo is None:
        logger.warning(
            "Could not parse %s=%r as a tz-aware datetime; using None",
            info.field_name,
            value,
        )
        return None
    return parsed


# also tags ApiDatetime fields, so convert_datetime_columns can find them
_API_DATETIME_VALIDATOR = BeforeValidator(_parse_api_datetime)

ApiDatetime = Annotated[datetime | None, _API_DATETIME_VALIDATOR]
"""A tz-aware datetime parsed exactly as the API states it (``Z`` means UTC)."""


def convert_datetime_columns(
    df: "pd.DataFrame", model: type[BaseModel]
) -> "pd.DataFrame":
    """Give every `ApiDatetime` column of `model` in `df` a UTC datetime dtype.

    Needed even when the values are already datetimes: an all-null column would
    otherwise stay `object`.
    """
    pd = get_pandas()
    for name, field in model.model_fields.items():
        if _API_DATETIME_VALIDATOR in field.metadata and name in df.columns:
            df[name] = pd.to_datetime(df[name], utc=True)
    return df
