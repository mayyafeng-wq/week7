from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import (
    NoteCreate,
    NotePatch,
    NoteRead,
    NoteTagUpdate,
    PaginatedMeta,
    PaginatedNotes,
)

router = APIRouter(prefix="/notes", tags=["notes"])

ALLOWED_SORT_FIELDS = {"id", "title", "created_at", "updated_at"}


def _apply_note_filters(stmt, q: Optional[str]):
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))
    return stmt


def _apply_note_sort(stmt, sort: str):
    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if sort_field in ALLOWED_SORT_FIELDS:
        return stmt.order_by(order_fn(getattr(Note, sort_field)))
    return stmt.order_by(desc(Note.created_at))


@router.get("/", response_model=PaginatedNotes)
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> PaginatedNotes:
    base_stmt = _apply_note_filters(select(Note), q)
    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    rows = (
        db.execute(_apply_note_sort(base_stmt, sort).offset(skip).limit(limit)).scalars().all()
    )
    return PaginatedNotes(
        items=[NoteRead.model_validate(row) for row in rows],
        meta=PaginatedMeta(total=total, skip=skip, limit=limit),
    )


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title.strip(), content=payload.content.strip())
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    if payload.title is None and payload.content is None:
        raise HTTPException(status_code=400, detail="At least one field must be provided")

    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title.strip()
    if payload.content is not None:
        note.content = payload.content.strip()
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204, response_class=Response)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()
    return Response(status_code=204)


@router.put("/{note_id}/tags", response_model=list[str])
def set_note_tags(note_id: int, payload: NoteTagUpdate, db: Session = Depends(get_db)) -> list[str]:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if payload.tag_ids:
        tags = db.execute(select(Tag).where(Tag.id.in_(payload.tag_ids))).scalars().all()
        if len(tags) != len(set(payload.tag_ids)):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        note.tags = tags
    else:
        note.tags = []
    db.add(note)
    db.flush()
    db.refresh(note)
    return [tag.name for tag in note.tags]
