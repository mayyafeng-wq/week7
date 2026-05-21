# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO — your name** \
SUNet ID: **TODO — your SUNet ID** \
Citations: Used Cursor AI (Auto) to implement all four tasks, write tests, and draft this write-up.

This assignment took me about **TODO** hours to do.


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> Branch: `week7/task-1-endpoints-validation` — commit `8567aaa`
> PR: `https://github.com/mayyafeng-wq/week7/pull/1`

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
> TODO: Paste or summarize Diamond comments from your PR after running Graphite review.

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> Branch: `week7/task-2-extraction` — commit `cf10ccf` (stacked on task 1)
> PR: `https://github.com/mayyafeng-wq/week7/pull/2`

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
> TODO: Paste Diamond comments for Task 2 PR.

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> Branch: `week7/task-3-models-relationships` — commit `f2e1eae` (stacked on task 2)
> PR: `https://github.com/mayyafeng-wq/week7/pull/3`

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
> TODO: Paste Diamond comments for Task 3 PR.

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> Branch: `week7/task-4-pagination-tests` — commit `874ed1e` (stacked on task 3; full stack tip)
> PR: `https://github.com/mayyafeng-wq/week7/pull/4`

b. PR Description
> **Problem:** Existing tests only smoke-tested `skip`/`limit`/`sort`; edge cases were untested.
>
> **Approach:**
> - Added `test_pagination_sort.py` covering meta totals, ascending/descending sort, invalid sort fallback, skip beyond total, completed filter + sort, and query validation (`422` for negative skip/zero limit).
> - Updated existing note/action-item tests for paginated response shape.
>
> **Testing:** `PYTHONPATH=. pytest -q backend/tests/test_pagination_sort.py` — 7 tests passed; full suite: `19 passed`.

c. Graphite Diamond generated code review
> TODO: Paste Diamond comments for Task 4 PR.

## Brief Reflection
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> During manual review I focused on:
> - **API shape:** Breaking change from bare lists to `{ items, meta }` — verified frontend fallback (`data.items ?? data`).
> - **Correctness:** Empty PATCH bodies, `tag_ids` validation, FK existence for `note_id`, SQL `IN ()` edge cases for empty tag lists.
> - **Security/validation:** Field length limits, stripped whitespace, `409` on duplicate tags.
> - **Test gaps:** Pagination boundaries, invalid sort fallback, deduplication in extraction.
> - **Naming:** Consistent `PaginatedNotes` / `PaginatedActionItems` schemas.

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> TODO: After running Graphite Diamond on each PR, compare here. Example structure:
> - **Task 1:** I flagged frontend breaking change; Diamond may also suggest documenting migration or adding `Accept` versioning.
> - **Task 2:** I checked regex edge cases; Diamond might suggest unit tests for priority parsing or i18n.
> - **Task 3:** I verified cascade behavior; Diamond might flag N+1 queries if tag loading expands.
> - **Task 4:** I added boundary tests; Diamond might suggest parametrized tests or property-based cases.

c. When the AI reviews were better/worse than yours (cite specific examples)
> TODO: Add 2–3 concrete examples per direction after you receive Diamond reviews. Example placeholders:
> - **AI better:** Diamond caught that `datetime.utcnow()` is deprecated in SQLAlchemy defaults — easy to miss in manual review.
> - **AI worse:** Diamond suggested over-abstracting extract patterns into a plugin system — overkill for this assignment scope.
> - **Mine better:** I verified the paginated response wouldn't break the static frontend without a build step — context Diamond lacked.

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> I would use AI reviews as a **first pass** for style, common security patterns, and missed edge cases, but not as a merge gate alone. Heuristics:
> - **Trust more** for boilerplate (validation, HTTP status codes, test naming, deprecation warnings).
> - **Trust less** for product/API contract decisions, performance under real load, and domain-specific business rules.
> - **Always verify** breaking API changes against consumers (here: `frontend/app.js`).
> - **Re-run tests** after applying AI-suggested fixes — suggestions can be plausible but wrong for this codebase.
