import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "app.db"


def main() -> None:
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO products (title, price, count) VALUES (?, ?, ?)",
        ("Keyboard", 2499.0, 5),
    )
    cursor.execute(
        "INSERT INTO products (title, price, count) VALUES (?, ?, ?)",
        ("Mouse", 1499.0, 8),
    )
    connection.commit()
    connection.close()
    print("Inserted 2 products into the initial schema.")


if __name__ == "__main__":
    main()
