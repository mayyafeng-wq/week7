from backend.app.services.extract import analyze_action_items, extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


def test_extract_checkbox_and_modal_verbs():
    text = """
    - [ ] Draft design doc
    1. We should deploy on Friday
    need to update dependencies
    """.strip()
    items = extract_action_items(text)
    assert "Draft design doc" in items
    assert any("deploy" in item.lower() for item in items)
    assert any("dependencies" in item.lower() for item in items)


def test_analyze_action_items_metadata():
    text = "TODO: urgent fix @bob due 2026-05-30"
    analyzed = analyze_action_items(text)
    assert len(analyzed) == 1
    item = analyzed[0]
    assert item.assignee == "bob"
    assert item.priority == "high"
    assert item.due_date == "2026-05-30"


def test_extract_deduplicates_lines():
    text = "TODO: ship\nTODO: ship"
    assert len(extract_action_items(text)) == 1
