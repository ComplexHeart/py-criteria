import pytest

from complexheart.domain.criteria import (
    Criteria,
    Filter,
    FilterGroup,
    Operator,
    Order,
    OrderType,
    Page,
)


def test_operator_values():
    assert str(Operator.EQUAL) == "=="
    assert str(Operator.NOT_EQUAL) == "!="
    assert str(Operator.GT) == ">"
    assert str(Operator.GTE) == ">="
    assert str(Operator.LT) == "<"
    assert str(Operator.LTE) == "<="
    assert str(Operator.IN) == "in"
    assert str(Operator.NOT_IN) == "not in"
    assert str(Operator.LIKE) == "like"
    assert str(Operator.NOT_LIKE) == "not like"
    assert str(Operator.CONTAINS) == "contains"
    assert str(Operator.NOT_CONTAINS) == "not contains"


def test_filter_creation_with_operator_enum():
    f = Filter("name", Operator.EQUAL, "Vincent")
    assert f.field == "name"
    assert f.operator == Operator.EQUAL
    assert f.value == "Vincent"


def test_filter_creation_with_string_operator():
    f = Filter("name", "==", "Vincent")
    assert f.operator == Operator.EQUAL


def test_filter_string_operator_conversion():
    assert Filter("f", "=", "v").operator == Operator.EQUAL
    assert Filter("f", "==", "v").operator == Operator.EQUAL
    assert Filter("f", "!=", "v").operator == Operator.NOT_EQUAL
    assert Filter("f", "<>", "v").operator == Operator.NOT_EQUAL
    assert Filter("f", ">", "v").operator == Operator.GT
    assert Filter("f", ">=", "v").operator == Operator.GTE
    assert Filter("f", "<", "v").operator == Operator.LT
    assert Filter("f", "<=", "v").operator == Operator.LTE
    assert Filter("f", "in", "v").operator == Operator.IN
    assert Filter("f", "not in", "v").operator == Operator.NOT_IN
    assert Filter("f", "like", "v").operator == Operator.LIKE
    assert Filter("f", "not like", "v").operator == Operator.NOT_LIKE


def test_filter_factory_methods():
    assert Filter.equal("f", "v") == Filter("f", Operator.EQUAL, "v")
    assert Filter.not_equal("f", "v") == Filter("f", Operator.NOT_EQUAL, "v")
    assert Filter.greater_than("f", 1) == Filter("f", Operator.GT, 1)
    assert Filter.greater_or_equal_than("f", 1) == Filter("f", Operator.GTE, 1)
    assert Filter.less_than("f", 1) == Filter("f", Operator.LT, 1)
    assert Filter.less_or_equal_than("f", 1) == Filter("f", Operator.LTE, 1)
    assert Filter.in_("f", [1, 2]) == Filter("f", Operator.IN, [1, 2])
    assert Filter.not_in("f", [1, 2]) == Filter("f", Operator.NOT_IN, [1, 2])
    assert Filter.like("f", "%v%") == Filter("f", Operator.LIKE, "%v%")
    assert Filter.not_like("f", "%v%") == Filter("f", Operator.NOT_LIKE, "%v%")
    assert Filter.contains("f", "v") == Filter("f", Operator.CONTAINS, "v")
    assert Filter.not_contains("f", "v") == Filter("f", Operator.NOT_CONTAINS, "v")


def test_filter_equality():
    f1 = Filter.equal("name", "Vincent")
    f2 = Filter.equal("name", "Vincent")
    f3 = Filter.equal("name", "Jules")

    assert f1 == f2
    assert f1 != f3


def test_filter_hash():
    f1 = Filter.equal("name", "Vincent")
    f2 = Filter.equal("name", "Vincent")

    assert hash(f1) == hash(f2)
    s = {f1, f2}
    assert len(s) == 1


def test_filter_hash_with_unhashable_value():
    f = Filter.in_("status", ["active", "pending"])
    h = hash(f)
    assert isinstance(h, int)


def test_filter_add_creates_filter_group():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)

    result = f1 + f2

    assert isinstance(result, FilterGroup)
    assert len(result) == 2
    assert f1 in result
    assert f2 in result


def test_filter_str():
    f = Filter.equal("name", "Vincent")
    assert str(f) == "name == Vincent"


