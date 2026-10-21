"""GeoJSON features and feature collections, and their conversion to pandas."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, TypeVar, get_args

from pydantic import Field, field_validator

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.dates import ApiDatetime, convert_datetime_columns
from sgu_client.models.shared import CRS, Geometry, Link, MultiPolygon, Point
from sgu_client.utils.pandas_helpers import get_pandas, optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd

P = TypeVar("P", bound=SGUBaseModel)


class Feature(SGUBaseModel, Generic[P]):
    """One feature of a collection (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Feature id, e.g. ``stationer.4086``")
    geometry: Geometry | None = Field(None, description="Feature geometry")
    properties: P = Field(..., description="Feature properties")


F = TypeVar("F", bound=Feature)

LonLat = tuple[float, float] | tuple[None, None]


def _point(geometry: Geometry | None) -> LonLat:
    if isinstance(geometry, Point):
        return geometry.coordinates[0], geometry.coordinates[1]
    return None, None


def _centroid(geometry: Geometry | None) -> LonLat:
    # SGU's areas are grid cells: one ring of four corners, so the mean of the
    # corners is the cell's centre. GeoJSON closes a ring by repeating its first
    # corner, which must not count twice.
    if isinstance(geometry, MultiPolygon) and geometry.coordinates:
        ring = geometry.coordinates[0][0] if geometry.coordinates[0] else []
        corners = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
        if corners:
            lons = [point[0] for point in corners]
            lats = [point[1] for point in corners]
            return sum(lons) / len(lons), sum(lats) / len(lats)
    return None, None


GeometryColumns = Literal["point", "centroid"]

_GEOMETRY_COLUMNS: dict[str, tuple[tuple[str, str], Callable[..., LonLat]]] = {
    "point": (("longitude", "latitude"), _point),
    "centroid": (("centroid_longitude", "centroid_latitude"), _centroid),
}


class FeatureCollection(SGUResponse, Generic[F]):
    """A collection of features (GeoJSON FeatureCollection).

    ``to_dataframe()`` gives one row per feature: ``feature_id`` first, then the
    collection's geometry columns (if any), then every property under its English
    name.
    """

    # which geometry columns the DataFrame has: "point" for longitude/latitude,
    # "centroid" for centroid_longitude/centroid_latitude, None for none
    _geometry: ClassVar[GeometryColumns | None] = None

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[F] = Field(default_factory=list, description="Features")

    # OGC API Features metadata
    totalFeatures: int | None = Field(None, description="Total number of features")
    numberMatched: int | None = Field(
        None, description="Number of features matching query"
    )
    numberReturned: int | None = Field(None, description="Number of features returned")
    timeStamp: ApiDatetime = Field(None, description="Response timestamp (UTC)")

    # Links and CRS
    links: list[Link] | None = Field(None, description="Related links")
    crs: CRS | None = Field(None, description="Coordinate reference system")

    @field_validator("totalFeatures", mode="before")
    @classmethod
    def _unknown_total_features(cls, value: Any) -> Any:
        return None if value == "unknown" else value

    @classmethod
    def _properties_model(cls) -> type[SGUBaseModel]:
        (feature,) = get_args(cls.model_fields["features"].annotation)
        return feature.model_fields["properties"].annotation

    @classmethod
    def _columns(cls) -> list[str]:
        geometry = _GEOMETRY_COLUMNS[cls._geometry][0] if cls._geometry else ()
        return ["feature_id", *geometry, *cls._properties_model().model_fields]

    def _row(self, feature: F) -> dict[str, Any]:
        row: dict[str, Any] = {"feature_id": feature.id}
        if self._geometry:
            names, values = _GEOMETRY_COLUMNS[self._geometry]
            row.update(zip(names, values(feature.geometry), strict=True))
        row.update(feature.properties.model_dump())
        return row

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self) -> "pd.DataFrame":
        """Convert to a pandas DataFrame with one row per feature.

        The index is each row's position in the API response.

        Returns:
            DataFrame with ``feature_id``, the geometry columns and the properties.
        """
        pd = get_pandas()
        rows = [self._row(feature) for feature in self.features]
        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=self._columns())
        return convert_datetime_columns(df, self._properties_model())


class TimeSeriesCollection(FeatureCollection[F], Generic[F]):
    """A feature collection with a date per feature.

    Adds sorting by date to ``to_dataframe()``, and ``to_series()``.
    """

    # the date column to sort by and index series on, and the default values column
    _date_column: ClassVar[str]
    _series_column: ClassVar[str]

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self, sort_by_date: bool = True) -> "pd.DataFrame":
        """Convert to a pandas DataFrame with one row per feature.

        Args:
            sort_by_date: Sort the rows by date. Either way the index is each
                row's position in the API response, so pass ``False`` (or call
                ``sort_index()``) to get the rows in API order.

        Returns:
            DataFrame with ``feature_id``, the geometry columns and the properties.
        """
        df = super().to_dataframe()
        if sort_by_date and not df.empty:
            df = df.sort_values(by=self._date_column, kind="stable")
        return df

    @optional_pandas_method("to_series() method")
    def to_series(
        self,
        index: str | None = None,
        data: str | None = None,
        sort_by_date: bool = True,
    ) -> "pd.Series":
        """Convert to a pandas Series, by default the collection's main value by date.

        Args:
            index: Column to use as index. Defaults to the collection's date column.
            data: Column to use as values. Defaults to the collection's main value.
            sort_by_date: Sort by date before creating the Series. Pass ``False``
                to keep the API response order.

        Returns:
            Series named after the ``data`` column.

        Raises:
            ValueError: If ``index`` or ``data`` is not a column.
        """
        df = self.to_dataframe(sort_by_date=sort_by_date)
        pd = get_pandas()

        index = index or self._date_column
        data = data or self._series_column

        if df.empty:
            return pd.Series(dtype=float)

        if index not in df.columns:
            raise ValueError(f"Index column '{index}' not found in DataFrame.")
        if data not in df.columns:
            raise ValueError(f"Data column '{data}' not found in DataFrame.")

        series = pd.Series(data=df[data].values, index=df[index])
        series.name = data
        return series
