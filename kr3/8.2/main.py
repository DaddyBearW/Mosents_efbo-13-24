from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from database import get_db_connection, init_db


app = FastAPI(title="Task 8.2")
init_db()


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool


def get_todo_by_id(todo_id: int) -> dict[str, object] | None:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, title, description, completed FROM todos WHERE id = ?",
        (todo_id,),
    )
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "completed": bool(row[3]),
    }


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate) -> dict[str, object]:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, 0),
    )
    todo_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return get_todo_by_id(todo_id)


@app.get("/todos/{todo_id}")
def read_todo(todo_id: int) -> dict[str, object]:
    todo = get_todo_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate) -> dict[str, object]:
    if get_todo_by_id(todo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, int(todo.completed), todo_id),
    )
    connection.commit()
    connection.close()
    return get_todo_by_id(todo_id)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int) -> dict[str, str]:
    if get_todo_by_id(todo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    connection.commit()
    connection.close()
    return {"message": "Todo deleted successfully!"}
