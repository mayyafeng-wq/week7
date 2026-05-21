def test_create_list_and_attach_tags_to_note(client):
    tag_a = client.post("/tags/", json={"name": "Backend"}).json()
    tag_b = client.post("/tags/", json={"name": "Frontend"}).json()

    note = client.post("/notes/", json={"title": "Tagged", "content": "Body"}).json()
    r = client.put(f"/notes/{note['id']}/tags", json={"tag_ids": [tag_a["id"], tag_b["id"]]})
    assert r.status_code == 200
    names = set(r.json())
    assert names == {"backend", "frontend"}

    r = client.get("/tags/", params={"q": "back"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_duplicate_tag_returns_conflict(client):
    client.post("/tags/", json={"name": "Ops"})
    r = client.post("/tags/", json={"name": "ops"})
    assert r.status_code == 409