def test_filter_group_creation_empty():
    g = FilterGroup()
    assert len(g) == 0
    assert not g


def test_filter_group_creation_with_filters():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup((f1, f2))

    assert len(g) == 2
    assert g


def test_filter_group_create_factory():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup.create(f1, f2)

    assert len(g) == 2
    assert f1 in g
    assert f2 in g


def test_filter_group_from_list_factory():
    filters = [Filter.equal("a", 1), Filter.equal("b", 2)]
    g = FilterGroup.from_list(filters)

    assert len(g) == 2


def test_filter_group_empty_factory():
    g = FilterGroup.empty()
    assert len(g) == 0


def test_filter_group_iteration():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup.create(f1, f2)

    result = list(g)
    assert result == [f1, f2]


def test_filter_group_contains():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    f3 = Filter.equal("c", 3)
    g = FilterGroup.create(f1, f2)

    assert f1 in g
    assert f2 in g
    assert f3 not in g


def test_filter_group_getitem_index():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup.create(f1, f2)

    assert g[0] == f1
    assert g[1] == f2


def test_filter_group_getitem_slice():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    f3 = Filter.equal("c", 3)
    g = FilterGroup.create(f1, f2, f3)

    sliced = g[0:2]

    assert isinstance(sliced, FilterGroup)
    assert len(sliced) == 2
    assert f1 in sliced
    assert f2 in sliced
    assert f3 not in sliced


def test_filter_group_add_filter_with_operator():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup.create(f1)

    result = g + f2

    assert isinstance(result, FilterGroup)
    assert len(result) == 2
    assert f1 in result
    assert f2 in result


def test_filter_group_add_filter_group():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g1 = FilterGroup.create(f1)
    g2 = FilterGroup.create(f2)

    result = g1 + g2

    assert isinstance(result, FilterGroup)
    assert len(result) == 2


def test_filter_group_radd_filter():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup.create(f2)

    result = f1 + g

    assert isinstance(result, FilterGroup)
    assert len(result) == 2
    assert result[0] == f1


def test_filter_group_chained_addition():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    f3 = Filter.equal("c", 3)

    result = f1 + f2 + f3

    assert isinstance(result, FilterGroup)
    assert len(result) == 3


def test_filter_group_equality():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g1 = FilterGroup.create(f1, f2)
    g2 = FilterGroup.create(f1, f2)
    g3 = FilterGroup.create(f2, f1)

    assert g1 == g2
    assert g1 != g3


def test_filter_group_str():
    f1 = Filter.equal("a", 1)
    f2 = Filter.equal("b", 2)
    g = FilterGroup.create(f1, f2)

    assert str(g) == "(a == 1 AND b == 2)"


def test_filter_group_str_empty():
    g = FilterGroup()
    assert str(g) == "()"


def test_filter_group_add_filter_method():
    g = FilterGroup.empty()
    f = Filter.equal("a", 1)

    result = g.add_filter(f)

    assert len(result) == 1
    assert f in result


def test_filter_group_add_filter_equal():
    g = FilterGroup.empty().add_filter_equal("name", "Vincent")

    assert len(g) == 1
    assert g[0] == Filter.equal("name", "Vincent")


def test_filter_group_add_filter_not_equal():
    g = FilterGroup.empty().add_filter_not_equal("name", "Vincent")

    assert len(g) == 1
    assert g[0] == Filter.not_equal("name", "Vincent")


def test_filter_group_add_filter_greater_than():
    g = FilterGroup.empty().add_filter_greater_than("age", 18)

    assert len(g) == 1
    assert g[0] == Filter.greater_than("age", 18)


def test_filter_group_add_filter_greater_or_equal_than():
    g = FilterGroup.empty().add_filter_greater_or_equal_than("age", 18)

    assert len(g) == 1
    assert g[0] == Filter.greater_or_equal_than("age", 18)


def test_filter_group_add_filter_less_than():
    g = FilterGroup.empty().add_filter_less_than("age", 65)

    assert len(g) == 1
    assert g[0] == Filter.less_than("age", 65)


def test_filter_group_add_filter_less_or_equal_than():
    g = FilterGroup.empty().add_filter_less_or_equal_than("age", 65)

    assert len(g) == 1
    assert g[0] == Filter.less_or_equal_than("age", 65)


