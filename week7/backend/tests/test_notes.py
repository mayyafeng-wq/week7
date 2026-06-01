def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "meta" in body
    assert body["meta"]["total"] >= 1
    assert len(body["items"]) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_note_validation_and_delete(client):
    r = client.post("/notes/", json={"title": "", "content": "x"})
    assert r.status_code == 422

    r = client.post("/notes/", json={"title": "Delete me", "content": "Soon gone"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_patch_note_requires_fields(client):
    r = client.post("/notes/", json={"title": "Patch", "content": "Body"})
    note_id = r.json()["id"]

    r = client.patch(f"/notes/{note_id}", json={})
    assert r.status_code == 400
