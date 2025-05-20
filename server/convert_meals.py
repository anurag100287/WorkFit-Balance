import pandas as pd
import json

df = pd.read_excel('IndianFoodDatasetXLS.xlsx')

def assign_nutrition(diet, course):
    diet = diet.lower() if isinstance(diet, str) else 'non-vegetarian'
    course = course.lower() if isinstance(course, str) else 'main course'
    is_vegetarian = any(v in diet for v in ['vegetarian', 'diabetic friendly', 'eggitarian', 'vegan'])
    diet_type = 'vegetarian' if is_vegetarian else 'non-vegetarian'
    if diet_type == 'vegetarian':
        if course in ['breakfast', 'snack']:
            return {'calories': 350, 'protein': 10, 'carbs': 50, 'fat': 10, 'purpose': 'High-carb for energy'}
        elif course in ['main course', 'lunch', 'dinner']:
            return {'calories': 500, 'protein': 20, 'carbs': 60, 'fat': 15, 'purpose': 'Balanced for sustenance'}
        else:
            return {'calories': 400, 'protein': 15, 'carbs': 55, 'fat': 12, 'purpose': 'Moderate for energy'}
    else:
        if course in ['main course', 'lunch', 'dinner']:
            return {'calories': 650, 'protein': 35, 'carbs': 70, 'fat': 20, 'purpose': 'High-protein for recovery'}
        elif course in ['breakfast', 'snack']:
            return {'calories': 400, 'protein': 20, 'carbs': 45, 'fat': 15, 'purpose': 'Moderate for energy'}
        else:
            return {'calories': 450, 'protein': 25, 'carbs': 50, 'fat': 18, 'purpose': 'Balanced for sustenance'}

df = df.dropna(subset=['TranslatedRecipeName', 'Diet', 'Course'])
df['Diet'] = df['Diet'].str.lower()
df['Course'] = df['Course'].str.lower().replace({'main course': 'main course', 'starter': 'snack', 'dessert': 'snack', 'side dish': 'main course'})
df = df[df['TranslatedRecipeName'].str.len() > 3]
df = df[df['TotalTimeInMins'].apply(lambda x: pd.isna(x) or (isinstance(x, (int, float)) and 5 <= x <= 120))]

meals = []
for idx, row in df.iterrows():
    nutrition = assign_nutrition(row['Diet'], row['Course'])
    meal = {
        'id': int(row['Srno']),
        'name': row['TranslatedRecipeName'],
        'type': 'vegetarian' if any(v in row['Diet'].lower() for v in ['vegetarian', 'diabetic friendly', 'eggitarian', 'vegan']) else 'non-vegetarian',
        'calories': nutrition['calories'],
        'protein': nutrition['protein'],
        'carbs': nutrition['carbs'],
        'fat': nutrition['fat'],
        'meal_type': row['Course'],
        'prep_time_minutes': int(row['TotalTimeInMins']) if pd.notna(row['TotalTimeInMins']) else 30,
        'instructions': row['TranslatedInstructions'] if pd.notna(row['TranslatedInstructions']) else 'Follow standard recipe.',
        'purpose': nutrition['purpose']
    }
    meals.append(meal)

with open('meals.json', 'w') as f:
    json.dump(meals, f, indent=2)

print(f"Generated meals.json with {len(meals)} entries.")