def test_filter_group_add_filter_in():
    g = FilterGroup.empty().add_filter_in("status", ["active", "pending"])

    assert len(g) == 1
    assert g[0] == Filter.in_("status", ["active", "pending"])


def test_filter_group_add_filter_not_in():
    g = FilterGroup.empty().add_filter_not_in("status", ["deleted"])

    assert len(g) == 1
    assert g[0] == Filter.not_in("status", ["deleted"])


def test_filter_group_add_filter_like():
    g = FilterGroup.empty().add_filter_like("name", "Vin%")

    assert len(g) == 1
    assert g[0] == Filter.like("name", "Vin%")


def test_filter_group_add_filter_not_like():
    g = FilterGroup.empty().add_filter_not_like("name", "Vin%")

    assert len(g) == 1
    assert g[0] == Filter.not_like("name", "Vin%")


def test_filter_group_add_filter_contains():
    g = FilterGroup.empty().add_filter_contains("tags", "vip")

    assert len(g) == 1
    assert g[0] == Filter.contains("tags", "vip")


def test_filter_group_add_filter_not_contains():
    g = FilterGroup.empty().add_filter_not_contains("tags", "spam")

    assert len(g) == 1
    assert g[0] == Filter.not_contains("tags", "spam")


def test_filter_group_chained_add_filter_methods():
    g = (
        FilterGroup.empty()
        .add_filter_equal("status", "active")
        .add_filter_greater_or_equal_than("age", 18)
        .add_filter_less_than("age", 65)
    )

    assert len(g) == 3


def test_order_default_is_asc():
    o = Order(("name",))
    assert o.type == OrderType.ASC


def test_order_desc_factory():
    o = Order.desc(("name",))
    assert o.type == OrderType.DESC


def test_order_asc_factory():
    o = Order.asc(("name",))
    assert o.type == OrderType.ASC


def test_order_none_factory():
    o = Order.none()
    assert o.type == OrderType.NONE
    assert o.by == ()


def test_order_multiple_columns():
    o = Order(("last_name", "first_name"), OrderType.ASC)
    assert o.by == ("last_name", "first_name")


def test_order_str():
    o = Order.desc(("name", "age"))
    assert str(o) == "name, age DESC"


def test_order_str_empty():
    o = Order.none()
    assert str(o) == ""


def test_order_by_is_immutable_tuple():
    o = Order(("name",))
    assert isinstance(o.by, tuple)


def test_page_defaults():
    p = Page()
    assert p.limit == 25
    assert p.offset == 0


def test_page_custom_values():
    p = Page(limit=100, offset=50)
    assert p.limit == 100
    assert p.offset == 50


def test_page_str():
    p = Page(10, 20)
    assert str(p) == "10, 20"


def test_criteria_with_filter_group():
    group = Filter.equal("name", "Vincent") + Filter.equal("surname", "Vega")
    c = Criteria().with_filter_group(group)

    assert len(c.groups) == 1
    assert len(c.groups[0]) == 2


def test_criteria_with_order():
    c = Criteria().with_order(Order.desc(("name", "surname")))

    assert c.order.type == OrderType.DESC
    assert c.order.by == ("name", "surname")


def test_criteria_with_page():
    c = Criteria().with_page(Page(10, 10))

    assert c.page.limit == 10
    assert c.page.offset == 10


def test_criteria_with_page_limit():
    c = Criteria().with_page_limit(50)

    assert c.page.limit == 50
    assert c.page.offset == 0


def test_criteria_with_page_offset():
    c = Criteria().with_page_offset(100)

    assert c.page.limit == 25
    assert c.page.offset == 100


def test_criteria_fluent_api():
    c = (
        Criteria()
        .filter("name", "==", "Vincent")
        .filter("surname", "==", "Vega")
        .order_by(("name", "surname"), "DESC")
        .limit(10)
        .offset(10)
    )

    assert isinstance(c, Criteria)
    assert len(c.filters) == 2


def test_criteria_filter_returns_new_instance():
    c1 = Criteria()
    c2 = c1.filter("name", "==", "Vincent")

    assert c1 is not c2
    assert len(c1.filters) == 0
    assert len(c2.filters) == 1


