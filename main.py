#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.label import Label

class MainApp(App):
    def build(self):
        return Label(text='🏎️ SuperTuxKart Mobile Works!')

if __name__ == '__main__':
    MainApp().run()