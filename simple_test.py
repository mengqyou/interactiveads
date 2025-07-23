#!/usr/bin/env python3
"""
Simple Kivy Test App for Android Build Verification
"""

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        label = Label(
            text='SuperTuxKart Mobile\nBuild Test Successful!',
            font_size='20sp'
        )
        
        button = Button(
            text='Tap to Test',
            size_hint=(1, 0.2)
        )
        button.bind(on_press=self.on_button_press)
        
        layout.add_widget(label)
        layout.add_widget(button)
        
        return layout
    
    def on_button_press(self, instance):
        instance.text = 'APK Build Working!'

if __name__ == '__main__':
    TestApp().run()