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
    ranked = sorted(zip(similarities, items), key=lambda x: x[0], reverse=True)[:2]
    return [item for _, item in ranked]

def create_schedule(user_data, workouts, meals):
    schedule = user_data.get('schedule', '').lower()
    # Parse work hours (e.g., "9am-5pm")
    work_hours = []
    if schedule:
        try:
            start, end = schedule.split('-')
            start_hour = int(start.replace('am', '').replace('pm', '').strip())
            end_hour = int(end.replace('am', '').replace('pm', '').strip())
            if 'pm' in end.lower() and end_hour < 12:
                end_hour += 12
            if 'pm' in start.lower() and start_hour < 12:
                start_hour += 12
            work_hours = list(range(start_hour, end_hour + 1))
        except:
            work_hours = []
    # Simple schedule: breakfast, lunch, dinner, one workout
    daily_schedule = {
        "7:00 AM": {"type": "meal", "name": meals[0]['name'] if meals else "Breakfast"},
        "12:00 PM": {"type": "meal", "name": meals[1]['name'] if len(meals) > 1 else "Lunch"},
        "7:00 PM": {"type": "meal", "name": meals[0]['name'] if meals else "Dinner"},
        "6:00 PM": {"type": "workout", "name": workouts[0]['name'] if workouts else "Workout"}
    }
    # Adjust workout time if it conflicts with work hours
    if work_hours:
        workout_time = "6:00 PM"
        workout_hour = 18  # 6:00 PM in 24-hour format
        if workout_hour in work_hours:
            # Move workout to after work
            new_hour = max(work_hours) + 1
            if new_hour > 23:
                new_hour = min(work_hours) - 1 if min(work_hours) > 6 else 21
            new_time = f"{new_hour % 12 or 12}:00 {'AM' if new_hour < 12 else 'PM'}"
            daily_schedule[new_time] = daily_schedule.pop(workout_time)
    return daily_schedule

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
    daily_schedule = create_schedule(data, recommended_workouts, recommended_meals)
    print(f"Received and saved: {data}")
    return jsonify({
        "message": "Data saved",
        "data": data,
        "workouts": recommended_workouts,
        "meals": recommended_meals,
        "schedule": daily_schedule
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)