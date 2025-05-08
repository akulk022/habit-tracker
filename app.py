from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

db_path = 'habits.db'  # <-- Define database path

def init_db():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/habits', methods=['POST'])
def add_habit():
    data = request.get_json()
    name = data['name']
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO habits (name) VALUES (?)', (name,))
        habit_id = c.lastrowid
        conn.commit()
    return jsonify({ 'id': habit_id, 'name': name })

@app.route('/habits', methods=['GET'])
def get_habits():
    print("Fetching habits from DB...")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name FROM habits')
        rows = c.fetchall()
        print("Got rows:", rows)
        habits = [{'id': row[0], 'name': row[1]} for row in rows]
    return jsonify(habits)


if __name__ == '__main__':
    if not os.path.exists(db_path):
        init_db()
    app.run(debug=True, port=3000)
