def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] >= 1
    assert len(body["items"]) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_action_item_get_delete_and_note_link(client):
    note = client.post("/notes/", json={"title": "Linked", "content": "Note"}).json()

    r = client.post(
        "/action-items/",
        json={"description": "From note", "note_id": note["id"]},
    )
    assert r.status_code == 201
    item = r.json()
    assert item["note_id"] == note["id"]

    r = client.get(f"/action-items/{item['id']}")
    assert r.status_code == 200

    r = client.delete(f"/action-items/{item['id']}")
    assert r.status_code == 204

    r = client.post("/action-items/", json={"description": "Bad link", "note_id": 99999})
    assert r.status_code == 404


def test_extract_endpoint(client):
    text = "TODO: write tests\n- [ ] Review @alice due Friday"
    r = client.post("/action-items/extract", json={"text": text})
    assert r.status_code == 200
    items = r.json()["items"]
    assert any("write tests" in i["text"].lower() for i in items)
    assert any(i.get("assignee") == "alice" for i in items)
