from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10_000)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=10_000)

    @field_validator("title", "content", mode="before")
    @classmethod
    def reject_empty_strings(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            raise ValueError("must not be empty")
        return value


class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=5_000)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=5_000)
    completed: bool | None = None

    @field_validator("description", mode="before")
    @classmethod
    def reject_empty_description(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            raise ValueError("must not be empty")
        return value


class PaginatedMeta(BaseModel):
    total: int
    skip: int
    limit: int


class PaginatedNotes(BaseModel):
    items: list[NoteRead]
    meta: PaginatedMeta


class PaginatedActionItems(BaseModel):
    items: list[ActionItemRead]
    meta: PaginatedMeta


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50_000)


class ExtractedActionItem(BaseModel):
    text: str
    priority: str | None = None
    assignee: str | None = None
    due_date: str | None = None


class ExtractResponse(BaseModel):
    items: list[ExtractedActionItem]
