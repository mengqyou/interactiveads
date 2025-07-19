"""
UI Renderer

Renders the mini-game interface using pygame
"""
import pygame
from typing import Dict, List, Tuple, Optional
from .game_engine import QuickSkirmishEngine, Position, Team, UnitType
from .asset_manager import AssetManager


class UIRenderer:
    """Renders the Quick Skirmish mini-game"""
    
    def __init__(self, engine: QuickSkirmishEngine, assets: AssetManager):
        self.engine = engine
        self.assets = assets
        
        # Display settings
        self.tile_size = 64
        self.board_offset_x = 50
        self.board_offset_y = 50
        
        # Calculate window size
        board_width = engine.board.size * self.tile_size
        board_height = engine.board.size * self.tile_size
        ui_panel_width = 250
        
        self.screen_width = board_width + ui_panel_width + 100
        self.screen_height = board_height + 150
        
        # Initialize pygame display
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Quick Skirmish - Tanks of Freedom Mini-Game")
        
        # UI state
        self.selected_unit_pos = None
        self.highlighted_moves = []
        self.highlighted_attacks = []
        
        # Colors
        self.colors = {
            'background': (50, 50, 50),
            'board': (100, 150, 50),
            'grid': (80, 120, 40),
            'text': (255, 255, 255),
            'blue_team': (100, 150, 255),
            'red_team': (255, 100, 100),
            'selected': (255, 255, 0),
            'button': (150, 150, 150),
            'button_hover': (200, 200, 200)
        }
        
        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
    def render(self):
        """Render the complete game state"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Render game board
        self._render_board()
        
        # Render units
        self._render_units()
        
        # Render UI panel
        self._render_ui_panel()
        
        # Render game over screen if needed
        if self.engine.game_over:
            self._render_game_over()
        
        pygame.display.flip()
    
    def _render_board(self):
        """Render the game board with grid"""
        board_rect = pygame.Rect(
            self.board_offset_x,
            self.board_offset_y,
            self.engine.board.size * self.tile_size,
            self.engine.board.size * self.tile_size
        )
        
        # Fill board background
        pygame.draw.rect(self.screen, self.colors['board'], board_rect)
        
        # Draw grid lines
        for i in range(self.engine.board.size + 1):
            # Vertical lines
            x = self.board_offset_x + i * self.tile_size
            pygame.draw.line(
                self.screen, 
                self.colors['grid'],
                (x, self.board_offset_y),
                (x, self.board_offset_y + self.engine.board.size * self.tile_size)
            )
            
            # Horizontal lines
            y = self.board_offset_y + i * self.tile_size
            pygame.draw.line(
                self.screen,
                self.colors['grid'],
                (self.board_offset_x, y),
                (self.board_offset_x + self.engine.board.size * self.tile_size, y)
            )
        
        # Render movement and attack highlights
        self._render_highlights()
    
    def _render_highlights(self):
        """Render movement and attack highlights"""
        # Movement highlights
        for pos in self.highlighted_moves:
            tile_rect = self._get_tile_rect(pos)
            highlight_surface = pygame.Surface((self.tile_size, self.tile_size))
            highlight_surface.fill((0, 255, 0))
            highlight_surface.set_alpha(100)
            self.screen.blit(highlight_surface, tile_rect)
        
        # Attack highlights
        for pos in self.highlighted_attacks:
            tile_rect = self._get_tile_rect(pos)
            highlight_surface = pygame.Surface((self.tile_size, self.tile_size))
            highlight_surface.fill((255, 0, 0))
            highlight_surface.set_alpha(100)
            self.screen.blit(highlight_surface, tile_rect)
        
        # Selected unit highlight
        if self.selected_unit_pos:
            tile_rect = self._get_tile_rect(self.selected_unit_pos)
            highlight_surface = pygame.Surface((self.tile_size, self.tile_size))
            highlight_surface.fill(self.colors['selected'])
            highlight_surface.set_alpha(150)
            self.screen.blit(highlight_surface, tile_rect)
    
    def _render_units(self):
        """Render all units on the board"""
        for unit in self.engine.board.units:
            # Get unit sprite
            sprite = self.assets.get_unit_sprite(unit.unit_type.value, unit.team.value)
            
            if sprite:
                # Scale sprite to fit tile
                scaled_sprite = self.assets.scale_sprite(sprite, self.tile_size / 32)
                
                # Position sprite in center of tile
                tile_rect = self._get_tile_rect(unit.position)
                sprite_rect = scaled_sprite.get_rect()
                sprite_rect.center = tile_rect.center
                
                self.screen.blit(scaled_sprite, sprite_rect)
            else:
                # Fallback: draw colored circle
                tile_rect = self._get_tile_rect(unit.position)
                color = self.colors['blue_team'] if unit.team == Team.BLUE else self.colors['red_team']
                pygame.draw.circle(self.screen, color, tile_rect.center, self.tile_size // 3)
            
            # Draw health bar
            self._render_health_bar(unit)
            
            # Draw unit type indicator
            self._render_unit_indicator(unit)
    
    def _render_health_bar(self, unit):
        """Render health bar above unit"""
        tile_rect = self._get_tile_rect(unit.position)
        
        # Health bar dimensions
        bar_width = self.tile_size - 10
        bar_height = 6
        
        # Health bar position (above unit)
        bar_x = tile_rect.x + 5
        bar_y = tile_rect.y - 10
        
        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (100, 100, 100), bg_rect)
        
        # Health fill
        health_ratio = unit.health / unit.max_health
        fill_width = int(bar_width * health_ratio)
        
        if health_ratio > 0.6:
            health_color = (0, 255, 0)
        elif health_ratio > 0.3:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self.screen, health_color, fill_rect)
    
    def _render_unit_indicator(self, unit):
        """Render unit type indicator"""
        tile_rect = self._get_tile_rect(unit.position)
        
        # Simple text indicator
        if unit.unit_type == UnitType.SOLDIER:
            indicator = "S"
        elif unit.unit_type == UnitType.TANK:
            indicator = "T"
        else:  # HELICOPTER
            indicator = "H"
        
        text_surface = self.font.render(indicator, True, self.colors['text'])
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (tile_rect.right - 5, tile_rect.bottom - 5)
        
        self.screen.blit(text_surface, text_rect)
    
    def _render_ui_panel(self):
        """Render the UI panel with game info and controls"""
        panel_x = self.board_offset_x + self.engine.board.size * self.tile_size + 20
        panel_y = self.board_offset_y
        
        # Current turn indicator
        team_text = f"Turn: {self.engine.current_team.value.title()}"
        turn_surface = self.big_font.render(team_text, True, self.colors['text'])
        self.screen.blit(turn_surface, (panel_x, panel_y))
        
        # Turn counter
        turn_text = f"Turn {self.engine.turn_count + 1}/{self.engine.max_turns}"
        turn_surface = self.font.render(turn_text, True, self.colors['text'])
        self.screen.blit(turn_surface, (panel_x, panel_y + 40))
        
        # Unit counts
        blue_units = len([u for u in self.engine.board.units if u.team == Team.BLUE])
        red_units = len([u for u in self.engine.board.units if u.team == Team.RED])
        
        blue_text = f"Blue Units: {blue_units}"
        red_text = f"Red Units: {red_units}"
        
        blue_surface = self.font.render(blue_text, True, self.colors['blue_team'])
        red_surface = self.font.render(red_text, True, self.colors['red_team'])
        
        self.screen.blit(blue_surface, (panel_x, panel_y + 80))
        self.screen.blit(red_surface, (panel_x, panel_y + 100))
        
        # End turn button (only for human player)
        if self.engine.current_team == Team.BLUE:
            self._render_end_turn_button(panel_x, panel_y + 140)
        
        # Instructions
        instructions = [
            "Click unit to select",
            "Green: Move",
            "Red: Attack",
            "Right-click: Cancel"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.font.render(instruction, True, self.colors['text'])
            self.screen.blit(inst_surface, (panel_x, panel_y + 200 + i * 25))
    
    def _render_end_turn_button(self, x: int, y: int):
        """Render end turn button"""
        button_rect = pygame.Rect(x, y, 120, 30)
        
        # Check if mouse is over button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)
        
        color = self.colors['button_hover'] if is_hover else self.colors['button']
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, self.colors['text'], button_rect, 2)
        
        # Button text
        text_surface = self.font.render("End Turn", True, self.colors['text'])
        text_rect = text_surface.get_rect()
        text_rect.center = button_rect.center
        self.screen.blit(text_surface, text_rect)
        
        # Store button rect for click detection
        self.end_turn_button_rect = button_rect
    
    def _render_game_over(self):
        """Render game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        if self.engine.winner:
            game_over_text = f"{self.engine.winner.value.title()} Wins!"
        else:
            game_over_text = "Draw!"
        
        text_surface = self.big_font.render(game_over_text, True, self.colors['text'])
        text_rect = text_surface.get_rect()
        text_rect.center = (self.screen_width // 2, self.screen_height // 2)
        
        self.screen.blit(text_surface, text_rect)
        
        # Restart instruction
        restart_text = "Press R to restart or ESC to quit"
        restart_surface = self.font.render(restart_text, True, self.colors['text'])
        restart_rect = restart_surface.get_rect()
        restart_rect.center = (self.screen_width // 2, self.screen_height // 2 + 50)
        
        self.screen.blit(restart_surface, restart_rect)
    
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Handle mouse click and return True if action was taken"""
        # Convert screen coordinates to board coordinates
        board_pos = self._screen_to_board_pos(pos)
        
        if board_pos and self.engine.current_team == Team.BLUE:
            # Check if clicking on end turn button
            if hasattr(self, 'end_turn_button_rect') and self.end_turn_button_rect.collidepoint(pos):
                self.engine.end_turn()
                self.selected_unit_pos = None
                self.highlighted_moves = []
                self.highlighted_attacks = []
                return True
            
            # Handle board clicks
            if self.selected_unit_pos is None:
                # Select unit
                unit = self.engine.board.get_unit_at(board_pos)
                if unit and unit.team == Team.BLUE:
                    self.selected_unit_pos = board_pos
                    self._update_highlights()
                    return True
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
                        self.assets.play_sound('move')
                        self.selected_unit_pos = board_pos
                        self._update_highlights()
                    return True
                elif board_pos in self.highlighted_attacks:
                    # Attack
                    success = self.engine.attack_unit(self.selected_unit_pos, board_pos)
                    if success:
                        self.assets.play_sound('attack')
                        self.selected_unit_pos = None
                        self.highlighted_moves = []
                        self.highlighted_attacks = []
                    return True
                else:
                    # Select different unit
                    unit = self.engine.board.get_unit_at(board_pos)
                    if unit and unit.team == Team.BLUE:
                        self.selected_unit_pos = board_pos
                        self._update_highlights()
                        return True
        
        return False
    
    def handle_right_click(self, pos: Tuple[int, int]):
        """Handle right mouse click (cancel selection)"""
        self.selected_unit_pos = None
        self.highlighted_moves = []
        self.highlighted_attacks = []
    
    def _update_highlights(self):
        """Update movement and attack highlights for selected unit"""
        if self.selected_unit_pos:
            actions = self.engine.get_valid_actions(self.selected_unit_pos)
            self.highlighted_moves = actions['moves']
            self.highlighted_attacks = actions['attacks']
        else:
            self.highlighted_moves = []
            self.highlighted_attacks = []
    
    def _screen_to_board_pos(self, screen_pos: Tuple[int, int]) -> Optional[Position]:
        """Convert screen coordinates to board position"""
        x, y = screen_pos
        
        # Check if click is within board area
        if (x < self.board_offset_x or 
            x >= self.board_offset_x + self.engine.board.size * self.tile_size or
            y < self.board_offset_y or 
            y >= self.board_offset_y + self.engine.board.size * self.tile_size):
            return None
        
        # Convert to board coordinates
        board_x = (x - self.board_offset_x) // self.tile_size
        board_y = (y - self.board_offset_y) // self.tile_size
        
        return Position(board_x, board_y)
    
    def _get_tile_rect(self, pos: Position) -> pygame.Rect:
        """Get screen rectangle for board position"""
        return pygame.Rect(
            self.board_offset_x + pos.x * self.tile_size,
            self.board_offset_y + pos.y * self.tile_size,
            self.tile_size,
            self.tile_size
        )