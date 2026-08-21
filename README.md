# Flashcards

A spaced repetition study tool built with Flask and SQLite. Cards you struggle with come back sooner; cards you know well get pushed further out.

## Why I built this

A side project to test myself on course vocabulary. I wanted something that would resurface terms right before I'd forget them, instead of drilling the whole deck every time.

## How the scheduling works

Implements the SM-2 algorithm. Each card carries two values:

- **interval** — days until the next review
- **ease** — a multiplier starting at 2.5 that tracks how well you know this card

After each review the interval is recalculated:

| Rating | Effect |
|---|---|
| Again | Interval resets to 1 day, ease drops 0.2 |
| Hard | Interval grows 1.2x, ease drops 0.15 |
| Good | Interval multiplied by ease — 1 to 3 to 8 to 20 days |
| Easy | Interval grows faster, ease increases 0.15 |

Ease is floored at 1.3 so a difficult card can't spiral into permanent daily repetition.

## Architecture

    app.py          Flask routes and request handling
    db.py           Database access layer — all SQL lives here
    scheduler.py    SM-2 implementation, pure functions, no I/O
    schema.sql      Table definitions
    templates/      Jinja2 views

Database access is isolated in `db.py` and scheduling logic in `scheduler.py`, so the algorithm can be tested without a database and routes never write SQL directly. All queries are parameterized against injection.

## Deployment

Deployed on Render with PostgreSQL. Originally built on SQLite, which worked locally but lost data on every service restart — the free tier uses ephemeral disk, so file-based storage doesn't survive a redeploy. Migrated to Postgres, with the connection string supplied through an environment variable so credentials stay out of the repo.

## Running locally

    pip install -r requirements.txt
    python db.py
    python app.py

Then open http://127.0.0.1:5000

## Stack

Python, Flask, SQLite, Jinja2, HTML/CSS, JavaScript