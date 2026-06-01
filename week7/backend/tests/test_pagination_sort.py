def _create_notes(client, count: int) -> list[int]:
    ids = []
    for i in range(count):
        r = client.post("/notes/", json={"title": f"Note {i}", "content": f"Body {i}"})
        assert r.status_code == 201
        ids.append(r.json()["id"])
    return ids


def _create_action_items(client, count: int) -> list[int]:
    ids = []
    for i in range(count):
        r = client.post("/action-items/", json={"description": f"Task {i}"})
        assert r.status_code == 201
        ids.append(r.json()["id"])
    return ids


def test_notes_pagination_meta(client):
    _create_notes(client, 5)
    r = client.get("/notes/", params={"skip": 2, "limit": 2, "sort": "id"})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"] == {"total": 5, "skip": 2, "limit": 2}
    assert len(body["items"]) == 2
    assert body["items"][0]["id"] < body["items"][1]["id"]


def test_notes_sort_descending(client):
    _create_notes(client, 3)
    r = client.get("/notes/", params={"sort": "-title", "limit": 10})
    titles = [n["title"] for n in r.json()["items"]]
    assert titles == sorted(titles, reverse=True)


def test_notes_invalid_sort_falls_back(client):
    _create_notes(client, 2)
    r = client.get("/notes/", params={"sort": "not_a_field"})
    assert r.status_code == 200
    assert len(r.json()["items"]) == 2


def test_notes_skip_beyond_total_returns_empty(client):
    _create_notes(client, 2)
    r = client.get("/notes/", params={"skip": 10, "limit": 5})
    body = r.json()
    assert body["meta"]["total"] == 2
    assert body["items"] == []


def test_action_items_pagination_and_filters(client):
    ids = _create_action_items(client, 4)
    client.put(f"/action-items/{ids[0]}/complete")
    client.put(f"/action-items/{ids[1]}/complete")

    r = client.get(
        "/action-items/",
        params={"completed": False, "skip": 0, "limit": 10, "sort": "-id"},
    )
    body = r.json()
    assert body["meta"]["total"] == 2
    open_ids = [item["id"] for item in body["items"]]
    assert open_ids == sorted(open_ids, reverse=True)


def test_action_items_sort_by_description(client):
    _create_action_items(client, 3)
    r = client.get("/action-items/", params={"sort": "description", "limit": 10})
    descriptions = [item["description"] for item in r.json()["items"]]
    assert descriptions == sorted(descriptions)


def test_pagination_query_validation(client):
    r = client.get("/notes/", params={"skip": -1})
    assert r.status_code == 422

    r = client.get("/notes/", params={"limit": 0})
    assert r.status_code == 422
