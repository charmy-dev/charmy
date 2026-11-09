from charmy.utils.var import Query, Var, resolve_references


def test_resolves_nested_references_in_containers_and_attributes():
    class Payload:
        value: object

    payload = Payload()
    payload.value = Var([Query(lambda: Var(7))])
    source = {"payload": payload, "values": (Var(3), [Query(lambda: 5)])}

    result = resolve_references(source)

    assert result is source
    assert payload.value == [7]
    assert source["values"] == (3, [5])


def test_resolves_a_shared_query_only_once():
    calls = 0

    def get_value():
        nonlocal calls
        calls += 1
        return 12

    query = Query(get_value)
    values = [query, query]

    assert resolve_references(values) == [12, 12]
    assert calls == 1


def test_resolves_slotted_object_attributes():
    class Payload:
        __slots__ = ("value",)
        value: object

    payload = Payload()
    payload.value = Var({"answer": Query(lambda: 42)})

    assert resolve_references(payload) is payload
    assert payload.value == {"answer": 42}


def test_preserves_container_cycles():
    values = []
    values.append(values)

    result = resolve_references(values)

    assert result is values
    assert values[0] is values
