
# Criteria (a.k.a Filter)

[![Test](https://github.com/ComplexHeart/py-criteria/actions/workflows/test.yml/badge.svg)](https://github.com/ComplexHeart/py-criteria/actions/workflows/test.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ComplexHeart_py-criteria&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ComplexHeart_py-criteria)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ComplexHeart_py-criteria&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ComplexHeart_py-criteria)

Small implementation of a filter criteria pattern in Python for Complex Heart SDK. Compose several filters using fluent
interface.

## Installation

Just install the package from PyPI using pip:

```bash
pip install complexheart-criteria
```

or using poetry:

```bash
poetry add complexheart-criteria
```

## Usage

Just import the package and use the `Criteria` class:

```python
from complexheart.domain.criteria import Criteria, Filter, Order, Page

criteria = Criteria(
    [Filter.gte('age', 18), Filter.eq('name', 'Vincent')],
    Order.desc(['name', 'surname']),
    Page(10, 10)
)

# once is instantiated you can use it as a normal object in your repositories.
customers = customer_repository.match(criteria)
```

Alternatively, you can use the fluent interface to build the `Criteria` object:

```python
from complexheart.domain.criteria import Criteria, Filter, Order, Page

criteria = Criteria()
criteria.filter('age', '>=', 18)
criteria.filter('name', '==', 'Vincent')
criteria.order_by(['name', 'surname'], 'DESC')
criteria.limit(10)
criteria.offset(10)

# once is instantiated you can use it as a normal object in your repositories.
customers = customer_repository.match(criteria)
```
