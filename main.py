#!/usr/bin/env python3
"""
SuperTuxKart Mobile - Simple Kivy App
Minimal tactical game for Android APK building
"""

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import random

class GameGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 6
        self.rows = 6
        self.spacing = 2
        self.padding = 10
        
        # Game state
        self.selected_unit = None
        self.turn = 1
        self.max_turns = 10
        
        # Units: [x, y, hp, team] where team: 0=player, 1=enemy
        self.units = [
            [0, 0, 3, 0], [1, 0, 2, 0], [2, 0, 2, 0],  # Player units
            [3, 5, 3, 1], [4, 5, 2, 1], [5, 5, 2, 1]   # Enemy units
        ]
        
        # Create grid buttons
        self.buttons = []
        for i in range(36):  # 6x6 grid
            btn = Button(
                text='',
                size_hint=(1, 1),
                font_size='20sp'
            )
            btn.bind(on_press=self.cell_clicked)
            btn.row = i // 6
            btn.col = i % 6
            self.buttons.append(btn)
            self.add_widget(btn)
        
        self.update_display()
    
    def get_unit_at(self, x, y):
        """Get unit at position"""
        for i, unit in enumerate(self.units):
            if unit[0] == x and unit[1] == y and unit[2] > 0:
                return i
        return None
    
    def cell_clicked(self, button):
        """Handle cell click"""
        x, y = button.col, button.row
        unit_idx = self.get_unit_at(x, y)
        
        # Select player unit
        if unit_idx is not None and self.units[unit_idx][3] == 0 and self.units[unit_idx][2] > 0:
            self.selected_unit = unit_idx
            self.update_display()
        
        # Move/attack with selected unit
        elif self.selected_unit is not None:
            selected = self.units[self.selected_unit]
            distance = abs(x - selected[0]) + abs(y - selected[1])
            
            if distance == 1:  # Adjacent cell
                if unit_idx is not None and self.units[unit_idx][3] == 1:
                    # Attack enemy
                    self.units[unit_idx][2] -= 1
                    if self.units[unit_idx][2] <= 0:
                        self.units[unit_idx][0] = -1  # Remove from board
                        self.units[unit_idx][1] = -1
                elif unit_idx is None:
                    # Move to empty cell
                    selected[0] = x
                    selected[1] = y
                
                self.selected_unit = None
                self.ai_turn()
                self.update_display()
    
    def ai_turn(self):
        """Simple AI turn"""
        enemies = [i for i, unit in enumerate(self.units) if unit[3] == 1 and unit[2] > 0]
        if enemies:
            enemy_idx = random.choice(enemies)
            enemy = self.units[enemy_idx]
            # Move toward center
            if enemy[0] > 2:
                enemy[0] -= 1
            elif enemy[0] < 2:
                enemy[0] += 1
            if enemy[1] > 2:
                enemy[1] -= 1
        
        self.turn += 1
    
    def update_display(self):
        """Update button display"""
        # Clear all buttons
        for btn in self.buttons:
            btn.text = ''
            btn.background_color = (0.5, 0.5, 0.5, 1)
        
        # Show units
        for i, unit in enumerate(self.units):
            if unit[2] > 0:  # Unit is alive
                x, y = unit[0], unit[1]
                if 0 <= x < 6 and 0 <= y < 6:
                    btn_idx = y * 6 + x
                    btn = self.buttons[btn_idx]
                    
                    if unit[3] == 0:  # Player unit
                        btn.text = '🚗' if i == 0 else '👤'
                        btn.background_color = (0.2, 0.4, 1, 1)  # Blue
                        if i == self.selected_unit:
                            btn.background_color = (1, 1, 0, 1)  # Yellow when selected
                    else:  # Enemy unit
                        btn.text = '🔴' if i == 3 else '💀'
                        btn.background_color = (1, 0.2, 0.2, 1)  # Red
        
        # Show possible moves for selected unit
        if self.selected_unit is not None:
            selected = self.units[self.selected_unit]
            sx, sy = selected[0], selected[1]
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if abs(dx) + abs(dy) == 1:  # Adjacent only
                        nx, ny = sx + dx, sy + dy
                        if 0 <= nx < 6 and 0 <= ny < 6:
                            btn_idx = ny * 6 + nx
                            btn = self.buttons[btn_idx]
                            unit_there = self.get_unit_at(nx, ny)
                            
                            if unit_there is None:
                                btn.background_color = (0, 1, 0, 0.5)  # Green for move
                            elif self.units[unit_there][3] == 1:
                                btn.background_color = (1, 0.5, 0, 0.8)  # Orange for attack

class SuperTuxKartMobileApp(App):
    def build(self):
        self.title = 'SuperTuxKart Mobile'
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='🏎️ SuperTuxKart Mobile',
            size_hint=(1, 0.1),
            font_size='24sp',
            color=(1, 1, 1, 1)
        )
        root.add_widget(title)
        
        # Game info
        self.info_label = Label(
            text='Tap blue units to select, then tap adjacent cells to move/attack',
            size_hint=(1, 0.1),
            font_size='14sp',
            color=(1, 1, 1, 1)
        )
        root.add_widget(self.info_label)
        
        # Game grid
        self.game_grid = GameGrid(size_hint=(1, 0.7))
        root.add_widget(self.game_grid)
        
        # Controls
        controls = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        reset_btn = Button(
            text='Reset Game',
            font_size='16sp'
        )
        reset_btn.bind(on_press=self.reset_game)
        controls.add_widget(reset_btn)
        
        root.add_widget(controls)
        
        return root
    
    def reset_game(self, instance):
        """Reset the game"""
        self.game_grid.selected_unit = None
        self.game_grid.turn = 1
        self.game_grid.units = [
            [0, 0, 3, 0], [1, 0, 2, 0], [2, 0, 2, 0],  # Player units
            [3, 5, 3, 1], [4, 5, 2, 1], [5, 5, 2, 1]   # Enemy units
        ]
        self.game_grid.update_display()

if __name__ == '__main__':
    SuperTuxKartMobileApp().run()