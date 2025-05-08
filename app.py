from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import date
import sqlite3
import os

app = Flask(__name__)
CORS(app)

db_path = 'habits.db'  # <-- Define database path

def init_db():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()

        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Create habits table (linked to user)
        c.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        # Create completions table (linked to user + habit)
        c.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                habit_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(habit_id) REFERENCES habits(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()


@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            user_id = c.lastrowid
            return jsonify({'user_id': user_id})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
        row = c.fetchone()
        if row:
            return jsonify({'user_id': row[0], 'username': row[1]})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/habits', methods=['POST'])
def add_habit():
    data = request.get_json()
    name = data['name']
    user_id = data['user_id']

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO habits (user_id, name) VALUES (?, ?)', (user_id, name))
        habit_id = c.lastrowid
        conn.commit()
    return jsonify({ 'id': habit_id, 'name': name })


@app.route('/habits', methods=['GET'])
def get_habits():
    user_id = int(request.args.get('user_id'))
    today = date.today().isoformat()

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT h.id, h.name,
                   EXISTS (
                       SELECT 1 FROM completions
                       WHERE habit_id = h.id AND user_id = ? AND date = ?
                   ) AS is_done
            FROM habits h
            WHERE h.user_id = ?
        ''', (user_id, today, user_id))
        rows = c.fetchall()
        habits = [{'id': row[0], 'name': row[1], 'done': bool(row[2])} for row in rows]
    return jsonify(habits)


@app.route('/complete/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    data = request.get_json()
    user_id = data['user_id']
    today = date.today().isoformat()

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO completions (user_id, habit_id, date)
            VALUES (?, ?, ?)
        ''', (user_id, habit_id, today))
        conn.commit()
    return jsonify({'status': 'ok'})

@app.route('/goals', methods=['POST'])
def add_goal():
    data = request.get_json()
    user_id = data['user_id']
    description = data['description']

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO goals (user_id, description) VALUES (?, ?)', (user_id, description))
        goal_id = c.lastrowid
        conn.commit()

    return jsonify({'id': goal_id, 'description': description})

@app.route('/goals', methods=['GET'])
def get_goals():
    user_id = int(request.args.get('user_id'))

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT id, description FROM goals WHERE user_id = ?', (user_id,))
        rows = c.fetchall()
        goals = [{'id': row[0], 'description': row[1]} for row in rows]

    return jsonify(goals)




if __name__ == '__main__':
    if not os.path.exists(db_path):
        init_db()
    app.run(debug=True, port=3000)
