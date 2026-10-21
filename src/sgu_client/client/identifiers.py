"""Find stations or sampling sites by any of their identifiers."""

import logging
from collections.abc import Mapping
from typing import Any, Generic, Literal, overload

from sgu_client.client.collection import C, SGUCollection
from sgu_client.exceptions import SGUAmbiguousError, SGUNotFoundError

logger = logging.getLogger(__name__)

IdentifierValue = int | str | list[int] | list[str] | None


class IdentifierLookup(Generic[C]):
    """Finds the features of one collection by the identifiers users know them by.

    Args:
        collection: The collection to look features up in, e.g. stations.
        identifiers: Identifier argument -> (API field, properties attribute),
            e.g. ``{"station_name": ("obsplatsnamn", "station_name")}``.
        key: The identifier other collections refer to these features by,
            e.g. ``"station_id"`` for measurements.
        noun: What one feature is called in messages, e.g. ``"station"``.
    """

    def __init__(
        self,
        collection: SGUCollection[C],
        identifiers: dict[str, tuple[str, str]],
        *,
        key: str,
        noun: str,
    ):
        self._collection = collection
        self._identifiers = identifiers
        self._key = key
        self._noun = noun

    def find_one(self, ids: Mapping[str, IdentifierValue], **query: Any) -> Any:
        """Find the one feature named by exactly one identifier."""
        identifier, values = self._select(ids)
        features = self._find(identifier, values, **query).features
        if len(features) > 1:
            raise SGUAmbiguousError(
                f"Multiple {self._noun}s found for {identifier}: {values[0]!r}"
            )
        return features[0]

    def find_all(self, ids: Mapping[str, IdentifierValue], **query: Any) -> C:
        """Find the features named by exactly one identifier, requiring all of them."""
        identifier, values = self._select(ids)
        return self._find(identifier, values, **query)

    @overload
    def keys(
        self, ids: Mapping[str, IdentifierValue], *, required: Literal[True] = True
    ) -> list[Any]: ...

    @overload
    def keys(
        self, ids: Mapping[str, IdentifierValue], *, required: bool
    ) -> list[Any] | None: ...

    def keys(
        self, ids: Mapping[str, IdentifierValue], *, required: bool = True
    ) -> list[Any] | None:
        """The key values of the features named by exactly one identifier.

        Key values are returned as given. Any other identifier costs a request to
        look the features up, which logs a warning.

        Args:
            ids: Identifier argument -> value, as the caller received them
            required: If False, no identifier is allowed too, and returns None
        """
        if not required and not any(ids.values()):
            return None
        identifier, values = self._select(ids, required=required)
        if identifier == self._key:
            return values
        self._warn_extra_request(identifier)
        return [self._key_of(f) for f in self._find(identifier, values).features]

    def key(self, ids: Mapping[str, IdentifierValue]) -> Any:
        """The key value of the one feature named by exactly one identifier.

        A key value is returned as given. Any other identifier costs a request to
        look the feature up, which logs a warning.
        """
        identifier, values = self._select(ids)
        if identifier == self._key:
            return values[0]
        self._warn_extra_request(identifier)
        return self._key_of(self.find_one(ids))

    def _key_of(self, feature: Any) -> Any:
        _, attribute = self._identifiers[self._key]
        value = getattr(feature.properties, attribute)
        if value is None:
            raise ValueError(
                f"{self._noun.capitalize()} {feature.id} has no {self._key}"
            )
        return value

    def _warn_extra_request(self, identifier: str) -> None:
        logger.warning(
            f"Using '{identifier}' requires an additional API request to look up "
            f"the {self._noun}(s). For better performance, use '{self._key}' "
            "directly if available."
        )

    def _find(self, identifier: str, values: list[Any], **query: Any) -> C:
        """Query the features with these identifier values; raise if any is missing."""
        field, attribute = self._identifiers[identifier]
        collection = self._collection.query(where={field: values}, **query)
        found = {getattr(f.properties, attribute) for f in collection.features}
        missing = [value for value in values if value not in found]
        if missing:
            raise SGUNotFoundError(
                f"No {self._noun}s found for {identifier}: {missing}"
            )
        return collection

    def _select(
        self, ids: Mapping[str, IdentifierValue], *, required: bool = True
    ) -> tuple[str, list[Any]]:
        """The one identifier given (empty values count as not given), as a list."""
        given = [(identifier, value) for identifier, value in ids.items() if value]
        if len(given) != 1:
            raise ValueError(
                f"Exactly one of {self._names()} must be provided."
                if required
                else f"At most one of {self._names()} can be provided."
            )
        ((identifier, value),) = given
        return identifier, value if isinstance(value, list) else [value]

    def _names(self) -> str:
        """The identifier arguments as prose, e.g. ``'a', 'b' or 'c'``."""
        *rest, last = (f"'{identifier}'" for identifier in self._identifiers)
        return f"{', '.join(rest)} or {last}" if rest else last
