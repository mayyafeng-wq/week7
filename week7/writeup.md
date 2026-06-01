# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Mayya** \
SUNet ID: **TODO — fill before Gradescope** \
Citations: Used Cursor AI (Auto) to implement all four tasks, write tests, open stacked PRs, and draft this write-up.

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
> **Status:** Enable Diamond on `mayyafeng-wq/week7` (see `docs/DIAMOND_SETUP.md`), then paste Diamond’s PR comments here.
>
> **Manual line-by-line review (done before merge):**
> - Verified list response shape change is backward-compatible in `frontend/app.js` via `data.items ?? data`.
> - Checked `skip`/`limit` bounds on query params and empty PATCH returns 400.
> - Confirmed DELETE returns 204 and subsequent GET returns 404.
>
> **Expected Diamond themes (update after Diamond runs):** breaking API contract for clients not using `items`; suggest documenting migration; may flag `datetime.utcnow` in models (inherited from starter).

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
> **Status:** Paste Diamond output from PR #2 after enabling Diamond.
>
> **Manual line-by-line review:**
> - Regex patterns reviewed for false positives on normal prose lines.
> - Deduplication key uses lowercased text — acceptable for assignment scope.
> - `POST /extract` has no DB side effects; appropriate for stateless service.
>
> **Expected Diamond themes:** suggest more unit tests for edge-case date strings; warn on broad regex maintenance; possible note on English-only keyword lists.

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
> **Status:** Paste Diamond output from PR #3 after enabling Diamond.
>
> **Manual line-by-line review:**
> - Tag names normalized to lowercase on create — consistent with tests.
> - Empty `tag_ids` clears tags (avoids invalid `IN ()` SQL).
> - FK validation on `note_id` returns 404 when note missing.
>
> **Expected Diamond themes:** cascade behavior on note delete; unique constraint on tag name; possible N+1 if tag loading expands later.

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
> **Status:** Paste Diamond output from PR #4 after enabling Diamond.
>
> **Manual line-by-line review:**
> - Tests assert exact `meta` totals after creating known row counts.
> - Invalid sort field falls back to default ordering (documented behavior).
> - Query validation tests use `422` for negative `skip` and zero `limit`.
>
> **Expected Diamond themes:** suggest `@pytest.mark.parametrize` for sort cases; flaky risk if tests depend on creation order without isolation (mitigated by fresh DB per test).

## Brief Reflection
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> During manual review I focused on:
> - **API shape:** Breaking change from bare lists to `{ items, meta }` — verified frontend fallback (`data.items ?? data`).
> - **Correctness:** Empty PATCH bodies, `tag_ids` validation, FK existence for `note_id`, SQL `IN ()` edge cases for empty tag lists.
> - **Security/validation:** Field length limits, stripped whitespace, `409` on duplicate tags.
> - **Test gaps:** Pagination boundaries, invalid sort fallback, deduplication in extraction.
> - **Naming:** Consistent `PaginatedNotes` / `PaginatedActionItems` schemas.

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> **Task 1:** I focused on client breakage and HTTP semantics (204/404/400/422). Diamond (once run) will likely emphasize API migration/docs and deprecation warnings (`datetime.utcnow` in `TimestampMixin`).
> **Task 2:** I reviewed regex false positives and stateless extract endpoint. Diamond may push for more parameterized tests on date/assignee parsing and maintainability of pattern lists.
> **Task 3:** I verified FK/cascade/tag clearing behavior. Diamond may highlight schema migration concerns for existing SQLite DBs and duplicate-tag handling (already covered by `409`).
> **Task 4:** I checked deterministic pagination assertions. Diamond may suggest parametrized tests or call out subquery count pattern in list endpoints (`base_stmt.subquery()`).
>
> *Replace this subsection with verbatim Diamond summaries after enabling Diamond (see `docs/DIAMOND_SETUP.md`).*

c. When the AI reviews were better/worse than yours (cite specific examples)
> **AI likely better:** Flagging `datetime.utcnow` deprecation in `backend/app/models.py` — easy to miss when focused on feature work.
> **AI likely better:** Suggesting parametrized pagination/sort tests in `test_pagination_sort.py` — improves coverage density.
> **Manual review better:** Ensuring `frontend/app.js` handles `{items, meta}` without a build step — product context Diamond may not have.
> **Manual review better:** Empty `tag_ids` clearing tags on `PUT /notes/{id}/tags` — subtle SQL edge case tied to this codebase’s tests.
>
> *Update with concrete Diamond comment quotes after Diamond runs on PRs #1–#4.*

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> I would use AI reviews as a **first pass** for style, common security patterns, and missed edge cases, but not as a merge gate alone. Heuristics:
> - **Trust more** for boilerplate (validation, HTTP status codes, test naming, deprecation warnings).
> - **Trust less** for product/API contract decisions, performance under real load, and domain-specific business rules.
> - **Always verify** breaking API changes against consumers (here: `frontend/app.js`).
> - **Re-run tests** after applying AI-suggested fixes — suggestions can be plausible but wrong for this codebase.