def test_criteria_order_by_returns_new_instance():
    c1 = Criteria()
    c2 = c1.order_by(("name",), "DESC")

    assert c1 is not c2
    assert c1.order.type == OrderType.NONE
    assert c2.order.type == OrderType.DESC


def test_criteria_limit_returns_new_instance():
    c1 = Criteria()
    c2 = c1.limit(50)

    assert c1 is not c2
    assert c1.page.limit == 25
    assert c2.page.limit == 50


def test_criteria_offset_returns_new_instance():
    c1 = Criteria()
    c2 = c1.offset(100)

    assert c1 is not c2
    assert c1.page.offset == 0
    assert c2.page.offset == 100


def test_criteria_filter_with_group_parameter():
    c = (
        Criteria()
        .filter("status", "==", "active", group=0)
        .filter("age", ">", 18, group=0)
        .filter("role", "==", "admin", group=1)
    )

    assert len(c.groups) == 2
    assert len(c.groups[0]) == 2
    assert len(c.groups[1]) == 1


def test_criteria_or_criteria():
    c1 = Criteria().with_filter_group(FilterGroup.create(Filter.equal("status", "active")))
    c2 = Criteria().with_filter_group(FilterGroup.create(Filter.equal("role", "admin")))

    result = c1 | c2

    assert len(result.groups) == 2
    assert len(result.groups[0]) == 1
    assert len(result.groups[1]) == 1


def test_criteria_and_criteria():
    c1 = Criteria().with_filter_group(FilterGroup.create(Filter.equal("tenant", "acme")))
    c2 = Criteria().with_filter_group(FilterGroup.create(Filter.equal("status", "active")))

    result = c1 & c2

    assert len(result.groups) == 1
    assert len(result.groups[0]) == 2


def test_criteria_or_only_accepts_criteria():
    c = Criteria()
    f = Filter.equal("a", 1)

    with pytest.raises(TypeError) as exc_info:
        c | f

    assert "unsupported operand type(s) for |: 'Criteria' and 'Filter'" in str(exc_info.value)
    assert "Use Criteria().with_filter_group()" in str(exc_info.value)


def test_criteria_and_only_accepts_criteria():
    c = Criteria()
    f = Filter.equal("a", 1)

    with pytest.raises(TypeError) as exc_info:
        c & f

    assert "unsupported operand type(s) for &: 'Criteria' and 'Filter'" in str(exc_info.value)
    assert "Use Criteria().with_filter_group()" in str(exc_info.value)


def test_criteria_or_rejects_filter_group():
    c = Criteria()
    g = FilterGroup.create(Filter.equal("a", 1))

    with pytest.raises(TypeError) as exc_info:
        c | g

    assert "unsupported operand type(s) for |: 'Criteria' and 'FilterGroup'" in str(exc_info.value)


def test_criteria_and_rejects_filter_group():
    c = Criteria()
    g = FilterGroup.create(Filter.equal("a", 1))

    with pytest.raises(TypeError) as exc_info:
        c & g

    assert "unsupported operand type(s) for &: 'Criteria' and 'FilterGroup'" in str(exc_info.value)


def test_criteria_operator_preserves_order_and_page():
    c1 = (
        Criteria()
        .with_filter_group(FilterGroup.create(Filter.equal("a", 1)))
        .with_order(Order.desc(("name",)))
        .with_page(Page(10, 20))
    )
    c2 = Criteria().with_filter_group(FilterGroup.create(Filter.equal("b", 2)))

    result = c1 | c2

    assert result.order.type == OrderType.DESC
    assert result.page.limit == 10
    assert result.page.offset == 20


def test_criteria_chained_with_methods():
    group = FilterGroup.create(Filter.equal("a", 1))
    c = Criteria().with_filter_group(group).with_order(Order.desc(("name",))).with_page_limit(10).with_page_offset(20)

    assert len(c.groups) == 1
    assert c.order.type == OrderType.DESC
    assert c.page.limit == 10
    assert c.page.offset == 20


def test_criteria_filters_property_flattens():
    group1 = Filter.equal("a", 1) + Filter.equal("b", 2)
    group2 = FilterGroup.create(Filter.equal("c", 3))
    c = Criteria().with_filter_group(group1).with_filter_group(group2)

    filters = c.filters
    assert len(filters) == 3


