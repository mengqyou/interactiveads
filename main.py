#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import random

class SuperTuxKartMobile(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Title
        title = Label(
            text='🏎️ SuperTuxKart Mobile\nQuick Skirmish',
            font_size='24sp',
            size_hint_y=0.3,
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        
        # Game status
        self.status = Label(
            text='Tap START to begin your racing adventure!',
            font_size='16sp',
            size_hint_y=0.2,
            halign='center'
        )
        self.status.bind(size=self.status.setter('text_size'))
        
        # Start button
        start_btn = Button(
            text='🏁 START RACE',
            font_size='20sp',
            size_hint_y=0.2,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        start_btn.bind(on_press=self.start_game)
        
        # Restart button
        restart_btn = Button(
            text='🔄 RESTART',
            font_size='16sp',
            size_hint_y=0.15,
            background_color=(0.8, 0.4, 0.2, 1)
        )
        restart_btn.bind(on_press=self.restart_game)
        
        # Instructions
        instructions = Label(
            text='Mini racing game based on SuperTuxKart.\nOptimized for mobile play!',
            font_size='14sp',
            size_hint_y=0.15,
            halign='center'
        )
        instructions.bind(size=instructions.setter('text_size'))
        
        # Add all widgets
        layout.add_widget(title)
        layout.add_widget(self.status)
        layout.add_widget(start_btn)
        layout.add_widget(restart_btn)
        layout.add_widget(instructions)
        
        return layout
    
    def start_game(self, button):
        """Start the racing simulation"""
        self.status.text = 'Racing in progress...'
        # Simulate a 5-second race
        Clock.schedule_once(self.finish_race, 5.0)
        button.disabled = True
        
    def finish_race(self, dt):
        """Finish the race with random result"""
        results = [
            "🥇 Victory! You won the race!",
            "🥈 Second place! Great racing!",
            "🥉 Third place! Not bad!",
            "🏁 You finished the race!"
        ]
        self.status.text = random.choice(results)
        
    def restart_game(self, button):
        """Reset the game"""
        self.status.text = 'Tap START to begin your racing adventure!'
        # Re-enable start button
        for child in self.root.children:
            if isinstance(child, Button) and 'START' in child.text:
                child.disabled = False

if __name__ == '__main__':
    SuperTuxKartMobile().run()