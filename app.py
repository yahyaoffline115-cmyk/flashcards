from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta
import db
import scheduler

app = Flask(__name__)
db.init_db()

@app.route("/")
def home():
    decks = db.get_decks()
    return render_template("index.html", decks=decks)

@app.route("/decks/new", methods=["POST"])
def new_deck():
    name = request.form["name"]
    if name.strip():
        db.create_deck(name)
    return redirect(url_for("home"))

@app.route("/decks/<int:deck_id>")
def deck_page(deck_id):
    deck = db.get_deck(deck_id)
    cards = db.get_cards(deck_id)
    return render_template("deck.html", deck=deck, cards=cards)

@app.route("/decks/<int:deck_id>/cards/new", methods=["POST"])
def new_card(deck_id):
    front = request.form["front"]
    back = request.form["back"]
    if front.strip() and back.strip():
        db.create_card(deck_id, front, back)
    return redirect(url_for("deck_page", deck_id=deck_id))

@app.route("/decks/<int:deck_id>/review")
def review(deck_id):
    deck = db.get_deck(deck_id)
    cards = db.get_due_cards(deck_id)
    if not cards:
        return render_template("done.html", deck=deck)
    return render_template("review.html", deck=deck, card=cards[0])

@app.route("/cards/<int:card_id>/rate", methods=["POST"])
def rate_card(card_id):
    rating = int(request.form["rating"])
    card = db.get_card(card_id)

    new_interval, new_ease = scheduler.schedule(rating, card["interval"], card["ease"])
    next_due = (date.today() + timedelta(days=new_interval)).isoformat()

    db.update_card_schedule(card_id, new_interval, new_ease, next_due)
    return redirect(url_for("review", deck_id=card["deck_id"]))

if __name__ == "__main__":
    app.run(debug=True)