def test_criteria_groups_property():
    c = (
        Criteria()
        .with_filter_group(FilterGroup.create(Filter.equal("a", 1)))
        .with_filter_group(FilterGroup.create(Filter.equal("b", 2)))
    )

    assert len(c.groups) == 2
    assert all(isinstance(g, FilterGroup) for g in c.groups)


def test_criteria_has_filters_true():
    c = Criteria().with_filter_group(FilterGroup.create(Filter.equal("a", 1)))
    assert c.has_filters() is True


def test_criteria_has_filters_false():
    c = Criteria()
    assert c.has_filters() is False


def test_criteria_has_order_true():
    c = Criteria().with_order(Order.desc(("name",)))
    assert c.has_order() is True


def test_criteria_has_order_false():
    c = Criteria()
    assert c.has_order() is False


def test_criteria_equality():
    group = FilterGroup.create(Filter.equal("a", 1))
    c1 = Criteria().with_filter_group(group)
    c2 = Criteria().with_filter_group(group)

    assert c1 == c2


def test_criteria_hash():
    group = FilterGroup.create(Filter.equal("a", 1))
    c1 = Criteria().with_filter_group(group)
    c2 = Criteria().with_filter_group(group)

    assert hash(c1) == hash(c2)


def test_complex_query_building():
    active_adults = FilterGroup.empty().add_filter_equal("status", "active").add_filter_greater_or_equal_than("age", 18)
    admins = FilterGroup.create(Filter.equal("role", "admin"), Filter.greater_or_equal_than("level", 5))

    c1 = Criteria().with_filter_group(active_adults)
    c2 = Criteria().with_filter_group(admins)
    combined = (c1 | c2).with_order(Order.desc(("last_name", "first_name"))).with_page_limit(20).with_page_offset(40)

    assert len(combined.groups) == 2
    assert len(combined.groups[0]) == 2
    assert len(combined.groups[1]) == 2
    assert combined.order.by == ("last_name", "first_name")
    assert combined.page.limit == 20
    assert combined.page.offset == 40


def test_complex_query_with_fluent_api():
    c = (
        Criteria()
        .filter("status", "==", "active", group=0)
        .filter("age", ">", 18, group=0)
        .filter("role", "==", "admin", group=1)
        .filter("level", ">=", 5, group=1)
        .order_by(("last_name", "first_name"), "DESC")
        .limit(20)
        .offset(40)
    )

    assert len(c.groups) == 2
    assert len(c.groups[0]) == 2
    assert len(c.groups[1]) == 2


def test_filter_composition_to_criteria():
    active_adults = Filter.equal("status", "active") + Filter.greater_than("age", 18)
    admin_users = FilterGroup.create(Filter.equal("role", "admin"))

    c = Criteria().with_filter_group(active_adults).with_filter_group(admin_users)

    assert len(c.groups) == 2


def test_merging_criteria_or():
    active_users = Criteria().with_filter_group(Filter.equal("status", "active") + Filter.greater_than("age", 18))
    admin_users = Criteria().with_filter_group(FilterGroup.create(Filter.equal("role", "admin")))

    combined = active_users | admin_users

    assert len(combined.groups) == 2


def test_merging_criteria_and():
    tenant_filter = Criteria().with_filter_group(FilterGroup.create(Filter.equal("tenant", "acme")))
    status_filter = Criteria().with_filter_group(FilterGroup.create(Filter.equal("status", "active")))

    merged = tenant_filter & status_filter

    assert len(merged.groups) == 1
    assert len(merged.groups[0]) == 2


def test_empty_criteria_and():
    c1 = Criteria()
    c2 = Criteria()

    result = c1 & c2

    assert len(result.groups) == 0


def test_filter_empty_field_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        Filter("", Operator.EQUAL, "value")

    assert "Filter field cannot be empty" in str(exc_info.value)


def test_filter_whitespace_field_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        Filter("   ", Operator.EQUAL, "value")

    assert "Filter field cannot be empty" in str(exc_info.value)


def test_page_negative_limit_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        Page(limit=-1)

    assert "limit must be >= 0" in str(exc_info.value)


