"""
Kivy-based Mini-Game

Mobile-optimized version of Quick Skirmish using Kivy
for Android deployment
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex
from kivy.vector import Vector
import json
from pathlib import Path

from .game_engine import QuickSkirmishEngine, Position, Team, UnitType


class GameBoard(Widget):
    """Kivy widget for the game board"""
    
    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.tile_size = 60
        self.board_size = engine.board.size
        
        # Touch handling
        self.selected_unit_pos = None
        self.highlighted_moves = []
        self.highlighted_attacks = []
        
        # Colors (Kivy uses 0-1 RGBA)
        self.colors = {
            'board': (0.4, 0.6, 0.2, 1),
            'grid': (0.3, 0.5, 0.15, 1),
            'blue_unit': (0.2, 0.4, 1, 1),
            'red_unit': (1, 0.2, 0.2, 1),
            'selected': (1, 1, 0, 0.6),
            'move': (0, 1, 0, 0.4),
            'attack': (1, 0, 0, 0.4)
        }
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        Clock.schedule_interval(self.update_board, 1/60.0)
        
    def update_graphics(self, *args):
        """Update graphics when size changes"""
        self.canvas.clear()
        self.draw_board()
        
    def draw_board(self):
        """Draw the game board"""
        with self.canvas:
            # Clear canvas
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Calculate board position (centered)
            board_pixel_size = self.board_size * self.tile_size
            self.board_x = (self.width - board_pixel_size) / 2
            self.board_y = (self.height - board_pixel_size) / 2
            
            # Draw board background
            Color(*self.colors['board'])
            Rectangle(pos=(self.board_x, self.board_y), 
                     size=(board_pixel_size, board_pixel_size))
            
            # Draw grid
            Color(*self.colors['grid'])
            for i in range(self.board_size + 1):
                # Vertical lines
                x = self.board_x + i * self.tile_size
                Line(points=[x, self.board_y, x, self.board_y + board_pixel_size], width=1)
                
                # Horizontal lines
                y = self.board_y + i * self.tile_size
                Line(points=[self.board_x, y, self.board_x + board_pixel_size, y], width=1)
            
            # Draw highlights
            self.draw_highlights()
            
            # Draw units
            self.draw_units()
    
    def draw_highlights(self):
        """Draw movement and attack highlights"""
        # Movement highlights
        for pos in self.highlighted_moves:
            tile_pos = self.get_tile_position(pos)
            Color(*self.colors['move'])
            Rectangle(pos=tile_pos, size=(self.tile_size, self.tile_size))
        
        # Attack highlights
        for pos in self.highlighted_attacks:
            tile_pos = self.get_tile_position(pos)
            Color(*self.colors['attack'])
            Rectangle(pos=tile_pos, size=(self.tile_size, self.tile_size))
        
        # Selected unit highlight
        if self.selected_unit_pos:
            tile_pos = self.get_tile_position(self.selected_unit_pos)
            Color(*self.colors['selected'])
            Rectangle(pos=tile_pos, size=(self.tile_size, self.tile_size))
    
    def draw_units(self):
        """Draw all units"""
        for unit in self.engine.board.units:
            tile_pos = self.get_tile_position(unit.position)
            center_x = tile_pos[0] + self.tile_size / 2
            center_y = tile_pos[1] + self.tile_size / 2
            
            # Unit color
            color = self.colors['blue_unit'] if unit.team == Team.BLUE else self.colors['red_unit']
            Color(*color)
            
            # Draw unit shape based on type
            if unit.unit_type == UnitType.SOLDIER:
                # Circle for soldier
                radius = self.tile_size * 0.3
                Ellipse(pos=(center_x - radius, center_y - radius), 
                       size=(radius * 2, radius * 2))
            elif unit.unit_type == UnitType.TANK:
                # Rectangle for tank
                size = self.tile_size * 0.6
                Rectangle(pos=(center_x - size/2, center_y - size/2), 
                         size=(size, size))
            else:  # HELICOPTER
                # Triangle for helicopter (simplified as circle with outline)
                radius = self.tile_size * 0.25
                Ellipse(pos=(center_x - radius, center_y - radius), 
                       size=(radius * 2, radius * 2))
                Color(1, 1, 1, 1)
                Line(circle=(center_x, center_y, radius), width=2)
            
            # Health bar
            self.draw_health_bar(unit, tile_pos)
    
    def draw_health_bar(self, unit, tile_pos):
        """Draw health bar above unit"""
        bar_width = self.tile_size * 0.8
        bar_height = 4
        bar_x = tile_pos[0] + (self.tile_size - bar_width) / 2
        bar_y = tile_pos[1] + self.tile_size + 5
        
        # Background
        Color(0.4, 0.4, 0.4, 1)
        Rectangle(pos=(bar_x, bar_y), size=(bar_width, bar_height))
        
        # Health fill
        health_ratio = unit.health / unit.max_health
        if health_ratio > 0.6:
            Color(0, 1, 0, 1)
        elif health_ratio > 0.3:
            Color(1, 1, 0, 1)
        else:
            Color(1, 0, 0, 1)
        
        fill_width = bar_width * health_ratio
        Rectangle(pos=(bar_x, bar_y), size=(fill_width, bar_height))
    
    def get_tile_position(self, board_pos):
        """Convert board position to screen position"""
        x = self.board_x + board_pos.x * self.tile_size
        y = self.board_y + (self.board_size - board_pos.y - 1) * self.tile_size
        return (x, y)
    
    def screen_to_board_pos(self, touch_pos):
        """Convert touch position to board position"""
        x, y = touch_pos
        
        # Check if touch is within board
        board_pixel_size = self.board_size * self.tile_size
        if (x < self.board_x or x >= self.board_x + board_pixel_size or
            y < self.board_y or y >= self.board_y + board_pixel_size):
            return None
        
        # Convert to board coordinates
        board_x = int((x - self.board_x) / self.tile_size)
        board_y = self.board_size - 1 - int((y - self.board_y) / self.tile_size)
        
        return Position(board_x, board_y)
    
    def on_touch_down(self, touch):
        """Handle touch input"""
        if not self.collide_point(*touch.pos):
            return False
        
        board_pos = self.screen_to_board_pos(touch.pos)
        if board_pos and self.engine.current_team == Team.BLUE:
            self.handle_board_touch(board_pos)
        
        return True
    
    def handle_board_touch(self, board_pos):
        """Handle touch on board position"""
        if self.selected_unit_pos is None:
            # Select unit
            unit = self.engine.board.get_unit_at(board_pos)
            if unit and unit.team == Team.BLUE:
                self.selected_unit_pos = board_pos
                self.update_highlights()
        else:
            # Action with selected unit
            if board_pos == self.selected_unit_pos:
                # Deselect
                self.selected_unit_pos = None
                self.highlighted_moves = []
                self.highlighted_attacks = []
            elif board_pos in self.highlighted_moves:
                # Move unit
                success = self.engine.move_unit(self.selected_unit_pos, board_pos)
                if success:
                    self.selected_unit_pos = board_pos
                    self.update_highlights()
            elif board_pos in self.highlighted_attacks:
                # Attack
                success = self.engine.attack_unit(self.selected_unit_pos, board_pos)
                if success:
                    self.selected_unit_pos = None
                    self.highlighted_moves = []
                    self.highlighted_attacks = []
            else:
                # Select different unit
                unit = self.engine.board.get_unit_at(board_pos)
                if unit and unit.team == Team.BLUE:
                    self.selected_unit_pos = board_pos
                    self.update_highlights()
    
    def update_highlights(self):
        """Update movement and attack highlights"""
        if self.selected_unit_pos:
            actions = self.engine.get_valid_actions(self.selected_unit_pos)
            self.highlighted_moves = actions['moves']
            self.highlighted_attacks = actions['attacks']
        else:
            self.highlighted_moves = []
            self.highlighted_attacks = []
    
    def update_board(self, dt):
        """Update board display"""
        self.canvas.clear()
        self.draw_board()


class GameUI(BoxLayout):
    """Main game UI layout"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Initialize game engine
        self.engine = QuickSkirmishEngine()
        
        # Create UI elements
        self.setup_ui()
        
        # Schedule AI turns
        Clock.schedule_interval(self.check_ai_turn, 0.5)
    
    def setup_ui(self):
        """Setup the UI layout"""
        # Top info panel
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        self.turn_label = Label(text=f"Turn: {self.engine.current_team.value.title()}", 
                               font_size='20sp')
        self.score_label = Label(text="Blue: 3 | Red: 3", font_size='16sp')
        
        info_layout.add_widget(self.turn_label)
        info_layout.add_widget(self.score_label)
        self.add_widget(info_layout)
        
        # Game board
        self.board_widget = GameBoard(self.engine, size_hint_y=0.8)
        self.add_widget(self.board_widget)
        
        # Bottom control panel
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        self.end_turn_btn = Button(text="End Turn", font_size='18sp')
        self.end_turn_btn.bind(on_press=self.end_turn)
        
        self.restart_btn = Button(text="Restart", font_size='18sp')
        self.restart_btn.bind(on_press=self.restart_game)
        
        control_layout.add_widget(self.end_turn_btn)
        control_layout.add_widget(self.restart_btn)
        self.add_widget(control_layout)
        
        # Update UI
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements"""
        self.turn_label.text = f"Turn: {self.engine.current_team.value.title()}"
        
        blue_units = len([u for u in self.engine.board.units if u.team == Team.BLUE])
        red_units = len([u for u in self.engine.board.units if u.team == Team.RED])
        self.score_label.text = f"Blue: {blue_units} | Red: {red_units}"
        
        # Disable end turn button during AI turn
        self.end_turn_btn.disabled = (self.engine.current_team == Team.RED)
        
        # Check game over
        if self.engine.game_over:
            if self.engine.winner:
                self.turn_label.text = f"{self.engine.winner.value.title()} Wins!"
            else:
                self.turn_label.text = "Draw!"
            self.end_turn_btn.disabled = True
    
    def end_turn(self, instance):
        """End current turn"""
        if self.engine.current_team == Team.BLUE:
            self.engine.end_turn()
            self.board_widget.selected_unit_pos = None
            self.board_widget.highlighted_moves = []
            self.board_widget.highlighted_attacks = []
            self.update_ui()
    
    def restart_game(self, instance):
        """Restart the game"""
        self.engine = QuickSkirmishEngine()
        self.board_widget.engine = self.engine
        self.board_widget.selected_unit_pos = None
        self.board_widget.highlighted_moves = []
        self.board_widget.highlighted_attacks = []
        self.update_ui()
    
    def check_ai_turn(self, dt):
        """Check if AI should take its turn"""
        if (self.engine.current_team == Team.RED and 
            not self.engine.game_over):
            # AI turn is handled automatically in engine.end_turn()
            pass
        self.update_ui()


class QuickSkirmishApp(App):
    """Main Kivy application"""
    
    def build(self):
        """Build the application"""
        self.title = "Quick Skirmish"
        return GameUI()


def main():
    """Run the mobile game"""
    QuickSkirmishApp().run()


if __name__ == "__main__":
    main()