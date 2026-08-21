import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
import db
import scheduler

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
db.init_db()

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.email = row["email"]

@login_manager.user_loader
def load_user(user_id):
    row = db.get_user(int(user_id))
    return User(row) if row else None

# ---------- auth ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not email or len(password) < 8:
            flash("Enter an email and a password of at least 8 characters.")
            return redirect(url_for("signup"))

        if db.get_user_by_email(email):
            flash("An account with that email already exists.")
            return redirect(url_for("signup"))

        user_id = db.create_user(email, generate_password_hash(password))
        login_user(User({"id": user_id, "email": email}))
        return redirect(url_for("home"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        row = db.get_user_by_email(email)

        if not row or not check_password_hash(row["password_hash"], request.form["password"]):
            flash("Email or password is incorrect.")
            return redirect(url_for("login"))

        login_user(User(row))
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------- decks ----------

@app.route("/")
@login_required
def home():
    decks = db.get_decks_with_counts(current_user.id)
    return render_template("index.html", decks=decks)

@app.route("/decks/new", methods=["POST"])
@login_required
def new_deck():
    name = request.form["name"]
    if name.strip():
        db.create_deck(current_user.id, name)
    return redirect(url_for("home"))

@app.route("/decks/<int:deck_id>")
@login_required
def deck_page(deck_id):
    deck = db.get_deck(deck_id, current_user.id)
    if not deck:
        return redirect(url_for("home"))
    cards = db.get_cards(deck_id)
    return render_template("deck.html", deck=deck, cards=cards)

@app.route("/decks/<int:deck_id>/delete", methods=["POST"])
@login_required
def remove_deck(deck_id):
    db.delete_deck(deck_id, current_user.id)
    return redirect(url_for("home"))

# ---------- cards ----------

@app.route("/decks/<int:deck_id>/cards/new", methods=["POST"])
@login_required
def new_card(deck_id):
    if not db.get_deck(deck_id, current_user.id):
        return redirect(url_for("home"))
    front = request.form["front"]
    back = request.form["back"]
    if front.strip() and back.strip():
        db.create_card(deck_id, front, back)
    return redirect(url_for("deck_page", deck_id=deck_id))

@app.route("/cards/<int:card_id>/delete", methods=["POST"])
@login_required
def remove_card(card_id):
    card = db.get_card(card_id, current_user.id)
    if not card:
        return redirect(url_for("home"))
    db.delete_card(card_id)
    return redirect(url_for("deck_page", deck_id=card["deck_id"]))

# ---------- review ----------

@app.route("/decks/<int:deck_id>/review")
@login_required
def review(deck_id):
    deck = db.get_deck(deck_id, current_user.id)
    if not deck:
        return redirect(url_for("home"))
    cards = db.get_due_cards(deck_id)
    if not cards:
        return render_template("done.html", deck=deck)
    return render_template("review.html", deck=deck, card=cards[0])

@app.route("/cards/<int:card_id>/rate", methods=["POST"])
@login_required
def rate_card(card_id):
    card = db.get_card(card_id, current_user.id)
    if not card:
        return redirect(url_for("home"))

    rating = int(request.form["rating"])
    new_interval, new_ease = scheduler.schedule(rating, card["interval_days"], card["ease"])
    next_due = date.today() + timedelta(days=new_interval)

    db.update_card_schedule(card_id, new_interval, new_ease, next_due)
    return redirect(url_for("review", deck_id=card["deck_id"]))

# ---------- practice ----------

@app.route("/decks/<int:deck_id>/practice/<int:index>")
@login_required
def practice(deck_id, index):
    deck = db.get_deck(deck_id, current_user.id)
    if not deck:
        return redirect(url_for("home"))
    cards = db.get_cards(deck_id)
    if not cards or index >= len(cards):
        return render_template("practice_done.html", deck=deck, total=len(cards))
    return render_template(
        "practice.html", deck=deck, card=cards[index], index=index, total=len(cards)
    )

if __name__ == "__main__":
    app.run(debug=True)