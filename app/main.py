from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
import requests

class UserForm(BoxLayout):
    gender = StringProperty("Male")
    workouts = ListProperty([])
    meals = ListProperty([])

    def submit_form(self):
        data = {
            "age": self.ids.age.text,
            "weight": self.ids.weight.text,
            "height": self.ids.height.text,
            "gender": self.gender,
            "goal": self.ids.goal.text,
            "schedule": self.ids.schedule.text
        }
        try:
            response = requests.post("http://localhost:5000/submit", json=data)
            result = response.json()
            self.workouts = result.get('workouts', [])
            self.meals = result.get('meals', [])
        except Exception as e:
            print(f"Error: {e}")

class WfbApp(App):
    def build(self):
        return UserForm()

if __name__ == "__main__":
    WfbApp().run()