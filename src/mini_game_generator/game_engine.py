"""
Mini-Game Engine

Core engine for generating and running tactical mini-games
based on the Quick Skirmish format from Tanks of Freedom
"""
import pygame
import json
import random
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class UnitType(Enum):
    SOLDIER = "soldier"
    TANK = "tank"
    HELICOPTER = "helicopter"


class Team(Enum):
    BLUE = "blue"
    RED = "red"


@dataclass
class Position:
    x: int
    y: int
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def distance_to(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class Unit:
    unit_type: UnitType
    team: Team
    position: Position
    health: int = 100
    max_health: int = 100
    attack_power: int = 30
    movement_range: int = 3
    attack_range: int = 1
    has_moved: bool = False
    has_attacked: bool = False
    
    def can_move_to(self, pos: Position, board_size: int) -> bool:
        """Check if unit can move to position"""
        if pos.x < 0 or pos.x >= board_size or pos.y < 0 or pos.y >= board_size:
            return False
        distance = self.position.distance_to(pos)
        return distance <= self.movement_range and not self.has_moved
    
    def can_attack(self, target_pos: Position) -> bool:
        """Check if unit can attack target position"""
        if self.has_attacked:
            return False
        distance = self.position.distance_to(target_pos)
        return distance <= self.attack_range
    
    def reset_turn(self):
        """Reset unit for new turn"""
        self.has_moved = False
        self.has_attacked = False


class GameBoard:
    """Manages the tactical game board"""
    
    def __init__(self, size: int = 8):
        self.size = size
        self.units: List[Unit] = []
        self.terrain = [[0 for _ in range(size)] for _ in range(size)]  # 0 = empty, 1 = obstacle
        
    def add_unit(self, unit: Unit) -> bool:
        """Add unit to board if position is valid"""
        if self.get_unit_at(unit.position) is None:
            self.units.append(unit)
            return True
        return False
    
    def get_unit_at(self, pos: Position) -> Optional[Unit]:
        """Get unit at position"""
        for unit in self.units:
            if unit.position.x == pos.x and unit.position.y == pos.y:
                return unit
        return None
    
    def move_unit(self, unit: Unit, new_pos: Position) -> bool:
        """Move unit to new position"""
        if unit.can_move_to(new_pos, self.size) and self.get_unit_at(new_pos) is None:
            unit.position = new_pos
            unit.has_moved = True
            return True
        return False
    
    def attack_unit(self, attacker: Unit, target_pos: Position) -> bool:
        """Attack unit at target position"""
        target = self.get_unit_at(target_pos)
        if target and attacker.can_attack(target_pos) and target.team != attacker.team:
            # Calculate damage
            damage = attacker.attack_power + random.randint(-5, 5)
            target.health -= damage
            attacker.has_attacked = True
            
            # Remove dead units
            if target.health <= 0:
                self.units.remove(target)
            
            return True
        return False
    
    def get_valid_moves(self, unit: Unit) -> List[Position]:
        """Get all valid move positions for unit"""
        moves = []
        for x in range(max(0, unit.position.x - unit.movement_range), 
                      min(self.size, unit.position.x + unit.movement_range + 1)):
            for y in range(max(0, unit.position.y - unit.movement_range), 
                          min(self.size, unit.position.y + unit.movement_range + 1)):
                pos = Position(x, y)
                if unit.can_move_to(pos, self.size) and self.get_unit_at(pos) is None:
                    moves.append(pos)
        return moves
    
    def get_attack_targets(self, unit: Unit) -> List[Position]:
        """Get all valid attack targets for unit"""
        targets = []
        for x in range(max(0, unit.position.x - unit.attack_range), 
                      min(self.size, unit.position.x + unit.attack_range + 1)):
            for y in range(max(0, unit.position.y - unit.attack_range), 
                          min(self.size, unit.position.y + unit.attack_range + 1)):
                pos = Position(x, y)
                target = self.get_unit_at(pos)
                if target and unit.can_attack(pos) and target.team != unit.team:
                    targets.append(pos)
        return targets


class QuickSkirmishEngine:
    """Main game engine for Quick Skirmish mini-game"""
    
    def __init__(self):
        self.board = GameBoard(6)  # Smaller board for quick games
        self.current_team = Team.BLUE
        self.turn_count = 0
        self.max_turns = 10  # 5 turns per player
        self.game_over = False
        self.winner = None
        
        # Initialize units
        self._setup_units()
    
    def _setup_units(self):
        """Setup initial unit positions"""
        # Blue team (player)
        blue_units = [
            Unit(UnitType.SOLDIER, Team.BLUE, Position(0, 2)),
            Unit(UnitType.TANK, Team.BLUE, Position(1, 1)),
            Unit(UnitType.SOLDIER, Team.BLUE, Position(1, 3)),
        ]
        
        # Red team (AI)
        red_units = [
            Unit(UnitType.SOLDIER, Team.RED, Position(5, 2)),
            Unit(UnitType.TANK, Team.RED, Position(4, 1)),
            Unit(UnitType.SOLDIER, Team.RED, Position(4, 3)),
        ]
        
        for unit in blue_units + red_units:
            self.board.add_unit(unit)
    
    def get_game_state(self) -> Dict:
        """Get current game state"""
        return {
            "board_size": self.board.size,
            "units": [
                {
                    "type": unit.unit_type.value,
                    "team": unit.team.value,
                    "position": {"x": unit.position.x, "y": unit.position.y},
                    "health": unit.health,
                    "max_health": unit.max_health,
                    "has_moved": unit.has_moved,
                    "has_attacked": unit.has_attacked
                }
                for unit in self.board.units
            ],
            "current_team": self.current_team.value,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "game_over": self.game_over,
            "winner": self.winner.value if self.winner else None
        }
    
    def move_unit(self, from_pos: Position, to_pos: Position) -> bool:
        """Move unit from one position to another"""
        unit = self.board.get_unit_at(from_pos)
        if unit and unit.team == self.current_team:
            return self.board.move_unit(unit, to_pos)
        return False
    
    def attack_unit(self, from_pos: Position, target_pos: Position) -> bool:
        """Attack from one position to another"""
        attacker = self.board.get_unit_at(from_pos)
        if attacker and attacker.team == self.current_team:
            return self.board.attack_unit(attacker, target_pos)
        return False
    
    def end_turn(self):
        """End current player's turn"""
        # Reset all units for current team
        for unit in self.board.units:
            if unit.team == self.current_team:
                unit.reset_turn()
        
        # Switch teams
        self.current_team = Team.RED if self.current_team == Team.BLUE else Team.BLUE
        
        # Increment turn counter
        if self.current_team == Team.BLUE:
            self.turn_count += 1
        
        # Check win conditions
        self._check_game_over()
        
        # AI turn if it's RED's turn
        if self.current_team == Team.RED and not self.game_over:
            self._ai_turn()
    
    def _check_game_over(self):
        """Check if game is over"""
        blue_units = [u for u in self.board.units if u.team == Team.BLUE]
        red_units = [u for u in self.board.units if u.team == Team.RED]
        
        if not blue_units:
            self.game_over = True
            self.winner = Team.RED
        elif not red_units:
            self.game_over = True
            self.winner = Team.BLUE
        elif self.turn_count >= self.max_turns:
            self.game_over = True
            # Winner determined by remaining units
            if len(blue_units) > len(red_units):
                self.winner = Team.BLUE
            elif len(red_units) > len(blue_units):
                self.winner = Team.RED
            else:
                self.winner = None  # Draw
    
    def _ai_turn(self):
        """Simple AI turn logic"""
        red_units = [u for u in self.board.units if u.team == Team.RED]
        
        for unit in red_units:
            # Try to attack first
            targets = self.board.get_attack_targets(unit)
            if targets:
                target = random.choice(targets)
                self.board.attack_unit(unit, target)
            else:
                # Move towards nearest enemy
                blue_units = [u for u in self.board.units if u.team == Team.BLUE]
                if blue_units:
                    nearest_enemy = min(blue_units, key=lambda u: unit.position.distance_to(u.position))
                    
                    # Find best move towards enemy
                    valid_moves = self.board.get_valid_moves(unit)
                    if valid_moves:
                        best_move = min(valid_moves, key=lambda pos: pos.distance_to(nearest_enemy.position))
                        self.board.move_unit(unit, best_move)
        
        # End AI turn
        self.end_turn()
    
    def get_valid_actions(self, pos: Position) -> Dict[str, List[Position]]:
        """Get valid actions for unit at position"""
        unit = self.board.get_unit_at(pos)
        if not unit or unit.team != self.current_team:
            return {"moves": [], "attacks": []}
        
        return {
            "moves": self.board.get_valid_moves(unit),
            "attacks": self.board.get_attack_targets(unit)
        }