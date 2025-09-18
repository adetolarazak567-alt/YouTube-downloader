from flask import Flask, jsonify
import sqlite3
from threading import Lock

app = Flask(__name__)
lock = Lock()  # Thread-safe increment

DB_FILE = "counters.db"

# Initialize database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                id INTEGER PRIMARY KEY,
                page_views INTEGER NOT NULL,
                downloads INTEGER NOT NULL
            )
        """)
        # Ensure there is 1 row
        c.execute("SELECT COUNT(*) FROM counters")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO counters (page_views, downloads) VALUES (0,0)")
        conn.commit()

init_db()

# Helper to get counters
def get_counters():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT page_views, downloads FROM counters WHERE id=1")
        row = c.fetchone()
        return {"pageViews": row[0], "downloads": row[1]}

# API endpoints
@app.route("/api/counts", methods=["GET"])
def counts():
    return jsonify(get_counters())

@app.route("/api/incrementPageView", methods=["POST"])
def increment_page_view():
    with lock:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("UPDATE counters SET page_views = page_views + 1 WHERE id=1")
            conn.commit()
    return jsonify(get_counters())

@app.route("/api/incrementDownload", methods=["POST"])
def increment_download():
    with lock:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("UPDATE counters SET downloads = downloads + 1 WHERE id=1")
            conn.commit()
    return jsonify(get_counters())

@app.route("/api/resetCounts", methods=["POST"])
def reset_counts():
    with lock:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("UPDATE counters SET page_views=0, downloads=0 WHERE id=1")
            conn.commit()
    return jsonify(get_counters())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
