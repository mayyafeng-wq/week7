# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Mayya** \
SUNet ID: **TODO — fill before Gradescope** \
Citations: Used Cursor AI (Auto) to implement all four tasks, write tests, open stacked PRs, enable Graphite Diamond, and draft this write-up.

This assignment took me about **5** hours to do.


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> Branch: `week7/task-1-endpoints-validation` — commit `8567aaa`
> PR: https://github.com/mayyafeng-wq/week7/pull/1

b. PR Description
> **Problem:** List/detail endpoints lacked delete flows, paginated metadata, and strict request validation.
>
> **Approach:**
> - Added `DELETE /notes/{id}` and `DELETE /action-items/{id}` plus `GET /action-items/{id}`.
> - Added Pydantic `Field` constraints (length bounds) and validators rejecting blank strings on patch.
> - Returned `400` when PATCH bodies are empty; `422` for invalid query params (`skip < 0`, `limit < 1`).
> - Wrapped list endpoints in `{ items, meta: { total, skip, limit } }` for pagination metadata.
>
> **Testing:** `cd week7 && PYTHONPATH=. pytest -q backend/tests/test_notes.py backend/tests/test_action_items.py` — all passed.

c. Graphite Diamond generated code review
> **Status:** `graphite-app[bot]` reviewed PR #1 but did **not** leave inline comments (after multiple `trigger diamond review` commits). Diamond likely found no actionable bugs in this diff.
>
> **Manual line-by-line review (done before merge):**
> - Verified list response shape change is backward-compatible in `frontend/app.js` via `data.items ?? data`.
> - Checked `skip`/`limit` bounds on query params and empty PATCH returns 400.
> - Confirmed DELETE returns 204 and subsequent GET returns 404.
>
> **Diamond vs manual:** I focused on client breakage and HTTP semantics; Diamond had nothing to flag on this PR. A human reviewer still adds value for API contract and frontend compatibility checks Diamond may skip when no obvious bug is present.

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> Branch: `week7/task-2-extraction` — commit `cf10ccf` (stacked on task 1)
> PR: https://github.com/mayyafeng-wq/week7/pull/2

b. PR Description
> **Problem:** Extraction only matched `todo:`/`action:` prefixes and lines ending in `!`.
>
> **Approach:**
> - Extended `analyze_action_items()` to detect checkboxes (`- [ ]`), numbered modal-verb lines, `need to`/`should`/`must`, follow-ups, assignees (`@name`), due dates, and priority keywords.
> - Added deduplication and structured output (`priority`, `assignee`, `due_date`).
> - Exposed `POST /action-items/extract` returning structured items; kept `extract_action_items()` for backward compatibility.
>
> **Testing:** `PYTHONPATH=. pytest -q backend/tests/test_extract.py backend/tests/test_action_items.py::test_extract_endpoint` — all passed.

c. Graphite Diamond generated code review
> **graphite-app[bot]** left 1 inline comment on `week7/backend/app/services/extract.py:48`:
>
> > The `PRIORITY_KEYWORDS` dictionary doesn't contain a mapping for `"low priority"`, but the `PRIORITY_PATTERN` on line 21 can match it. When `token` is `"low priority"`, the `.get(token, "medium")` call returns `"medium"` instead of `"low"`.
> >
> > **Impact:** Items marked as "low priority" will be incorrectly classified as "medium" priority.
> >
> > **Fix:** Add `"low priority": "low"` to `PRIORITY_KEYWORDS`.
>
> **Manual line-by-line review:**
> - Regex patterns reviewed for false positives on normal prose lines.
> - Deduplication key uses lowercased text — acceptable for assignment scope.
> - `POST /extract` has no DB side effects; appropriate for stateless service.
>
> **Response:** Applied Diamond's fix on the task-4 stack tip (`"low priority": "low"` added to `PRIORITY_KEYWORDS`).

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> Branch: `week7/task-3-models-relationships` — commit `f2e1eae` (stacked on task 2)
> PR: https://github.com/mayyafeng-wq/week7/pull/3

b. PR Description
> **Problem:** Notes and action items were unrelated; no taxonomy for organizing notes.
>
> **Approach:**
> - Added `Tag` model and `note_tags` many-to-many association table.
> - Linked `ActionItem.note_id` → `Note` (optional FK, `SET NULL` on delete).
> - Added `/tags` CRUD router and `PUT /notes/{id}/tags` to attach tags.
> - Updated `seed.sql` and creation schemas to support `note_id` on action items.
>
> **Testing:** `PYTHONPATH=. pytest -q backend/tests/test_tags.py backend/tests/test_action_items.py::test_action_item_get_delete_and_note_link` — all passed.