def test_page_negative_offset_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        Page(offset=-1)

    assert "offset must be >= 0" in str(exc_info.value)


def test_page_zero_limit_is_valid():
    p = Page(limit=0)
    assert p.limit == 0


def test_page_zero_offset_is_valid():
    p = Page(offset=0)
    assert p.offset == 0


def test_filter_repr():
    f = Filter.equal("name", "Vincent")
    assert repr(f) == "Filter('name', EQUAL, 'Vincent')"


def test_filter_repr_with_number():
    f = Filter.greater_than("age", 18)
    assert repr(f) == "Filter('age', GT, 18)"


def test_filter_group_repr_empty():
    g = FilterGroup()
    assert repr(g) == "FilterGroup()"


def test_filter_group_repr_with_filters():
    g = Filter.equal("a", 1) + Filter.equal("b", 2)
    assert repr(g) == "FilterGroup(Filter('a', EQUAL, 1), Filter('b', EQUAL, 2))"


def test_criteria_repr_empty():
    c = Criteria()
    assert repr(c) == "Criteria(groups=0)"


def test_criteria_repr_with_filters():
    c = Criteria().with_filter_group(FilterGroup.create(Filter.equal("a", 1)))
    assert "groups=1" in repr(c)
    assert "filters=1" in repr(c)


def test_criteria_repr_with_order():
    c = Criteria().with_order(Order.desc(("name",)))
    assert "order=('name',)" in repr(c)


def test_criteria_repr_with_custom_page():
    c = Criteria().with_page(Page(10, 20))
    assert "page=(10, 20)" in repr(c)


def test_criteria_repr_full():
    c = (
        Criteria()
        .with_filter_group(FilterGroup.create(Filter.equal("a", 1)))
        .with_order(Order.desc(("name",)))
        .with_page(Page(10, 20))
    )
    r = repr(c)
    assert "groups=1" in r
    assert "filters=1" in r
    assert "order=('name',)" in r
    assert "page=(10, 20)" in r


def test_filter_add_invalid_type_raises_type_error():
    f = Filter.equal("a", 1)

    with pytest.raises(TypeError) as exc_info:
        f + "invalid"

    assert "unsupported operand type(s) for +: 'Filter' and 'str'" in str(exc_info.value)


def test_filter_group_add_invalid_type_raises_type_error():
    g = FilterGroup.create(Filter.equal("a", 1))

    with pytest.raises(TypeError) as exc_info:
        g + "invalid"

    assert "unsupported operand type(s) for +: 'FilterGroup' and 'str'" in str(exc_info.value)


def test_filter_group_radd_invalid_type_raises_type_error():
    g = FilterGroup.create(Filter.equal("a", 1))

    with pytest.raises(TypeError) as exc_info:
        "invalid" + g

    assert "unsupported operand type(s) for +" in str(exc_info.value)


def test_criteria_str_empty():
    c = Criteria()
    assert str(c) == ""


def test_criteria_str_with_filters():
    c = Criteria().with_filter_group(Filter.equal("status", "active") + Filter.greater_than("age", 18))
    assert str(c) == "WHERE (status == active AND age > 18)"


def test_criteria_str_with_multiple_groups():
    c = (
        Criteria()
        .with_filter_group(Filter.equal("status", "active") + Filter.greater_than("age", 18))
        .with_filter_group(FilterGroup.create(Filter.equal("role", "admin")))
    )
    assert str(c) == "WHERE (status == active AND age > 18) OR (role == admin)"


def test_criteria_str_with_order():
    c = Criteria().with_order(Order.desc(("name",)))
    assert str(c) == "ORDER BY name DESC"


def test_criteria_str_with_page():
    c = Criteria().with_page(Page(10, 20))
    assert str(c) == "LIMIT 10 OFFSET 20"


def test_criteria_str_full():
    c = (
        Criteria()
        .with_filter_group(Filter.equal("status", "active") + Filter.greater_than("age", 18))
        .with_filter_group(FilterGroup.create(Filter.equal("role", "admin")))
        .with_order(Order.desc(("name",)))
        .with_page(Page(10, 20))
    )
    expected = "WHERE (status == active AND age > 18) OR (role == admin) ORDER BY name DESC LIMIT 10 OFFSET 20"
    assert str(c) == expected
