from flask import Flask, request, render_template, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect("reservations.db") as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timeslot TEXT NOT NULL UNIQUE
        )''')


@app.route('/')
def index():
    with sqlite3.connect("reservations.db") as conn:
        cursor = conn.cursor()
        slots = [f"{h:02}:00" for h in range(24)]  # 00:00 to 23:00
        booked = {row[0] for row in cursor.execute("SELECT timeslot FROM reservations")}
        reservations = [
            {"username": row[0], "timeslot": row[1]}
            for row in cursor.execute("SELECT username, timeslot FROM reservations ORDER BY timeslot")
        ]
    return render_template('index.html', slots=slots, booked=booked, reservations=reservations)



@app.route('/reserve', methods=['POST'])
def reserve():
    username = request.form['username']
    timeslot = request.form['timeslot']
    try:
        with sqlite3.connect("reservations.db") as conn:
            conn.execute("INSERT INTO reservations (username, timeslot) VALUES (?, ?)", (username, timeslot))
    except sqlite3.IntegrityError:
        return "Slot already reserved!", 409
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
