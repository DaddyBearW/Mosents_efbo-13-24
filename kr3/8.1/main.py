from fastapi import FastAPI
from pydantic import BaseModel

from database import get_db_connection, init_db


app = FastAPI(title="Task 8.1")
init_db()


class User(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(user: User) -> dict[str, str]:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, user.password),
    )
    connection.commit()
    connection.close()
    return {"message": "User registered successfully!"}
