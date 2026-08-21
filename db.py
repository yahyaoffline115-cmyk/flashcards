import os
import psycopg
from psycopg.rows import dict_row
from datetime import date

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

def init_db():
    with get_connection() as conn:
        with open("schema.sql") as f:
            conn.execute(f.read())
        conn.commit()

def create_deck(name):
    with get_connection() as conn:
        conn.execute("INSERT INTO decks (name) VALUES (%s)", (name,))
        conn.commit()

def get_decks():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM decks ORDER BY name").fetchall()

def get_decks_with_counts():
    today = date.today()
    with get_connection() as conn:
        return conn.execute("""
            SELECT d.id, d.name,
                   COUNT(c.id) AS total,
                   COUNT(CASE WHEN c.due_date <= %s THEN 1 END) AS due
            FROM decks d
            LEFT JOIN cards c ON c.deck_id = d.id
            GROUP BY d.id, d.name
            ORDER BY d.name
        """, (today,)).fetchall()

def get_deck(deck_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM decks WHERE id = %s", (deck_id,)).fetchone()

def delete_deck(deck_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM decks WHERE id = %s", (deck_id,))
        conn.commit()

def get_cards(deck_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM cards WHERE deck_id = %s ORDER BY id", (deck_id,)).fetchall()

def get_card(card_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM cards WHERE id = %s", (card_id,)).fetchone()

def create_card(deck_id, front, back):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO cards (deck_id, front, back, due_date) VALUES (%s, %s, %s, %s)",
            (deck_id, front, back, date.today())
        )
        conn.commit()

def delete_card(card_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM cards WHERE id = %s", (card_id,))
        conn.commit()

def get_due_cards(deck_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM cards WHERE deck_id = %s AND due_date <= %s ORDER BY due_date",
            (deck_id, date.today())
        ).fetchall()

def update_card_schedule(card_id, interval_days, ease, due_date):
    with get_connection() as conn:
        conn.execute(
            "UPDATE cards SET interval_days = %s, ease = %s, due_date = %s WHERE id = %s",
            (interval_days, ease, due_date, card_id)
        )
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized")