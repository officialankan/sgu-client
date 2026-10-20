"""One SGU collection: how to query it, look up its features and filter them."""

from collections.abc import Sequence
from datetime import datetime as Datetime
from typing import Any, Generic, TypeVar

from sgu_client.client.base import BaseClient
from sgu_client.exceptions import SGUAmbiguousError, SGUNotFoundError
from sgu_client.models.base import SGUResponse

C = TypeVar("C", bound=SGUResponse)

FilterValue = int | str
Where = dict[str, FilterValue | Sequence[FilterValue]]


def _literal(value: FilterValue) -> str:
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return str(value)


def _condition(field: str, value: FilterValue | Sequence[FilterValue]) -> str:
    values = [value] if isinstance(value, int | str) else list(value)
    if len(values) == 1:
        return f"{field}={_literal(values[0])}"
    return f"{field} in ({', '.join(_literal(v) for v in values)})"


class SGUCollection(Generic[C]):
    """Access to one collection (e.g. ``stationer``) of one SGU dataset.

    Args:
        base_client: HTTP client that makes the requests.
        dataset: Dataset path below ``SGUConfig.base_url``,
            e.g. ``"grundvattennivaer-observerade"``.
        name: Collection name within the dataset, e.g. ``"stationer"``.
        model: Collection model that responses are parsed into.
        label: Singular name used in error messages, e.g. ``"Station"``.
        date_field: Field that ``tmin``/``tmax`` filter on, e.g. ``"obsdatum"``.
            Collections without one reject ``tmin``/``tmax``.
    """

    def __init__(
        self,
        base_client: BaseClient,
        *,
        dataset: str,
        name: str,
        model: type[C],
        label: str,
        date_field: str | None = None,
    ):
        self._client = base_client
        self._items = f"collections/{name}/items"
        self._model = model
        self._label = label
        self._plural = f"{label.lower()}s"
        self._name = name
        self._date_field = date_field
        root = base_client.config.base_url.rstrip("/")
        self._dataset_url = f"{root}/{dataset}/ogc/features/v1/"

    def query(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        where: Where | None = None,
        tmin: str | Datetime | None = None,
        tmax: str | Datetime | None = None,
        **kwargs: Any,
    ) -> C:
        """Query the collection and parse the response into its collection model.

        ``where``, ``tmin``/``tmax`` and ``filter_expr`` are combined with ``AND``,
        in that order.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features (paginated automatically)
            filter_expr: CQL filter expression
            sortby: Sort expressions, e.g. ``["+obsdatum"]``
            where: Field conditions, e.g. ``{"platsbeteckning": ["95_2", "101_1"]}``.
                A single value becomes ``field=value``, several become
                ``field in (...)``. String values are quoted and escaped.
            tmin: Earliest value of the collection's date field (inclusive)
            tmax: Latest value of the collection's date field (inclusive)
            **kwargs: Additional query parameters, sent as given

        Raises:
            ValueError: If ``tmin``/``tmax`` is given and the collection has no
                date field.
        """
        params = self._params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            where=where,
            tmin=tmin,
            tmax=tmax,
            **kwargs,
        )
        return self._fetch(self._items, params)

    def get(self, feature_id: str) -> Any:
        """Get one feature by its feature id (e.g. ``"stationer.4086"``).

        Raises:
            SGUNotFoundError: If no feature has that id.
            SGUAmbiguousError: If several features are returned.
        """
        collection = self._fetch(f"{self._items}/{feature_id}", {})
        return self._one(
            collection,
            not_found=f"{self._label} {feature_id} not found",
            ambiguous=f"Multiple {self._plural} returned for ID {feature_id}",
        )

    def find_one(self, **query: Any) -> Any:
        """Query the collection and return its only matching feature.

        Takes the same arguments as :meth:`query`.

        Raises:
            SGUNotFoundError: If nothing matches.
            SGUAmbiguousError: If several features match.
        """
        params = self._params(**query)
        collection = self._fetch(self._items, params)
        filter_text = params.get("filter")
        return self._one(
            collection,
            not_found=f"No {self._plural} found for {filter_text}",
            ambiguous=f"Multiple {self._plural} found for {filter_text}",
        )

    def _params(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        where: Where | None = None,
        tmin: str | Datetime | None = None,
        tmax: str | Datetime | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        conditions = [_condition(f, v) for f, v in (where or {}).items()]
        conditions.extend(self._date_conditions(tmin, tmax))
        if filter_expr:
            conditions.append(filter_expr)
        params: dict[str, Any] = {
            "bbox": ",".join(map(str, bbox)) if isinstance(bbox, list) else bbox,
            "datetime": datetime,
            "limit": limit,
            "filter": " AND ".join(conditions) or None,
            "sortby": ",".join(sortby) if isinstance(sortby, list) else sortby,
            **kwargs,
        }
        return {key: value for key, value in params.items() if value is not None}

    def _date_conditions(
        self, tmin: str | Datetime | None, tmax: str | Datetime | None
    ) -> list[str]:
        bounds = [(">=", tmin), ("<=", tmax)]
        given = [(op, value) for op, value in bounds if value]
        if given and self._date_field is None:
            raise ValueError(f"{self._name} has no date field to filter tmin/tmax on")
        return [
            f"{self._date_field} {op} "
            f"'{value.isoformat() if isinstance(value, Datetime) else value}'"
            for op, value in given
        ]

    def _fetch(self, endpoint: str, params: dict[str, Any]) -> C:
        response = self._client.get(endpoint, params=params, base_url=self._dataset_url)
        return self._model(**response)

    @staticmethod
    def _one(collection: SGUResponse, *, not_found: str, ambiguous: str) -> Any:
        features = collection.features  # ty: ignore[unresolved-attribute]
        if not features:
            raise SGUNotFoundError(not_found)
        if len(features) > 1:
            raise SGUAmbiguousError(ambiguous)
        return features[0]
