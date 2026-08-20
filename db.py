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

def get_due_cards(deck_id):
    from datetime import date
    today = date.today().isoformat()
    conn = get_connection()
    cards = conn.execute(
        "SELECT * FROM cards WHERE deck_id = ? AND due_date <= ? ORDER BY due_date",
        (deck_id, today)
    ).fetchall()
    conn.close()
    return cards

def get_card(card_id):
    conn = get_connection()
    card = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    conn.close()
    return card

def update_card_schedule(card_id, interval, ease, due_date):
    conn = get_connection()
    conn.execute(
        "UPDATE cards SET interval = ?, ease = ?, due_date = ? WHERE id = ?",
        (interval, ease, due_date, card_id)
    )
    conn.commit()
    conn.close()

def delete_deck(deck_id):
    conn = get_connection()
    conn.execute("DELETE FROM cards WHERE deck_id = ?", (deck_id,))
    conn.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
    conn.commit()
    conn.close()

def delete_card(card_id):
    conn = get_connection()
    conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()

def get_decks_with_counts():
    from datetime import date
    today = date.today().isoformat()
    conn = get_connection()
    decks = conn.execute("""
        SELECT d.id, d.name,
               COUNT(c.id) AS total,
               SUM(CASE WHEN c.due_date <= ? THEN 1 ELSE 0 END) AS due
        FROM decks d
        LEFT JOIN cards c ON c.deck_id = d.id
        GROUP BY d.id, d.name
        ORDER BY d.name
    """, (today,)).fetchall()
    conn.close()
    return decks

if __name__ == "__main__":
    init_db()
    print("Database initialized")