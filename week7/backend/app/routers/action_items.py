from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Note
from ..schemas import (
    ActionItemCreate,
    ActionItemPatch,
    ActionItemRead,
    ExtractRequest,
    ExtractResponse,
    ExtractedActionItem,
    PaginatedActionItems,
    PaginatedMeta,
)
from ..services.extract import analyze_action_items

router = APIRouter(prefix="/action-items", tags=["action_items"])

ALLOWED_SORT_FIELDS = {"id", "description", "completed", "created_at", "updated_at", "note_id"}


def _apply_item_filters(stmt, completed: Optional[bool], note_id: Optional[int]):
    if completed is not None:
        stmt = stmt.where(ActionItem.completed.is_(completed))
    if note_id is not None:
        stmt = stmt.where(ActionItem.note_id == note_id)
    return stmt


def _apply_item_sort(stmt, sort: str):
    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if sort_field in ALLOWED_SORT_FIELDS:
        return stmt.order_by(order_fn(getattr(ActionItem, sort_field)))
    return stmt.order_by(desc(ActionItem.created_at))


def _validate_note_id(note_id: int | None, db: Session) -> None:
    if note_id is None:
        return
    if not db.get(Note, note_id):
        raise HTTPException(status_code=404, detail="Linked note not found")


@router.get("/", response_model=PaginatedActionItems)
def list_items(
    db: Session = Depends(get_db),
    completed: Optional[bool] = None,
    note_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at"),
) -> PaginatedActionItems:
    base_stmt = _apply_item_filters(select(ActionItem), completed, note_id)
    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    rows = (
        db.execute(_apply_item_sort(base_stmt, sort).offset(skip).limit(limit)).scalars().all()
    )
    return PaginatedActionItems(
        items=[ActionItemRead.model_validate(row) for row in rows],
        meta=PaginatedMeta(total=total, skip=skip, limit=limit),
    )


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    _validate_note_id(payload.note_id, db)
    item = ActionItem(
        description=payload.description.strip(),
        completed=False,
        note_id=payload.note_id,
    )
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.get("/{item_id}", response_model=ActionItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return ActionItemRead.model_validate(item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ActionItemRead)
def patch_item(
    item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)
) -> ActionItemRead:
    if not payload.model_fields_set:
        raise HTTPException(status_code=400, detail="At least one field must be provided")

    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    if "note_id" in payload.model_fields_set:
        if payload.note_id is not None:
            _validate_note_id(payload.note_id, db)
        item.note_id = payload.note_id
    if payload.description is not None:
        item.description = payload.description.strip()
    if payload.completed is not None:
        item.completed = payload.completed

    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=204, response_class=Response)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    db.delete(item)
    db.flush()
    return Response(status_code=204)


@router.post("/extract", response_model=ExtractResponse)
def extract_items(payload: ExtractRequest) -> ExtractResponse:
    analyzed = analyze_action_items(payload.text)
    return ExtractResponse(
        items=[
            ExtractedActionItem(
                text=item.text,
                priority=item.priority,
                assignee=item.assignee,
                due_date=item.due_date,
            )
            for item in analyzed
        ]
    )
