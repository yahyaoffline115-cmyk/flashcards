from flask import Flask, render_template, request, redirect, url_for
import db

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)