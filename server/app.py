from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
logger.debug("Flask app initialized")

# Load datasets
logger.debug("Loading workouts.json")
with open('workouts.json', 'r') as f:
    workouts = json.load(f)
logger.debug(f"Loaded {len(workouts)} workouts")

logger.debug("Loading meals.json")
with open('meals.json', 'r') as f:
    meals = json.load(f)
logger.debug(f"Loaded {len(meals)} meals")

def get_db_connection():
    conn = sqlite3.connect('data.sqlite', timeout=30)  # Increased timeout
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    logger.debug("Initializing database")
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS users')
        c.execute('DROP TABLE IF EXISTS weekly_plan')
        c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY, age TEXT, weight TEXT, height TEXT,
                      gender TEXT, diet TEXT, goal TEXT, work_start TEXT,
                      work_end TEXT, lunch_time TEXT)''')
        c.execute('''CREATE TABLE weekly_plan
                     (user_id INTEGER, day INTEGER, schedule TEXT,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
    logger.debug("Database initialized")

init_db()

def calculate_bmi(weight, height):
    weight = float(weight) if weight else 70
    height = float(height) / 100 if height else 1.7
    return weight / (height ** 2)

def parse_time(time_str):
    return datetime.strptime(time_str, '%I:%M %p') if time_str else datetime.strptime('9:00 AM', '%I:%M %p')

def recommend(user_data, items, item_type, day_of_week, used_workouts):
    logger.debug(f"Recommending {item_type} for day {day_of_week}")
    goal = user_data.get('goal', 'fitness').lower()
    gender = user_data.get('gender', 'male').lower()
    diet = user_data.get('diet', 'non-vegetarian').lower()
    age = float(user_data.get('age', '30'))
    bmi = calculate_bmi(user_data.get('weight', '70'), user_data.get('height', '170'))
    work_start = parse_time(user_data.get('work_start', '9:00 AM'))
    work_end = parse_time(user_data.get('work_end', '10:00 PM'))
    work_duration = (work_end - work_start).seconds / 3600

    weekly_split = {0: 'push', 1: 'pull', 2: 'legs', 3: 'rest', 4: 'push', 5: 'pull', 6: 'legs'}
    target_split = weekly_split.get(day_of_week, 'rest')
    if target_split == 'rest' and item_type == 'workout':
        return []

    user_vector = [
        1 if goal == 'fitness' else 0.5,
        min(bmi / 30, 1.0) if bmi < 30 else 0.5,
        1 - (work_duration / 12) if work_duration < 12 else 0.3,
        1 - (age / 50) if age <= 50 else 0.4,
        1 if gender == 'male' else 0.9,
        1 if diet == 'vegetarian' else 0.8,
        0.8 if bmi > 25 else 1.0,
        1.0 if age < 35 else 0.7,
        1.0 if goal == 'fitness' and bmi < 25 else 0.6
    ]

    item_vectors = []
    for item in items:
        goal_score = bmi_score = duration_score = age_score = gender_score = diet_score = intensity_score = split_score = volume_score = 0
        if item_type == 'workout':
            if goal == 'fitness' and item['type'] in ['strength', 'bodyweight']:
                goal_score = 1.3 if item['intensity'] == 'high' else 1.0
            bmi_score = 1.0 if bmi < 25 and item['calories_burned'] > 150 else 0.7
            duration = item.get('duration_minutes', 20)
            duration_score = 1.0 if duration <= 30 and work_duration > 8 else 0.6
            age_score = 1.0 if age < 40 and item['intensity'] != 'high' else 0.5
            gender_score = 1.0 if gender == 'male' and item['muscle_group'] in ['chest', 'back', 'legs'] else 0.9
            intensity_score = 1.0 if item['intensity'] == 'medium' and bmi > 25 else 0.8
            split_score = 2.0 if target_split == item['split'] else 0.05
            volume_score = 1.0 if item['sets'] >= 3 else 0.7
            if item['id'] in used_workouts:
                split_score *= 0.01
        elif item_type == 'meal':
            if goal == 'fitness' and item['protein'] >= 15:
                goal_score = 1.3 if item['protein'] >= 25 else 1.0
            bmi_score = 1.0 if bmi < 25 or item['calories'] < 600 else 0.6
            prep_time = item.get('prep_time_minutes', 30)
            duration_score = 1.0 if prep_time <= 20 and work_duration > 8 else 0.7
            age_score = 1.0 if age < 40 else 0.8
            gender_score = 1.0 if gender == 'male' and item['protein'] > 20 else 0.9
            diet_score = 2.0 if item['type'] == diet else 0.0
            intensity_score = 1.0
            split_score = 1.0
            volume_score = 1.0
        item_vectors.append([goal_score, bmi_score, duration_score, age_score, gender_score, diet_score, intensity_score, split_score, volume_score])

    if not item_vectors:
        return []
    similarities = cosine_similarity([user_vector], item_vectors)[0]
    ranked = sorted(zip(similarities, items), key=lambda x: x[0], reverse=True)[:3]
    return [item for _, item in ranked]

def create_schedule(user_data, workouts, meals):
    work_start = parse_time(user_data.get('work_start', '9:00 AM'))
    work_end = parse_time(user_data.get('work_end', '10:00 PM'))
    lunch_time = parse_time(user_data.get('lunch_time', '1:00 PM'))
    work_hours = []
    current = work_start
    while current < work_end:
        work_hours.append(current.hour)
        current += timedelta(hours=1)

    meal_plan = [
        {"time": "7:00 AM", "calories": 350, "protein": 10, "carbs": 50, "fat": 10, "meal_type": "breakfast", "purpose": "High-carb for energy"},
        {"time": lunch_time.strftime('%I:%M %p'), "calories": 600, "protein": 30, "carbs": 70, "fat": 20, "meal_type": "lunch", "purpose": "High-protein for recovery"},
        {"time": "8:00 PM", "calories": 600, "protein": 30, "carbs": 70, "fat": 20, "meal_type": "dinner", "purpose": "High-protein for recovery"}
    ]

    daily_schedule = {}
    for meal in meal_plan:
        time = meal['time']
        target_calories = meal['calories']
        target_protein = meal['protein']
        target_carbs = meal['carbs']
        target_fat = meal['fat']
        meal_type = meal['meal_type']
        purpose = meal['purpose']
        suitable_meals = [m for m in meals if m.get('meal_type') == meal_type and 
                         m.get('type') == user_data.get('diet', 'non-vegetarian').lower() and 
                         'purpose' in m and
                         abs(m['calories'] - target_calories) <= 150 and 
                         abs(m['protein'] - target_protein) <= 15 and 
                         abs(m['carbs'] - target_carbs) <= 30]
        if not suitable_meals:
            suitable_meals = [m for m in meals if m.get('meal_type') == meal_type and 
                             m.get('type') == user_data.get('diet', 'non-vegetarian').lower() and 
                             'purpose' in m]
        if not suitable_meals:
            suitable_meals = [m for m in meals if m.get('meal_type') in ['main course', 'breakfast', 'snack'] and 
                             'purpose' in m]
        selected_meal = suitable_meals[0] if suitable_meals else meals[0]
        daily_schedule[time] = {
            "type": "meal",
            "name": selected_meal['name'],
            "calories": selected_meal['calories'],
            "protein": selected_meal['protein'],
            "carbs": selected_meal['carbs'],
            "fat": selected_meal['fat'],
            "purpose": selected_meal.get('purpose', purpose)
        }

    if workouts:
        workout_time = (work_end + timedelta(hours=1)).strftime('%I:%M %p')
        workout_end = (work_end + timedelta(hours=2, minutes=30)).strftime('%I:%M %p')
        warmup = "5 min dynamic stretches (leg swings, arm circles)"
        detailed_workouts = [
            {
                **w,
                "instructions": f"Use 70-80% 1RM, rest {90 if w['intensity'] == 'high' else 60}s."
            } for w in workouts
        ]
        daily_schedule[f"{workout_time}-{workout_end}"] = {
            "type": "workout",
            "name": f"{workouts[0]['split'].capitalize()} Day",
            "details": detailed_workouts,
            "warmup": warmup
        }

    return daily_schedule

@app.route('/submit', methods=['POST'])
def submit():
    logger.debug("Received /submit request")
    user_data = request.json
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO users (age, weight, height, gender, diet, goal, work_start, work_end, lunch_time)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_data.get('age'), user_data.get('weight'), user_data.get('height'),
                   user_data.get('gender'), user_data.get('diet'), user_data.get('goal'),
                   user_data.get('work_start'), user_data.get('work_end'), user_data.get('lunch_time')))
        user_id = c.lastrowid

        week_start = datetime.now()
        weekly_schedule = {}
        used_workouts = set()
        for day in range(7):
            current_day = (week_start + timedelta(days=day)).weekday()
            selected_workouts = recommend(user_data, workouts, 'workout', current_day, used_workouts)
            for w in selected_workouts:
                used_workouts.add(w['id'])
            selected_meals = recommend(user_data, meals, 'meal', current_day, used_workouts)
            daily_schedule = create_schedule(user_data, selected_workouts, selected_meals)
            weekly_schedule[day] = daily_schedule
            c.execute('INSERT INTO weekly_plan (user_id, day, schedule) VALUES (?, ?, ?)',
                      (user_id, day, json.dumps(daily_schedule)))
        conn.commit()
    logger.debug(f"Stored schedule for user_id {user_id}")
    return jsonify({'schedule': weekly_schedule[0]})

if __name__ == '__main__':
    logger.debug("Starting Flask server")
    app.run(host='127.0.0.1', port=5000, debug=False)  # Disable debug to prevent multiple instances