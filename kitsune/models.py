from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


class Message(BaseModel):
    id: int
    session_id: int
    content: str
    created_at: str


class Session(BaseModel):
    id: int
    created_at: str
    updated_at: str


@dataclass
class MemoryStore:
    pass


@dataclass
class Deps:
    memory: MemoryStore
