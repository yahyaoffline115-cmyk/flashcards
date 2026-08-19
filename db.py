import sqlite3

DATABASE = "flashcards.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with open("schema.sql") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def create_deck(name):
    conn = get_connection()
    conn.execute("INSERT INTO decks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_decks():
    conn = get_connection()
    decks = conn.execute("SELECT * FROM decks ORDER BY name").fetchall()
    conn.close()
    return decks

def get_deck(deck_id):
    conn = get_connection()
    deck = conn.execute("SELECT * FROM decks WHERE id = ?", (deck_id,)).fetchone()
    conn.close()
    return deck

def get_cards(deck_id):
    conn = get_connection()
    cards = conn.execute("SELECT * FROM cards WHERE deck_id = ?", (deck_id,)).fetchall()
    conn.close()
    return cards

def create_card(deck_id, front, back):
    from datetime import date
    today = date.today().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO cards (deck_id, front, back, due_date) VALUES (?, ?, ?, ?)",
        (deck_id, front, back, today)
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized")