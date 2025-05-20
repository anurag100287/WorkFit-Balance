import pandas as pd
import json

# Load datasets
exercise_df = pd.read_csv('exercises.csv')
mega_df = pd.read_csv('megaGymDataset.csv')

# Function to map body part to split
def assign_split(body_part):
    push = ['chest', 'shoulders', 'triceps']
    pull = ['back', 'biceps']
    legs = ['quads', 'hamstrings', 'glutes', 'calves']
    body_part = body_part.lower() if isinstance(body_part, str) else ''
    if any(part in body_part for part in push):
        return 'push'
    elif any(part in body_part for part in pull):
        return 'pull'
    elif any(part in body_part for part in legs):
        return 'legs'
    return 'push'

# Clean datasets
exercise_df = exercise_df.dropna(subset=['name', 'bodyPart'])
mega_df = mega_df.dropna(subset=['Title', 'BodyPart'])

# Process exercises.csv
workouts = []
for idx, row in exercise_df.iterrows():
    instructions = [row[f'instructions/{i}'] for i in range(11) if pd.notna(row[f'instructions/{i}'])]
    name = row['name'].lower() if pd.notna(row['name']) else ''
    body_part = row['bodyPart'].lower() if pd.notna(row['bodyPart']) else ''
    intensity = 'high' if any(kw in name for kw in ['squat', 'deadlift', 'bench', 'press', 'pull-up']) or \
                         any(bp in body_part for bp in ['chest', 'back', 'legs']) else 'medium'
    workout = {
        'id': int(row['id']),
        'name': row['name'],
        'type': 'strength',
        'muscle_group': row['bodyPart'],
        'split': assign_split(row['bodyPart']),
        'equipment': row['equipment'] if pd.notna(row['equipment']) else 'none',
        'calories_burned': 200 if intensity == 'high' else 150,
        'duration_minutes': 20 if intensity == 'high' else 15,
        'sets': 4 if intensity == 'high' else 3,
        'reps': '6-8' if intensity == 'high' else '8-12',
        'intensity': intensity,
        'instructions': f"{' '.join(instructions)} Use 70-80% 1RM, rest {90 if intensity == 'high' else 60}s.",
        'youtube_link': row['gifUrl'] if pd.notna(row['gifUrl']) else ''
    }
    if len(workout['name']) > 3:
        workouts.append(workout)

# Process megaGymDataset.csv
seen_names = {w['name'].lower() for w in workouts}
for idx, row in mega_df.iterrows():
    name = row['Title']
    if name.lower() not in seen_names:
        intensity = row['Level'].lower() if pd.notna(row['Level']) else 'medium'
        workout = {
            'id': len(workouts) + idx + 1,
            'name': name,
            'type': row['Type'].lower() if pd.notna(row['Type']) else 'strength',
            'muscle_group': row['BodyPart'].lower() if pd.notna(row['BodyPart']) else 'unknown',
            'split': assign_split(row['BodyPart']),
            'equipment': row['Equipment'].lower() if pd.notna(row['Equipment']) else 'none',
            'calories_burned': 200 if intensity == 'high' else 150,
            'duration_minutes': 20 if intensity == 'high' else 15,
            'sets': 4 if intensity == 'high' else 3,
            'reps': '6-8' if intensity == 'high' else '8-12',
            'intensity': intensity,
            'instructions': f"{row['Desc'] if pd.notna(row['Desc']) else 'Perform with proper form.'} Use 70-80% 1RM, rest {90 if intensity == 'high' else 60}s.",
            'youtube_link': ''
        }
        if len(workout['name']) > 3:
            workouts.append(workout)

# Save to workouts.json
with open('workouts.json', 'w') as f:
    json.dump(workouts, f, indent=2)

print(f"Generated workouts.json with {len(workouts)} entries.")