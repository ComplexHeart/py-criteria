from complexheart.domain.criteria import Criteria, Filter, Order, Page


def test_criteria_should_instantiate_successfully():
    c = Criteria(
        [Filter.eq('name', 'Vincent'), Filter.eq('surname', 'Vega')],
        Order.desc(['name', 'surname']),
        Page(10, 10)
    )

    assert isinstance(c, Criteria)
    assert str(c) == "['name == Vincent', 'surname == Vega'] name, surname DESC 10, 10"


def test_criteria_should_instantiate_with_fluent_successfully():
    c = Criteria() \
        .filter('name', '==', 'Vincent') \
        .filter('surname', '==', 'Vega') \
        .order_by(['name', 'surname'], 'DESC') \
        .limit(10) \
        .offset(10)

    assert isinstance(c, Criteria)
    assert str(c) == "['name == Vincent', 'surname == Vega'] name, surname DESC 10, 10"
