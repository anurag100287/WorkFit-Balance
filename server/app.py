from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data.sqlite')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    age TEXT,
                    weight TEXT,
                    height TEXT,
                    gender TEXT,
                    goal TEXT,
                    schedule TEXT
                    )''')
        conn.commit()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO users (age, weight, height, gender, goal, schedule)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                  (data.get('age'), data.get('weight'), data.get('height'),
                   data.get('gender'), data.get('goal'), data.get('schedule')))
        conn.commit()
    print(f"Received and saved: {data}")
    return jsonify({"message": "Data saved", "data": data})

if __name__ == '__main__':
    init_db()  # Create database and table on startup
    app.run(debug=True, host='0.0.0.0', port=5000)