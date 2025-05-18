from flask import Flask, request, jsonify
import sqlite3
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data.sqlite')
WORKOUTS_PATH = os.path.join(os.path.dirname(__file__), 'workouts.json')
MEALS_PATH = os.path.join(os.path.dirname(__file__), 'meals.json')

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

def load_datasets():
    with open(WORKOUTS_PATH, 'r') as f:
        workouts = json.load(f)
    with open(MEALS_PATH, 'r') as f:
        meals = json.load(f)
    return workouts, meals

def recommend(user_data, items, item_type):
    # Simple feature vector: goal-based scoring
    goal = user_data.get('goal', '').lower()
    user_vector = [1 if goal in ['weight loss', 'muscle gain'] else 0]
    item_vectors = []
    for item in items:
        score = 0
        if item_type == 'workout':
            if goal == 'weight loss' and item['type'] == 'bodyweight':
                score = 1
            elif goal == 'muscle gain' and item['type'] == 'strength':
                score = 1
        elif item_type == 'meal':
            if goal == 'weight loss' and item['calories'] < 500:
                score = 1
            elif goal == 'muscle gain' and item['protein'] > 20:
                score = 1
        item_vectors.append([score])
    if not item_vectors:
        return []
    similarities = cosine_similarity([user_vector], item_vectors)[0]
    # Sort by similarity score
    ranked = sorted(zip(similarities, items), key=lambda x: x[0], reverse=True)[:2]
    return [item for _, item in ranked]

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
    workouts, meals = load_datasets()
    recommended_workouts = recommend(data, workouts, 'workout')
    recommended_meals = recommend(data, meals, 'meal')
    print(f"Received and saved: {data}")
    return jsonify({
        "message": "Data saved",
        "data": data,
        "workouts": recommended_workouts,
        "meals": recommended_meals
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)