"""Find stations or sampling sites by any of their identifiers."""

import logging
from collections.abc import Mapping
from typing import Any, Generic, Literal, overload

from sgu_client.client.collection import C, SGUCollection, only_feature
from sgu_client.exceptions import SGUNotFoundError

logger = logging.getLogger(__name__)

IdentifierValue = int | str | list[int] | list[str] | None


class IdentifierLookup(Generic[C]):
    """Finds the features of one collection by the identifiers users know them by.

    Each method takes ``given``: every identifier argument of the calling method,
    mapped to the value the caller received (``None`` or empty if not given).

    Args:
        collection: The collection to look features up in, e.g. stations.
        identifiers: Identifier argument -> (API field, properties attribute),
            e.g. ``{"station_name": ("obsplatsnamn", "station_name")}``.
        ref: The identifier other collections refer to these features by,
            e.g. ``"station_id"`` for measurements.
        noun: What one feature is called in messages, e.g. ``"station"``.
    """

    def __init__(
        self,
        collection: SGUCollection[C],
        identifiers: dict[str, tuple[str, str]],
        *,
        ref: str,
        noun: str,
    ):
        self._collection = collection
        self._identifiers = identifiers
        self._ref = ref
        self._noun = noun

    def find_one(self, given: Mapping[str, IdentifierValue], **query: Any) -> Any:
        """Find the one feature named by exactly one identifier.

        Raises:
            SGUNotFoundError: If no feature matches.
            SGUAmbiguousError: If several features match.
            ValueError: If not exactly one identifier is given.
        """
        identifier, values = self._select(given)
        return self._find_one(identifier, values[0], **query)

    def find_all(self, given: Mapping[str, IdentifierValue], **query: Any) -> C:
        """Find the features named by exactly one identifier, requiring all of them.

        Raises:
            SGUNotFoundError: If any of the values matches no feature.
            ValueError: If not exactly one identifier is given.
        """
        identifier, values = self._select(given)
        return self._find_all(identifier, values, **query)

    def ref(self, given: Mapping[str, IdentifierValue]) -> Any:
        """The ref value of the one feature named by exactly one identifier.

        A ref value is returned as given. Any other identifier costs a request to
        look the feature up, which logs a warning.

        Raises:
            SGUNotFoundError: If no feature matches.
            SGUAmbiguousError: If several features match.
            ValueError: If not exactly one identifier is given, or if the
                looked-up feature has no ref value.
        """
        identifier, values = self._select(given)
        if identifier == self._ref:
            return values[0]
        self._warn_extra_request(identifier)
        return self._ref_of(self._find_one(identifier, values[0]))

    @overload
    def refs(
        self, given: Mapping[str, IdentifierValue], *, required: Literal[True] = True
    ) -> list[Any]: ...

    @overload
    def refs(
        self, given: Mapping[str, IdentifierValue], *, required: bool
    ) -> list[Any] | None: ...

    def refs(
        self, given: Mapping[str, IdentifierValue], *, required: bool = True
    ) -> list[Any] | None:
        """The ref values of the features named by exactly one identifier.

        Ref values are returned as given. Any other identifier costs a request to
        look the features up, which logs a warning.

        Args:
            given: Identifier argument -> value, as the caller received them
            required: If False, no identifier is allowed too, and returns None

        Raises:
            SGUNotFoundError: If any of the values matches no feature.
            ValueError: If not exactly one identifier is given (at most one if
                not required), or if a looked-up feature has no ref value.
        """
        if not required and not any(given.values()):
            return None
        identifier, values = self._select(given, required=required)
        if identifier == self._ref:
            return values
        self._warn_extra_request(identifier)
        features = self._find_all(identifier, values).features
        return [self._ref_of(feature) for feature in features]

    def _find_one(self, identifier: str, value: Any, **query: Any) -> Any:
        field, _ = self._identifiers[identifier]
        collection = self._collection.query(where={field: value}, **query)
        return only_feature(
            collection,
            not_found=f"No {self._noun}s found for {identifier}: {[value]}",
            ambiguous=f"Multiple {self._noun}s found for {identifier}: {value!r}",
        )

    def _find_all(self, identifier: str, values: list[Any], **query: Any) -> C:
        field, attribute = self._identifiers[identifier]
        collection = self._collection.query(where={field: values}, **query)
        found = {getattr(f.properties, attribute) for f in collection.features}
        missing = [value for value in values if value not in found]
        if missing:
            raise SGUNotFoundError(
                f"No {self._noun}s found for {identifier}: {missing}"
            )
        return collection

    def _ref_of(self, feature: Any) -> Any:
        _, attribute = self._identifiers[self._ref]
        value = getattr(feature.properties, attribute)
        if value is None:
            raise ValueError(
                f"{self._noun.capitalize()} {feature.id} has no {self._ref}"
            )
        return value

    def _warn_extra_request(self, identifier: str) -> None:
        logger.warning(
            f"Using '{identifier}' requires an additional API request to look up "
            f"the {self._noun}(s). For better performance, use '{self._ref}' "
            "directly if available."
        )

    def _select(
        self, given: Mapping[str, IdentifierValue], *, required: bool = True
    ) -> tuple[str, list[Any]]:
        """The one identifier given (empty values count as not given), as a list."""
        provided = [(name, value) for name, value in given.items() if value]
        if len(provided) != 1:
            names = ", ".join(f"'{name}'" for name in self._identifiers)
            names = " or ".join(names.rsplit(", ", 1))
            raise ValueError(
                f"Exactly one of {names} must be provided."
                if required
                else f"At most one of {names} can be provided."
            )
        ((identifier, value),) = provided
        return identifier, value if isinstance(value, list) else [value]
