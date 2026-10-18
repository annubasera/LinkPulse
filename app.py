from flask import Flask, request, redirect, render_template_string
import sqlite3
import random
import string

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("links.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT UNIQUE,
        original_url TEXT,
        clicks INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def make_code():
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))

PAGE = """
<h1>LinkPulse</h1>
<form method="POST">
    <input type="text" name="url" placeholder="Long URL yahan daalo" size="50" required>
    <button type="submit">Shorten URL</button>
</form>
{% if short %}
    <p>Short link: <a href="{{ short }}">{{ short }}</a></p>
{% endif %}
<h3>Analytics</h3>
<table border="1" cellpadding="6">
    <tr><th>Short</th><th>Original</th><th>Clicks</th></tr>
    {% for l in links %}
    <tr>
        <td>{{ l['short_code'] }}</td>
        <td>{{ l['original_url'] }}</td>
        <td>{{ l['clicks'] }}</td>
    </tr>
    {% endfor %}
</table>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    short = None
    conn = get_db()
    if request.method == "POST":
        url = request.form["url"]
        if not url.startswith("http"):
            url = "https://" + url
        code = make_code()
        conn.execute("INSERT INTO links (short_code, original_url) VALUES (?, ?)", (code, url))
        conn.commit()
        short = request.host_url + code
    links = conn.execute("SELECT * FROM links ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(PAGE, short=short, links=links)

@app.route("/<code>")
def go(code):
    conn = get_db()
    row = conn.execute("SELECT * FROM links WHERE short_code = ?", (code,)).fetchone()
    if row is None:
        conn.close()
        return "Link nahi mila", 404
    conn.execute("UPDATE links SET clicks = clicks + 1 WHERE short_code = ?", (code,))
    conn.commit()
    conn.close()
    return redirect(row["original_url"])
init_db()
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
