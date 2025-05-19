import json
import random

# Workout attributes
workout_templates = [
    {"name": "Bench Press", "type": "strength", "muscle_group": "chest", "split": "push", "equipment": "barbell", "calories_burned": 200, "duration_minutes": 20, "sets": 3, "reps": "8-12", "intensity": "high", "instructions": "Lie on bench, grip barbell, lower to chest, press up.", "youtube_link": "https://www.youtube.com/watch?v=rT7DgCr-3_M"},
    {"name": "Pull-Ups", "type": "bodyweight", "muscle_group": "back", "split": "pull", "equipment": "pull-up bar", "calories_burned": 180, "duration_minutes": 15, "sets": 3, "reps": "6-10", "intensity": "high", "instructions": "Hang from bar, pull up until chin above bar.", "youtube_link": "https://www.youtube.com/watch?v=eGo4IYlbE5g"},
    {"name": "Squats", "type": "strength", "muscle_group": "legs", "split": "legs", "equipment": "barbell", "calories_burned": 250, "duration_minutes": 20, "sets": 3, "reps": "8-12", "intensity": "high", "instructions": "Stand with bar on shoulders, squat to knee level.", "youtube_link": "https://www.youtube.com/watch?v=Dy28eq2PjcY"},
    # Add more templates for variety (covering push/pull/legs)
    {"name": "Incline Press", "type": "strength", "muscle_group": "chest", "split": "push", "equipment": "dumbbell", "calories_burned": 180, "duration_minutes": 20, "sets": 3, "reps": "10-12", "intensity": "high", "instructions": "Lie on incline bench, press dumbbells up.", "youtube_link": "https://www.youtube.com/watch?v=8iPEnn-ltC8"},
    {"name": "Deadlift", "type": "strength", "muscle_group": "back", "split": "pull", "equipment": "barbell", "calories_burned": 300, "duration_minutes": 20, "sets": 3, "reps": "6-10", "intensity": "high", "instructions": "Grip barbell, lift with straight back.", "youtube_link": "https://www.youtube.com/watch?v=op9kVnSso6Q"},
    {"name": "Leg Press", "type": "strength", "muscle_group": "legs", "split": "legs", "equipment": "machine", "calories_burned": 230, "duration_minutes": 20, "sets": 3, "reps": "10-12", "intensity": "high", "instructions": "Sit in leg press, push platform.", "youtube_link": "https://www.youtube.com/watch?v=IZxyjW7LWks"},
    {"name": "Lateral Raises", "type": "strength", "muscle_group": "shoulders", "split": "push", "equipment": "dumbbell", "calories_burned": 130, "duration_minutes": 15, "sets": 3, "reps": "12-15", "intensity": "medium", "instructions": "Raise dumbbells to shoulder height.", "youtube_link": "https://www.youtube.com/watch?v=3VcKaXpzqRo"},
    {"name": "Bicep Curls", "type": "strength", "muscle_group": "biceps", "split": "pull", "equipment": "dumbbell", "calories_burned": 130, "duration_minutes": 15, "sets": 3, "reps": "12-15", "intensity": "medium", "instructions": "Curl dumbbells to shoulders.", "youtube_link": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo"},
    {"name": "Calf Raises", "type": "strength", "muscle_group": "calves", "split": "legs", "equipment": "none", "calories_burned": 120, "duration_minutes": 15, "sets": 3, "reps": "15-20", "intensity": "medium", "instructions": "Stand, raise heels.", "youtube_link": "https://www.youtube.com/watch?v=3kA2tIP2BCY"},
    {"name": "Tricep Dips", "type": "bodyweight", "muscle_group": "triceps", "split": "push", "equipment": "dip bar", "calories_burned": 150, "duration_minutes": 15, "sets": 3, "reps": "10-15", "intensity": "medium", "instructions": "Grip dip bars, lower body, push up.", "youtube_link": "https://www.youtube.com/watch?v=2z8JmcrW-As"}
]
muscle_groups = ["chest", "back", "legs", "shoulders", "triceps", "biceps", "quads", "hamstrings", "calves"]
splits = ["push", "pull", "legs"]
equipment = ["barbell", "dumbbell", "machine", "cable", "none", "pull-up bar", "dip bar", "bench"]
intensities = ["low", "medium", "high"]
types = ["strength", "bodyweight", "cardio"]

# Meal attributes
meal_templates = [
    {"name": "Oatmeal with Protein Powder", "type": "vegetarian", "calories": 400, "protein": 20, "carbs": 60, "fat": 10, "meal_type": "breakfast", "prep_time_minutes": 10, "instructions": "Mix oats with water, microwave 2 min, add protein powder."},
    {"name": "Chicken Wrap", "type": "non-vegetarian", "calories": 500, "protein": 30, "carbs": 50, "fat": 15, "meal_type": "lunch", "prep_time_minutes": 15, "instructions": "Grill chicken, wrap with veggies and sauce."},
    {"name": "Grilled Chicken Salad", "type": "non-vegetarian", "calories": 400, "protein": 35, "carbs": 20, "fat": 15, "meal_type": "dinner", "prep_time_minutes": 20, "instructions": "Grill chicken, toss with greens and dressing."},
    {"name": "Vegetable Pulao", "type": "vegetarian", "calories": 450, "protein": 10, "carbs": 70, "fat": 12, "meal_type": "lunch", "prep_time_minutes": 30, "instructions": "Sauté veggies, cook with rice and spices."},
    {"name": "Paneer Tikka", "type": "vegetarian", "calories": 400, "protein": 20, "carbs": 30, "fat": 25, "meal_type": "dinner", "prep_time_minutes": 30, "instructions": "Marinate paneer, grill with veggies."},
    {"name": "Boiled Eggs with Toast", "type": "non-vegetarian", "calories": 350, "protein": 18, "carbs": 30, "fat": 15, "meal_type": "breakfast", "prep_time_minutes": 15, "instructions": "Boil eggs 8 min, toast bread."},
    {"name": "Salmon with Quinoa", "type": "non-vegetarian", "calories": 450, "protein": 30, "carbs": 40, "fat": 18, "meal_type": "dinner", "prep_time_minutes": 25, "instructions": "Bake salmon, cook quinoa."},
    {"name": "Chickpea Salad", "type": "vegetarian", "calories": 400, "protein": 15, "carbs": 50, "fat": 15, "meal_type": "lunch", "prep_time_minutes": 15, "instructions": "Toss chickpeas with veggies and dressing."},
    {"name": "Greek Yogurt with Fruit", "type": "vegetarian", "calories": 300, "protein": 15, "carbs": 40, "fat": 5, "meal_type": "breakfast", "prep_time_minutes": 5, "instructions": "Mix yogurt with fruit and honey."},
    {"name": "Turkey Sandwich", "type": "non-vegetarian", "calories": 450, "protein": 25, "carbs": 50, "fat": 10, "meal_type": "lunch", "prep_time_minutes": 10, "instructions": "Layer turkey, lettuce, and mayo on bread."}
]
meal_types = ["breakfast", "lunch", "dinner"]
diet_types = ["vegetarian", "non-vegetarian"]

# Generate workouts
workouts = []
for i in range(1, 201):
    base = random.choice(workout_templates)
    muscle = random.choice(muscle_groups)
    split = random.choice(splits)
    equip = random.choice(equipment)
    intensity = random.choice(intensities)
    workout = {
        "id": i,
        "name": f"{base['name']} Variation {i}" if i > len(workout_templates) else base['name'],
        "type": random.choice(types),
        "muscle_group": muscle,
        "split": split,
        "equipment": equip,
        "calories_burned": base['calories_burned'] + random.randint(-20, 20),
        "duration_minutes": base['duration_minutes'] + random.randint(-5, 5),
        "sets": random.randint(2, 4),
        "reps": random.choice(["8-12", "10-15", "12-20", "failure"]),
        "intensity": intensity,
        "instructions": base['instructions'],
        "youtube_link": base['youtube_link']
    }
    workouts.append(workout)

# Generate meals
meals = []
for i in range(1, 201):
    base = random.choice(meal_templates)
    meal_type = random.choice(meal_types)
    diet = random.choice(diet_types)
    meal = {
        "id": i,
        "name": f"{base['name']} Variation {i}" if i > len(meal_templates) else base['name'],
        "type": diet,
        "calories": base['calories'] + random.randint(-50, 50),
        "protein": base['protein'] + random.randint(-5, 5),
        "carbs": base['carbs'] + random.randint(-10, 10),
        "fat": base['fat'] + random.randint(-5, 5),
        "meal_type": meal_type,
        "prep_time_minutes": base['prep_time_minutes'] + random.randint(-5, 5),
        "instructions": base['instructions']
    }
    meals.append(meal)

# Save to files
with open("workouts.json", "w") as f:
    json.dump(workouts, f, indent=2)
with open("meals.json", "w") as f:
    json.dump(meals, f, indent=2)

print("Generated workouts.json and meals.json with ~200 entries each.")