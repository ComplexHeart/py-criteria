from __future__ import annotations

from typing import Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum, unique


@dataclass(frozen=True)
class Filter:
    field: str
    operator: str
    value: Any

    @staticmethod
    def eq(field: str, value: Any) -> Filter:
        return Filter(field, '==', value)

    @staticmethod
    def neq(field: str, value: Any) -> Filter:
        return Filter(field, '!=', value)

    @staticmethod
    def gt(field: str, value: Any) -> Filter:
        return Filter(field, '>', value)

    @staticmethod
    def gte(field: str, value: Any) -> Filter:
        return Filter(field, '>=', value)

    @staticmethod
    def lt(field: str, value: Any) -> Filter:
        return Filter(field, '<', value)

    @staticmethod
    def lte(field: str, value: Any) -> Filter:
        return Filter(field, '<=', value)

    @staticmethod
    def contains(field: str, value: Any) -> Filter:
        return Filter(field, 'in', value)

    @staticmethod
    def not_contains(field: str, value: Any) -> Filter:
        return Filter(field, 'not in', value)

    @staticmethod
    def like(field: str, value: Any) -> Filter:
        return Filter(field, 'like', value)

    def __str__(self) -> str:
        return f"{self.field} {self.operator} {self.value}"


@unique
class OrderType(Enum):
    ASC = 'ASC'
    DESC = 'DESC'
    NONE = 'NONE'

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Order:
    by: List[str]
    type: OrderType = OrderType.ASC

    @staticmethod
    def desc(by: List[str]) -> Order:
        return Order(by, OrderType.DESC)

    @staticmethod
    def asc(by: List[str]) -> Order:
        return Order(by, OrderType.ASC)

    @staticmethod
    def none() -> Order:
        return Order([], OrderType.NONE)

    def __str__(self) -> str:
        return f"{', '.join(self.by)} {self.type}"


@dataclass(frozen=True)
class Page:
    limit: int = 25
    offset: int = 0

    def __str__(self) -> str:
        return f"{self.limit}, {self.offset}"


class Criteria:
    def __init__(
            self,
            filters: Optional[List[Filter]] = None,
            order: Optional[Order] = None,
            page: Optional[Page] = None,
    ):
        self.filters = filters or []
        self.order = order or Order.none()
        self.page = page or Page()

    def filter(self, field: str, operator: str, value: Any) -> Criteria:
        self.filters.append(Filter(field, operator, value))
        return self

    def order_by(self, by: List[str], order: Union[OrderType, str] = OrderType.ASC) -> Criteria:
        if not isinstance(order, OrderType):
            order = OrderType(order.upper())

        self.order = Order(by, order)
        return self

    def limit(self, limit: int) -> Criteria:
        self.page = Page(limit, self.page.offset)
        return self

    def offset(self, offset: int) -> Criteria:
        self.page = Page(self.page.limit, offset)
        return self

    def __str__(self) -> str:
        return f"{[str(f) for f in self.filters]} {self.order} {self.page}"
