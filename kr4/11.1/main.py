from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


app = FastAPI(title="Task 11.1")

notes_db: dict[int, dict[str, object]] = {}
note_id_seq = count(start=1)


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=500)


class NoteUpdate(BaseModel):
    done: bool


def reset_state() -> None:
    global note_id_seq
    notes_db.clear()
    note_id_seq = count(start=1)


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteCreate) -> dict[str, object]:
    note_id = next(note_id_seq)
    notes_db[note_id] = {
        "title": note.title,
        "content": note.content,
        "done": False,
    }
    return {"id": note_id, **notes_db[note_id]}


@app.get("/notes/{note_id}")
def get_note(note_id: int) -> dict[str, object]:
    note = notes_db.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": note_id, **note}


@app.patch("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate) -> dict[str, object]:
    note = notes_db.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note["done"] = payload.done
    return {"id": note_id, **note}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int) -> dict[str, str]:
    if notes_db.pop(note_id, None) is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}
