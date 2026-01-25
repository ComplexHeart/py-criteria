from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any, overload


@unique
class Operator(Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "in"
    NOT_IN = "not in"
    LIKE = "like"
    NOT_LIKE = "not like"
    CONTAINS = "contains"
    NOT_CONTAINS = "not contains"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Filter:
    field: str
    operator: Operator
    value: Any

    def __post_init__(self) -> None:
        if not self.field or not self.field.strip():
            raise ValueError("Filter field cannot be empty")
        if isinstance(self.operator, str):
            object.__setattr__(self, "operator", _str_to_operator(self.operator))

    def __add__(self, other: Filter | FilterGroup) -> FilterGroup:
        if isinstance(other, Filter):
            return FilterGroup((self, other))
        if isinstance(other, FilterGroup):
            return FilterGroup((self, *other._filters))
        raise TypeError(f"unsupported operand type(s) for +: 'Filter' and '{type(other).__name__}'")

    def __hash__(self) -> int:
        try:
            return hash((self.field, self.operator, self.value))
        except TypeError:
            return hash((self.field, self.operator, str(self.value)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Filter):
            return NotImplemented
        return self.field == other.field and self.operator == other.operator and self.value == other.value

    def __repr__(self) -> str:
        return f"Filter({self.field!r}, {self.operator.name}, {self.value!r})"

    @staticmethod
    def equal(field: str, value: Any) -> Filter:
        return Filter(field, Operator.EQUAL, value)

    @staticmethod
    def not_equal(field: str, value: Any) -> Filter:
        return Filter(field, Operator.NOT_EQUAL, value)

    @staticmethod
    def greater_than(field: str, value: Any) -> Filter:
        return Filter(field, Operator.GT, value)

    @staticmethod
    def greater_or_equal_than(field: str, value: Any) -> Filter:
        return Filter(field, Operator.GTE, value)

    @staticmethod
    def less_than(field: str, value: Any) -> Filter:
        return Filter(field, Operator.LT, value)

    @staticmethod
    def less_or_equal_than(field: str, value: Any) -> Filter:
        return Filter(field, Operator.LTE, value)

    @staticmethod
    def in_(field: str, value: Sequence[Any]) -> Filter:
        return Filter(field, Operator.IN, value)

    @staticmethod
    def not_in(field: str, value: Sequence[Any]) -> Filter:
        return Filter(field, Operator.NOT_IN, value)

    @staticmethod
    def contains(field: str, value: Any) -> Filter:
        return Filter(field, Operator.CONTAINS, value)

    @staticmethod
    def not_contains(field: str, value: Any) -> Filter:
        return Filter(field, Operator.NOT_CONTAINS, value)

    @staticmethod
    def like(field: str, value: Any) -> Filter:
        return Filter(field, Operator.LIKE, value)

    @staticmethod
    def not_like(field: str, value: Any) -> Filter:
        return Filter(field, Operator.NOT_LIKE, value)

    def __str__(self) -> str:
        return f"{self.field} {self.operator} {self.value}"


def _str_to_operator(op: str) -> Operator:
    mapping = {
        "==": Operator.EQUAL,
        "=": Operator.EQUAL,
        "!=": Operator.NOT_EQUAL,
        "<>": Operator.NOT_EQUAL,
        ">": Operator.GT,
        ">=": Operator.GTE,
        "<": Operator.LT,
        "<=": Operator.LTE,
        "in": Operator.IN,
        "not in": Operator.NOT_IN,
        "like": Operator.LIKE,
        "not like": Operator.NOT_LIKE,
        "contains": Operator.CONTAINS,
        "not contains": Operator.NOT_CONTAINS,
    }
    normalized = op.lower().strip()
    if normalized in mapping:
        return mapping[normalized]
    if op in mapping:
        return mapping[op]
    raise ValueError(f"Unknown operator: {op}")


@dataclass(frozen=True)
class FilterGroup:
    _filters: tuple[Filter, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        return len(self._filters)

    def __iter__(self) -> Iterator[Filter]:
        return iter(self._filters)

    def __contains__(self, item: object) -> bool:
        return item in self._filters

    @overload
    def __getitem__(self, index: int) -> Filter: ...

    @overload
    def __getitem__(self, index: slice) -> FilterGroup: ...

    def __getitem__(self, index: int | slice) -> Filter | FilterGroup:
        if isinstance(index, slice):
            return FilterGroup(self._filters[index])
        return self._filters[index]

    def __bool__(self) -> bool:
        return len(self._filters) > 0

    def __add__(self, other: Filter | FilterGroup) -> FilterGroup:
        if isinstance(other, Filter):
            return FilterGroup((*self._filters, other))
        if isinstance(other, FilterGroup):
            return FilterGroup(self._filters + other._filters)
        raise TypeError(f"unsupported operand type(s) for +: 'FilterGroup' and '{type(other).__name__}'")

    def __radd__(self, other: Filter) -> FilterGroup:
        if isinstance(other, Filter):
            return FilterGroup((other, *self._filters))
        raise TypeError(f"unsupported operand type(s) for +: '{type(other).__name__}' and 'FilterGroup'")

    def __hash__(self) -> int:
        return hash(self._filters)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FilterGroup):
            return NotImplemented
        return self._filters == other._filters

    def __repr__(self) -> str:
        if not self._filters:
            return "FilterGroup()"
        filters = ", ".join(repr(f) for f in self._filters)
        return f"FilterGroup({filters})"

    @staticmethod
    def create(*filters: Filter) -> FilterGroup:
        return FilterGroup(filters)

    @staticmethod
    def from_list(filters: list[Filter]) -> FilterGroup:
        return FilterGroup(tuple(filters))

    @staticmethod
    def empty() -> FilterGroup:
        return FilterGroup()

    def add_filter(self, f: Filter) -> FilterGroup:
        return FilterGroup((*self._filters, f))

    def add_filter_equal(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.equal(field, value))

    def add_filter_not_equal(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.not_equal(field, value))

    def add_filter_greater_than(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.greater_than(field, value))

    def add_filter_greater_or_equal_than(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.greater_or_equal_than(field, value))

    def add_filter_less_than(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.less_than(field, value))

    def add_filter_less_or_equal_than(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.less_or_equal_than(field, value))

    def add_filter_in(self, field: str, value: Sequence[Any]) -> FilterGroup:
        return self.add_filter(Filter.in_(field, value))

    def add_filter_not_in(self, field: str, value: Sequence[Any]) -> FilterGroup:
        return self.add_filter(Filter.not_in(field, value))

    def add_filter_like(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.like(field, value))

    def add_filter_not_like(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.not_like(field, value))

    def add_filter_contains(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.contains(field, value))

    def add_filter_not_contains(self, field: str, value: Any) -> FilterGroup:
        return self.add_filter(Filter.not_contains(field, value))

    def __str__(self) -> str:
        if not self._filters:
            return "()"
        return "(" + " AND ".join(str(f) for f in self._filters) + ")"


@unique
class OrderType(Enum):
    ASC = "ASC"
    DESC = "DESC"
    NONE = "NONE"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Order:
    by: tuple[str, ...] = field(default_factory=tuple)
    type: OrderType = OrderType.ASC

    def __hash__(self) -> int:
        return hash((self.by, self.type))

    @staticmethod
    def desc(by: tuple[str, ...]) -> Order:
        return Order(by, OrderType.DESC)

    @staticmethod
    def asc(by: tuple[str, ...]) -> Order:
        return Order(by, OrderType.ASC)

    @staticmethod
    def none() -> Order:
        return Order((), OrderType.NONE)

    def __str__(self) -> str:
        if not self.by:
            return ""
        return f"{', '.join(self.by)} {self.type}"


@dataclass(frozen=True)
class Page:
    limit: int = 25
    offset: int = 0

    def __post_init__(self) -> None:
        if self.limit < 0:
            raise ValueError(f"limit must be >= 0, got {self.limit}")
        if self.offset < 0:
            raise ValueError(f"offset must be >= 0, got {self.offset}")

    def __str__(self) -> str:
        return f"{self.limit}, {self.offset}"


@dataclass(frozen=True)
class Criteria:
    _groups: tuple[FilterGroup, ...] = field(default_factory=tuple)
    order: Order = field(default_factory=Order.none)
    page: Page = field(default_factory=Page)

    def __or__(self, other: Criteria) -> Criteria:
        if not isinstance(other, Criteria):
            raise TypeError(
                f"unsupported operand type(s) for |: 'Criteria' and '{type(other).__name__}'. "
                "Use Criteria().with_filter_group() to add filters."
            )
        return Criteria(self._groups + other._groups, self.order, self.page)

    def __and__(self, other: Criteria) -> Criteria:
        if not isinstance(other, Criteria):
            raise TypeError(
                f"unsupported operand type(s) for &: 'Criteria' and '{type(other).__name__}'. "
                "Use Criteria().with_filter_group() to add filters."
            )
        all_filters: list[Filter] = []
        for group in self._groups:
            all_filters.extend(group._filters)
        for group in other._groups:
            all_filters.extend(group._filters)
        if not all_filters:
            return Criteria((), self.order, self.page)
        return Criteria((FilterGroup(tuple(all_filters)),), self.order, self.page)

    def __hash__(self) -> int:
        return hash((self._groups, self.order, self.page))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Criteria):
            return NotImplemented
        return self._groups == other._groups and self.order == other.order and self.page == other.page

    def __repr__(self) -> str:
        parts = [f"groups={len(self._groups)}"]
        if self.has_filters():
            parts.append(f"filters={len(self.filters)}")
        if self.has_order():
            parts.append(f"order={self.order.by}")
        if self.page != Page():
            parts.append(f"page=({self.page.limit}, {self.page.offset})")
        return f"Criteria({', '.join(parts)})"

    def with_filter_group(self, group: FilterGroup) -> Criteria:
        return Criteria((*self._groups, group), self.order, self.page)

    def with_order(self, order: Order) -> Criteria:
        return Criteria(self._groups, order, self.page)

    def with_page(self, page: Page) -> Criteria:
        return Criteria(self._groups, self.order, page)

    def with_page_limit(self, limit: int) -> Criteria:
        return Criteria(self._groups, self.order, Page(limit, self.page.offset))

    def with_page_offset(self, offset: int) -> Criteria:
        return Criteria(self._groups, self.order, Page(self.page.limit, offset))

    def filter(self, field: str, operator: str, value: Any, group: int = 0) -> Criteria:
        new_filter = Filter(field, _str_to_operator(operator), value)

        groups_list = list(self._groups)
        while len(groups_list) <= group:
            groups_list.append(FilterGroup())

        target_group = groups_list[group]
        groups_list[group] = FilterGroup((*target_group._filters, new_filter))

        return Criteria(tuple(groups_list), self.order, self.page)

    def order_by(self, by: tuple[str, ...], order: OrderType | str = OrderType.ASC) -> Criteria:
        if not isinstance(order, OrderType):
            order = OrderType(order.upper())
        return Criteria(self._groups, Order(by, order), self.page)

    def limit(self, limit: int) -> Criteria:
        return self.with_page_limit(limit)

    def offset(self, offset: int) -> Criteria:
        return self.with_page_offset(offset)

    @property
    def filters(self) -> list[Filter]:
        result: list[Filter] = []
        for group in self._groups:
            result.extend(group._filters)
        return result

    @property
    def groups(self) -> tuple[FilterGroup, ...]:
        return self._groups

    def has_filters(self) -> bool:
        return any(len(g) > 0 for g in self._groups)

    def has_order(self) -> bool:
        return self.order.type != OrderType.NONE and len(self.order.by) > 0

    def __str__(self) -> str:
        parts = []

        if self.has_filters():
            group_strs = [str(g) for g in self._groups if g]
            parts.append("WHERE " + " OR ".join(group_strs))

        if self.has_order():
            parts.append(f"ORDER BY {self.order}")

        if self.page != Page():
            parts.append(f"LIMIT {self.page.limit} OFFSET {self.page.offset}")

        return " ".join(parts)
