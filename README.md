
# Criteria (a.k.a Filter)

[![Test](https://github.com/ComplexHeart/py-criteria/actions/workflows/test.yml/badge.svg)](https://github.com/ComplexHeart/py-criteria/actions/workflows/test.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ComplexHeart_py-criteria&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ComplexHeart_py-criteria)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ComplexHeart_py-criteria&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ComplexHeart_py-criteria)

Small implementation of a filter criteria pattern in Python for Complex Heart SDK. Query-system agnostic - works with SQL, NoSQL, APIs, or any data source.

## Installation

```bash
pip install complex-heart-criteria
```

or using uv:

```bash
uv add complex-heart-criteria
```

## Usage

```python
from complexheart.domain.criteria import Criteria, Filter, FilterGroup, Order, Page
```

### Building FilterGroups

Use `+` to compose filters into a FilterGroup (AND logic within group):

```python
active_adults = Filter.equal("status", "active") + Filter.greater_or_equal_than("age", 18)
```

Or use the fluent API:

```python
active_adults = (
    FilterGroup.empty()
    .add_filter_equal("status", "active")
    .add_filter_greater_or_equal_than("age", 18)
)
```

### Building Criteria

Add FilterGroups to Criteria (OR logic between groups):

```python
c = (
    Criteria()
    .with_filter_group(active_adults)
    .with_order(Order.desc(("created_at",)))
    .with_page_limit(10)
    .with_page_offset(20)
)
```

### Merging Criteria

Use `|` for OR and `&` for AND between Criteria objects:

```python
active_users = Criteria().with_filter_group(
    Filter.equal("status", "active") + Filter.greater_than("age", 18)
)
admin_users = Criteria().with_filter_group(
    FilterGroup.create(Filter.equal("role", "admin"))
)

# OR: concatenate groups
combined = active_users | admin_users
# Result: (status = 'active' AND age > 18) OR (role = 'admin')

# AND: merge into single group
merged = active_users & admin_users
# Result: (status = 'active' AND age > 18 AND role = 'admin')
```

### Fluent API

```python
criteria = (
    Criteria()
    .filter("status", "==", "active", group=0)
    .filter("age", ">=", 18, group=0)
    .filter("role", "==", "admin", group=1)
    .order_by(("created_at",), "DESC")
    .limit(10)
    .offset(20)
)
# Result: (status = 'active' AND age >= 18) OR (role = 'admin')
```

### Filter Factories

```python
Filter.equal("name", "Vincent")              # name == 'Vincent'
Filter.not_equal("name", "Vincent")          # name != 'Vincent'
Filter.greater_than("age", 18)               # age > 18
Filter.greater_or_equal_than("age", 18)      # age >= 18
Filter.less_than("age", 65)                  # age < 65
Filter.less_or_equal_than("age", 65)         # age <= 65
Filter.in_("status", ["a", "b"])             # status IN ('a', 'b')
Filter.not_in("status", ["x"])               # status NOT IN ('x')
Filter.like("name", "Vin%")                  # name LIKE 'Vin%'
Filter.not_like("name", "Vin%")              # name NOT LIKE 'Vin%'
Filter.contains("tags", "vip")               # tags contains 'vip'
Filter.not_contains("tags", "x")             # tags not contains 'x'
```

### FilterGroup Methods

```python
group = (
    FilterGroup.empty()
    .add_filter_equal("status", "active")
    .add_filter_greater_than("age", 18)
    .add_filter_in("role", ["admin", "moderator"])
)
```

Available methods: `add_filter_equal`, `add_filter_not_equal`, `add_filter_greater_than`,
`add_filter_greater_or_equal_than`, `add_filter_less_than`, `add_filter_less_or_equal_than`,
`add_filter_in`, `add_filter_not_in`, `add_filter_like`, `add_filter_not_like`,
`add_filter_contains`, `add_filter_not_contains`.

### Repository Integration

```python
customers = customer_repository.match(criteria)
```

## Immutability

All classes are immutable frozen dataclasses. Methods return new instances:

```python
c1 = Criteria()
c2 = c1.filter("name", "==", "Vincent")

assert c1 is not c2
assert len(c1.filters) == 0
assert len(c2.filters) == 1
```

## Migration from v0.x

v1.0 introduces breaking changes:

### Immutability

```python
# Old (v0.x) - mutation pattern
c = Criteria()
c.filter("name", "==", "Vincent")  # mutated c

# New (v1.x) - immutable, must reassign
c = Criteria()
c = c.filter("name", "==", "Vincent")  # returns new instance
```

### Filter Factory Names

```python
# Old
Filter.eq("name", "v")
Filter.neq("name", "v")
Filter.gt("age", 18)
Filter.gte("age", 18)
Filter.lt("age", 65)
Filter.lte("age", 65)

# New (aligned with PHP version)
Filter.equal("name", "v")
Filter.not_equal("name", "v")
Filter.greater_than("age", 18)
Filter.greater_or_equal_than("age", 18)
Filter.less_than("age", 65)
Filter.less_or_equal_than("age", 65)
```

### Order.by is now tuple

```python
# Old
Order.desc(["name", "age"])

# New
Order.desc(("name", "age"))
```

### Criteria operators only accept Criteria

```python
# Old - operators accepted Filter/FilterGroup
c = Criteria() | Filter.equal("a", 1)

# New - use with_filter_group instead
c = Criteria().with_filter_group(FilterGroup.create(Filter.equal("a", 1)))

# Operators only work between Criteria objects
c1 = Criteria().with_filter_group(group1)
c2 = Criteria().with_filter_group(group2)
combined = c1 | c2  # OK
merged = c1 & c2    # OK
```