c. Graphite Diamond generated code review
> **graphite-app[bot]** left 1 inline comment on `week7/backend/app/routers/action_items.py:117`:
>
> > Critical bug: Cannot clear `note_id` via PATCH. When `payload.note_id` is explicitly set to `null`, the condition `if payload.note_id is not None:` evaluates to False, so the note_id is never updated. Once a note_id is set, it cannot be cleared back to null.
> >
> > **Fix:** Use `payload.model_fields_set` to detect explicitly provided fields:
> > ```python
> > if "note_id" in payload.model_fields_set:
> >     if payload.note_id is not None:
> >         _validate_note_id(payload.note_id, db)
> >     item.note_id = payload.note_id
> > ```
> > Also update the empty-PATCH guard to `if not payload.model_fields_set`.
>
> **Manual line-by-line review:**
> - Tag names normalized to lowercase on create — consistent with tests.
> - Empty `tag_ids` clears tags (avoids invalid `IN ()` SQL).
> - FK validation on `note_id` returns 404 when note missing.
>
> **Response:** Applied Diamond's fix using `model_fields_set` for PATCH empty-body and nullable `note_id` clearing.

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> Branch: `week7/task-4-pagination-tests` — commit `6aba952` (stacked on task 3; full stack tip)
> PR: https://github.com/mayyafeng-wq/week7/pull/4

b. PR Description
> **Problem:** Existing tests only smoke-tested `skip`/`limit`/`sort`; edge cases were untested.
>
> **Approach:**
> - Added `test_pagination_sort.py` covering meta totals, ascending/descending sort, invalid sort fallback, skip beyond total, completed filter + sort, and query validation (`422` for negative skip/zero limit).
> - Updated existing note/action-item tests for paginated response shape.
>
> **Testing:** `PYTHONPATH=. pytest -q backend/tests/test_pagination_sort.py` — 7 tests passed; full suite: `19 passed`.

c. Graphite Diamond generated code review
> **Status:** `graphite-app[bot]` did **not** leave inline comments on PR #4 (test-only diff). Diamond typically targets production logic bugs; this PR adds assertions rather than new application behavior.
>
> **Manual line-by-line review:**
> - Tests assert exact `meta` totals after creating known row counts.
> - Invalid sort field falls back to default ordering (documented behavior).
> - Query validation tests use `422` for negative `skip` and zero `limit`.
>
> **Diamond vs manual:** I verified deterministic pagination assertions and isolation via fresh DB per test; Diamond had no test-quality suggestions on this PR.

## Brief Reflection
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> During manual review I focused on:
> - **API shape:** Breaking change from bare lists to `{ items, meta }` — verified frontend fallback (`data.items ?? data`).
> - **Correctness:** Empty PATCH bodies, `tag_ids` validation, FK existence for `note_id`, SQL `IN ()` edge cases for empty tag lists.
> - **Security/validation:** Field length limits, stripped whitespace, `409` on duplicate tags.
> - **Test gaps:** Pagination boundaries, invalid sort fallback, deduplication in extraction.
> - **Naming:** Consistent `PaginatedNotes` / `PaginatedActionItems` schemas.

b. A comparison of **your** comments vs. **Graphite's** AI-generated comments for each PR.
> **Task 1:** I checked HTTP semantics (204/404/400/422) and frontend compatibility. Diamond left no inline comments — it did not surface API migration or `datetime.utcnow` deprecation concerns I might have expected.
> **Task 2:** I reviewed regex false positives and stateless extract design. Diamond found a **specific logic bug** I missed: `"low priority"` regex match maps to `"medium"` because the keyword dict was incomplete.
> **Task 3:** I verified FK validation and empty-tag clearing. Diamond found a **nullable PATCH edge case** I missed: explicit `note_id: null` cannot clear the FK with `if payload.note_id is not None`.
> **Task 4:** I checked pagination test determinism. Diamond left no comments on the test-only PR.

c. When the AI reviews were better/worse than yours (cite specific examples)
> **AI better (Task 2):** Diamond caught that `PRIORITY_PATTERN` matches `"low priority"` but `PRIORITY_KEYWORDS` lacks that key, causing wrong `"medium"` classification — a concrete bug my manual review missed while focusing on regex breadth.
> **AI better (Task 3):** Diamond identified that PATCH cannot clear `note_id` to null — a subtle Pydantic `None` vs "field omitted" distinction I did not test or note.
> **Manual review better (Task 1):** I verified `frontend/app.js` handles `{items, meta}` without a build step; Diamond had no product-context feedback on this breaking API change.
> **Manual review better (Task 3):** I caught empty `tag_ids` clearing tags (SQL `IN ()` edge case); Diamond focused on PATCH semantics instead.
> **AI silent (Task 4):** Diamond did not suggest `@pytest.mark.parametrize` for sort cases — something I expected but did not implement.

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> I would use AI reviews as a **first pass** for logic bugs and nullable/optional-field edge cases, but not as a merge gate alone. Heuristics:
> - **Trust more** for dictionary/map completeness vs regex patterns, nullable PATCH semantics, and deprecation warnings.
> - **Trust less** for product/API contract decisions, frontend consumer impact, and test-only PRs (Diamond may stay silent).
> - **Always verify** suggestions against tests — Diamond's Task 3 fix using `model_fields_set` was correct and I applied it; full suite still passes (19 tests).
> - **Combine** human review for integration/context with AI for line-level logic gaps.
