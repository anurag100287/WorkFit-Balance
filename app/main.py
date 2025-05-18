from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class UserForm(BoxLayout):
    gender = StringProperty("Male")  # Default gender

    def submit_form(self):
        # Placeholder for form submission
        print(f"Age: {self.ids.age.text}, Weight: {self.ids.weight.text}, "
              f"Height: {self.ids.height.text}, Gender: {self.gender}, "
              f"Goal: {self.ids.goal.text}, Schedule: {self.ids.schedule.text}")

class WfbApp(App):
    def build(self):
        return UserForm()

if __name__ == "__main__":
    WfbApp().run()