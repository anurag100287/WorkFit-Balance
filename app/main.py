from kivy.app import App
from kivy.uix.label import Label

class WfbApp(App):
    def build(self):
        return Label(text="Welcome to WorkFit Balance")

if __name__ == "__main__":
    WfbApp().run()