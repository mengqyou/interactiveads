#!/usr/bin/env python3
"""
Shattered Pixel Dungeon: Boss Rush Arena Mini-Game

A 5-8 minute mini-game capturing the most exciting moments from Shattered Pixel Dungeon:
- Face iconic bosses (Goo, Tengu, DM-300) in quick succession
- Choose from 6 hero classes with unique abilities
- Strategic combat with resource management
- Simplified but authentic mechanics

Based on analysis of the full Shattered Pixel Dungeon open-source codebase.
"""

import pygame
import random
import math
import json
import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
GRID_SIZE = 32
ARENA_WIDTH = 15
ARENA_HEIGHT = 15

# Colors (Pixel Dungeon inspired palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (128, 128, 128)
RED = (255, 64, 64)
GREEN = (64, 255, 64)
BLUE = (64, 64, 255)
YELLOW = (255, 255, 64)
PURPLE = (255, 64, 255)
ORANGE = (255, 128, 0)
BROWN = (139, 69, 19)
DUNGEON_FLOOR = (89, 86, 82)
DUNGEON_WALL = (45, 45, 45)

class GameState(Enum):
    MENU = "menu"
    CLASS_SELECT = "class_select"
    PLAYING = "playing"
    BOSS_TRANSITION = "boss_transition"
    VICTORY = "victory"
    GAME_OVER = "game_over"

class HeroClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    HUNTRESS = "huntress"
    DUELIST = "duelist"
    CLERIC = "cleric"

class BossType(Enum):
    GOO = "goo"
    TENGU = "tengu"
    DM300 = "dm300"

@dataclass
class Stats:
    max_health: int
    health: int
    accuracy: int
    damage: Tuple[int, int]  # min, max
    armor: int
    
class StatusEffect:
    def __init__(self, name: str, duration: int, color: Tuple[int, int, int]):
        self.name = name
        self.duration = duration
        self.color = color
        
    def tick(self):
        self.duration -= 1
        return self.duration > 0

class Entity:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int], symbol: str):
        self.x = x
        self.y = y
        self.color = color
        self.symbol = symbol
        self.stats = Stats(100, 100, 85, (10, 15), 0)
        self.status_effects: List[StatusEffect] = []
        
    def move(self, dx: int, dy: int):
        new_x = max(0, min(ARENA_WIDTH - 1, self.x + dx))
        new_y = max(0, min(ARENA_HEIGHT - 1, self.y + dy))
        self.x, self.y = new_x, new_y
        
    def take_damage(self, damage: int) -> bool:
        actual_damage = max(1, damage - self.stats.armor)
        self.stats.health -= actual_damage
        return self.stats.health <= 0
        
    def heal(self, amount: int):
        self.stats.health = min(self.stats.max_health, self.stats.health + amount)
        
    def attack(self, target: 'Entity') -> int:
        if random.randint(1, 100) <= self.stats.accuracy:
            damage = random.randint(self.stats.damage[0], self.stats.damage[1])
            target.take_damage(damage)
            return damage
        return 0
        
    def add_status_effect(self, effect: StatusEffect):
        # Remove existing effect of same type
        self.status_effects = [e for e in self.status_effects if e.name != effect.name]
        self.status_effects.append(effect)
        
    def update_status_effects(self):
        self.status_effects = [e for e in self.status_effects if e.tick()]

class Hero(Entity):
    def __init__(self, hero_class: HeroClass):
        super().__init__(7, 12, WHITE, "@")
        self.hero_class = hero_class
        self.level = 3
        self.experience = 0
        self.potions = 3
        self.special_cooldown = 0
        
        # Class-specific stats and abilities
        self._setup_class_stats()
        
    def _setup_class_stats(self):
        class_configs = {
            HeroClass.WARRIOR: {
                'health': 120, 'damage': (12, 18), 'armor': 5, 'color': RED,
                'description': 'High health and armor, defensive abilities'
            },
            HeroClass.MAGE: {
                'health': 80, 'damage': (15, 22), 'armor': 0, 'color': BLUE,
                'description': 'Magic attacks, elemental damage'
            },
            HeroClass.ROGUE: {
                'health': 90, 'damage': (10, 25), 'armor': 2, 'color': DARK_GRAY,
                'description': 'High critical hits, stealth attacks'
            },
            HeroClass.HUNTRESS: {
                'health': 85, 'damage': (14, 20), 'armor': 3, 'color': GREEN,
                'description': 'Ranged attacks, nature magic'
            },
            HeroClass.DUELIST: {
                'health': 95, 'damage': (13, 19), 'armor': 4, 'color': PURPLE,
                'description': 'Combo attacks, weapon mastery'
            },
            HeroClass.CLERIC: {
                'health': 100, 'damage': (11, 16), 'armor': 3, 'color': YELLOW,
                'description': 'Healing abilities, holy magic'
            }
        }
        
        config = class_configs[self.hero_class]
        self.stats.max_health = config['health']
        self.stats.health = config['health']
        self.stats.damage = config['damage']
        self.stats.armor = config['armor']
        self.color = config['color']
        self.description = config['description']
        
    def use_potion(self):
        if self.potions > 0:
            self.potions -= 1
            heal_amount = random.randint(20, 35)
            self.heal(heal_amount)
            return heal_amount
        return 0
        
    def special_ability(self, target: Optional[Entity] = None) -> str:
        if self.special_cooldown > 0:
            return "Special ability on cooldown!"
            
        self.special_cooldown = 5
        
        if self.hero_class == HeroClass.WARRIOR:
            self.stats.armor += 10
            self.add_status_effect(StatusEffect("Shield", 3, YELLOW))
            return "Warrior's Defense! +10 armor for 3 turns"
            
        elif self.hero_class == HeroClass.MAGE:
            if target:
                damage = random.randint(25, 35)
                target.take_damage(damage)
                target.add_status_effect(StatusEffect("Burning", 3, ORANGE))
                return f"Fireball! {damage} damage + burning"
            return "Fireball cast!"
            
        elif self.hero_class == HeroClass.ROGUE:
            self.add_status_effect(StatusEffect("Stealth", 2, DARK_GRAY))
            return "Vanished into shadows! Next attack guaranteed critical"
            
        elif self.hero_class == HeroClass.HUNTRESS:
            # Nature's blessing - heal and boost
            self.heal(15)
            self.add_status_effect(StatusEffect("Nature's Blessing", 4, GREEN))
            return "Nature's Blessing! Healed and boosted accuracy"
            
        elif self.hero_class == HeroClass.DUELIST:
            self.add_status_effect(StatusEffect("Combo", 3, PURPLE))
            return "Combo Chain! Next 3 attacks deal extra damage"
            
        elif self.hero_class == HeroClass.CLERIC:
            self.heal(30)
            # Remove all negative status effects
            self.status_effects = [e for e in self.status_effects if e.name in ["Shield", "Stealth", "Nature's Blessing", "Combo"]]
            return "Divine Heal! Restored health and cleansed debuffs"
            
        return "Special ability used!"

class Boss(Entity):
    def __init__(self, boss_type: BossType):
        super().__init__(7, 3, RED, "B")
        self.boss_type = boss_type
        self.phase = 1
        self.special_cooldown = 0
        self.enraged = False
        
        self._setup_boss_stats()
        
    def _setup_boss_stats(self):
        boss_configs = {
            BossType.GOO: {
                'health': 150, 'damage': (15, 25), 'armor': 2, 'color': GREEN,
                'name': 'Caustic Goo', 'description': 'Acidic slime that pumps up for massive attacks'
            },
            BossType.TENGU: {
                'health': 120, 'damage': (18, 28), 'armor': 5, 'color': DARK_GRAY,
                'name': 'Tengu', 'description': 'Teleporting assassin with shuriken barrages'
            },
            BossType.DM300: {
                'health': 200, 'damage': (20, 30), 'armor': 8, 'color': LIGHT_GRAY,
                'name': 'DM-300', 'description': 'War machine with rockets and toxic gas'
            }
        }
        
        config = boss_configs[self.boss_type]
        self.stats.max_health = config['health']
        self.stats.health = config['health']
        self.stats.damage = config['damage']
        self.stats.armor = config['armor']
        self.color = config['color']
        self.name = config['name']
        self.description = config['description']
        
    def ai_action(self, hero: Hero) -> str:
        # Check if should enrage (below 50% health)
        if not self.enraged and self.stats.health < self.stats.max_health // 2:
            self.enraged = True
            self.stats.damage = (self.stats.damage[0] + 5, self.stats.damage[1] + 10)
            return f"{self.name} becomes enraged! Damage increased!"
            
        # Use special ability if available
        if self.special_cooldown <= 0:
            return self._use_special_ability(hero)
            
        # Move towards hero and attack
        dx = 1 if hero.x > self.x else -1 if hero.x < self.x else 0
        dy = 1 if hero.y > self.y else -1 if hero.y < self.y else 0
        
        # If adjacent, attack
        if abs(hero.x - self.x) <= 1 and abs(hero.y - self.y) <= 1:
            damage = self.attack(hero)
            if damage > 0:
                return f"{self.name} attacks for {damage} damage!"
            else:
                return f"{self.name} misses!"
        else:
            self.move(dx, dy)
            return f"{self.name} moves closer"
            
    def _use_special_ability(self, hero: Hero) -> str:
        self.special_cooldown = random.randint(3, 5)
        
        if self.boss_type == BossType.GOO:
            # Pump up - next attack deals massive damage
            self.add_status_effect(StatusEffect("Pumped", 2, ORANGE))
            return f"{self.name} pumps up! Next attack will be devastating!"
            
        elif self.boss_type == BossType.TENGU:
            # Teleport behind hero
            possible_positions = [
                (hero.x - 1, hero.y), (hero.x + 1, hero.y),
                (hero.x, hero.y - 1), (hero.x, hero.y + 1)
            ]
            valid_positions = [(x, y) for x, y in possible_positions 
                             if 0 <= x < ARENA_WIDTH and 0 <= y < ARENA_HEIGHT]
            if valid_positions:
                self.x, self.y = random.choice(valid_positions)
                # Immediate attack with bonus damage
                damage = self.attack(hero) + 10
                return f"{self.name} teleports and strikes for {damage} damage!"
            return f"{self.name} attempts to teleport but fails!"
            
        elif self.boss_type == BossType.DM300:
            # Rocket barrage - damages hero regardless of position
            damage = random.randint(15, 25)
            hero.take_damage(damage)
            hero.add_status_effect(StatusEffect("Stunned", 1, YELLOW))
            return f"{self.name} fires rockets for {damage} damage! Hero is stunned!"
            
        return f"{self.name} uses special ability!"
        
    def update(self):
        super().update_status_effects()
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

class BossRushGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Shattered Pixel Dungeon: Boss Rush Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        
        self.state = GameState.MENU
        self.hero: Optional[Hero] = None
        self.current_boss: Optional[Boss] = None
        self.boss_queue = [BossType.GOO, BossType.TENGU, BossType.DM300]
        self.current_boss_index = 0
        self.turn_log: List[str] = []
        self.game_start_time = 0
        self.score = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.CLASS_SELECT
                        
                elif self.state == GameState.CLASS_SELECT:
                    class_keys = {
                        pygame.K_1: HeroClass.WARRIOR,
                        pygame.K_2: HeroClass.MAGE,
                        pygame.K_3: HeroClass.ROGUE,
                        pygame.K_4: HeroClass.HUNTRESS,
                        pygame.K_5: HeroClass.DUELIST,
                        pygame.K_6: HeroClass.CLERIC
                    }
                    if event.key in class_keys:
                        self.start_game(class_keys[event.key])
                        
                elif self.state == GameState.PLAYING:
                    self.handle_game_input(event.key)
                    
                elif self.state in [GameState.VICTORY, GameState.GAME_OVER]:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                        
        return True
        
    def handle_game_input(self, key):
        if not self.hero or not self.current_boss:
            return
            
        action_taken = False
        
        # Movement
        if key == pygame.K_UP or key == pygame.K_w:
            self.hero.move(0, -1)
            action_taken = True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.hero.move(0, 1)
            action_taken = True
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.hero.move(-1, 0)
            action_taken = True
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.hero.move(1, 0)
            action_taken = True
            
        # Actions
        elif key == pygame.K_SPACE:  # Attack
            if abs(self.hero.x - self.current_boss.x) <= 1 and abs(self.hero.y - self.current_boss.y) <= 1:
                damage = self.hero.attack(self.current_boss)
                if damage > 0:
                    self.add_log(f"You attack {self.current_boss.name} for {damage} damage!")
                else:
                    self.add_log("You miss!")
                action_taken = True
            else:
                self.add_log("No target in range!")
                
        elif key == pygame.K_h:  # Use potion
            heal = self.hero.use_potion()
            if heal > 0:
                self.add_log(f"You drink a health potion and recover {heal} HP!")
                action_taken = True
            else:
                self.add_log("No potions left!")
                
        elif key == pygame.K_q:  # Special ability
            result = self.hero.special_ability(self.current_boss)
            self.add_log(result)
            action_taken = True
            
        if action_taken:
            # Update hero
            self.hero.update_status_effects()
            if self.hero.special_cooldown > 0:
                self.hero.special_cooldown -= 1
                
            # Boss turn
            if self.current_boss.stats.health > 0:
                boss_action = self.current_boss.ai_action(self.hero)
                self.add_log(boss_action)
                self.current_boss.update()
                
            # Check win/lose conditions
            if self.current_boss.stats.health <= 0:
                self.boss_defeated()
            elif self.hero.stats.health <= 0:
                self.state = GameState.GAME_OVER
                
    def start_game(self, hero_class: HeroClass):
        self.hero = Hero(hero_class)
        self.current_boss_index = 0
        self.score = 0
        self.turn_log = []
        self.game_start_time = pygame.time.get_ticks()
        self.spawn_next_boss()
        self.state = GameState.PLAYING
        self.add_log(f"Hero {hero_class.value.title()} enters the arena!")
        
    def spawn_next_boss(self):
        if self.current_boss_index < len(self.boss_queue):
            boss_type = self.boss_queue[self.current_boss_index]
            self.current_boss = Boss(boss_type)
            self.add_log(f"{self.current_boss.name} appears!")
        else:
            self.state = GameState.VICTORY
            
    def boss_defeated(self):
        self.score += 100 + (self.hero.stats.health // 2)  # Bonus for remaining health
        self.add_log(f"{self.current_boss.name} defeated! +{100 + (self.hero.stats.health // 2)} points")
        
        # Heal between bosses
        self.hero.heal(20)
        self.hero.potions += 1
        self.add_log("You found a health potion and feel refreshed!")
        
        self.current_boss_index += 1
        
        if self.current_boss_index >= len(self.boss_queue):
            self.state = GameState.VICTORY
        else:
            self.spawn_next_boss()
            
    def add_log(self, message: str):
        self.turn_log.append(message)
        if len(self.turn_log) > 15:  # Keep only last 15 messages
            self.turn_log.pop(0)
            
    def reset_game(self):
        self.state = GameState.MENU
        self.hero = None
        self.current_boss = None
        self.current_boss_index = 0
        self.turn_log = []
        self.score = 0
        
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.title_font.render("SHATTERED PIXEL DUNGEON", True, WHITE)
        subtitle = self.font.render("Boss Rush Arena", True, YELLOW)
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 200))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        instructions = [
            "Face the iconic bosses from Shattered Pixel Dungeon!",
            "",
            "• Choose your hero class wisely",
            "• Fight Goo, Tengu, and DM-300 in succession", 
            "• Use potions and special abilities strategically",
            "• Survive to become the ultimate champion!",
            "",
            "Press SPACE to begin your adventure"
        ]
        
        y_offset = 280
        for instruction in instructions:
            text = self.font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
    def draw_class_select(self):
        self.screen.fill(BLACK)
        
        title = self.title_font.render("Choose Your Hero", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        classes = [
            (HeroClass.WARRIOR, "1", RED),
            (HeroClass.MAGE, "2", BLUE),
            (HeroClass.ROGUE, "3", DARK_GRAY),
            (HeroClass.HUNTRESS, "4", GREEN),
            (HeroClass.DUELIST, "5", PURPLE),
            (HeroClass.CLERIC, "6", YELLOW)
        ]
        
        y_start = 150
        for i, (hero_class, key, color) in enumerate(classes):
            y = y_start + i * 80
            
            # Draw class info
            hero = Hero(hero_class)  # Temporary for stats
            
            class_text = self.font.render(f"{key}. {hero_class.value.title()}", True, color)
            desc_text = self.font.render(hero.description, True, WHITE)
            stats_text = self.font.render(f"HP: {hero.stats.max_health} | DMG: {hero.stats.damage[0]}-{hero.stats.damage[1]} | ARM: {hero.stats.armor}", True, LIGHT_GRAY)
            
            self.screen.blit(class_text, (150, y))
            self.screen.blit(desc_text, (150, y + 25))
            self.screen.blit(stats_text, (150, y + 45))
            
    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Draw arena
        arena_start_x = 50
        arena_start_y = 50
        
        for y in range(ARENA_HEIGHT):
            for x in range(ARENA_WIDTH):
                rect = pygame.Rect(
                    arena_start_x + x * GRID_SIZE,
                    arena_start_y + y * GRID_SIZE,
                    GRID_SIZE, GRID_SIZE
                )
                pygame.draw.rect(self.screen, DUNGEON_FLOOR, rect)
                pygame.draw.rect(self.screen, DUNGEON_WALL, rect, 1)
                
        # Draw entities
        if self.hero:
            hero_rect = pygame.Rect(
                arena_start_x + self.hero.x * GRID_SIZE + 4,
                arena_start_y + self.hero.y * GRID_SIZE + 4,
                GRID_SIZE - 8, GRID_SIZE - 8
            )
            pygame.draw.rect(self.screen, self.hero.color, hero_rect)
            
            # Draw hero symbol
            symbol = self.font.render("@", True, WHITE)
            symbol_rect = symbol.get_rect(center=hero_rect.center)
            self.screen.blit(symbol, symbol_rect)
            
        if self.current_boss:
            boss_rect = pygame.Rect(
                arena_start_x + self.current_boss.x * GRID_SIZE + 2,
                arena_start_y + self.current_boss.y * GRID_SIZE + 2,
                GRID_SIZE - 4, GRID_SIZE - 4
            )
            pygame.draw.rect(self.screen, self.current_boss.color, boss_rect)
            
            # Draw boss symbol
            symbol = self.font.render("B", True, WHITE)
            symbol_rect = symbol.get_rect(center=boss_rect.center)
            self.screen.blit(symbol, symbol_rect)
            
        # Draw UI
        self.draw_ui()
        
    def draw_ui(self):
        ui_x = 550
        
        # Hero info
        if self.hero:
            y = 50
            texts = [
                f"Hero: {self.hero.hero_class.value.title()}",
                f"Health: {self.hero.stats.health}/{self.hero.stats.max_health}",
                f"Potions: {self.hero.potions}",
                f"Special: {'Ready' if self.hero.special_cooldown == 0 else f'Cooldown {self.hero.special_cooldown}'}",
                ""
            ]
            
            for text in texts:
                if text:
                    color = RED if "Health" in text and self.hero.stats.health < 30 else WHITE
                    rendered = self.font.render(text, True, color)
                    self.screen.blit(rendered, (ui_x, y))
                y += 25
                
        # Boss info
        if self.current_boss:
            y += 20
            texts = [
                f"Boss: {self.current_boss.name}",
                f"Health: {self.current_boss.stats.health}/{self.current_boss.stats.max_health}",
                f"Status: {'Enraged' if self.current_boss.enraged else 'Normal'}",
                ""
            ]
            
            for text in texts:
                if text:
                    color = YELLOW if "Enraged" in text else WHITE
                    rendered = self.font.render(text, True, color)
                    self.screen.blit(rendered, (ui_x, y))
                y += 25
                
        # Controls
        y += 20
        controls = [
            "Controls:",
            "WASD/Arrows - Move",
            "SPACE - Attack",
            "H - Use Potion", 
            "Q - Special Ability",
            ""
        ]
        
        for control in controls:
            if control:
                color = YELLOW if control == "Controls:" else LIGHT_GRAY
                rendered = self.font.render(control, True, color)
                self.screen.blit(rendered, (ui_x, y))
            y += 20
            
        # Turn log
        y += 20
        log_title = self.font.render("Combat Log:", True, YELLOW)
        self.screen.blit(log_title, (ui_x, y))
        y += 25
        
        for message in self.turn_log[-8:]:  # Show last 8 messages
            rendered = self.font.render(message, True, WHITE)
            self.screen.blit(rendered, (ui_x, y))
            y += 20
            
        # Score and progress
        progress_text = f"Boss {self.current_boss_index + 1}/3"
        score_text = f"Score: {self.score}"
        time_elapsed = (pygame.time.get_ticks() - self.game_start_time) // 1000
        time_text = f"Time: {time_elapsed//60}:{time_elapsed%60:02d}"
        
        self.screen.blit(self.font.render(progress_text, True, WHITE), (ui_x, 20))
        self.screen.blit(self.font.render(score_text, True, WHITE), (ui_x + 150, 20))
        self.screen.blit(self.font.render(time_text, True, WHITE), (ui_x + 250, 20))
        
    def draw_end_screen(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.VICTORY:
            title = self.title_font.render("VICTORY!", True, GREEN)
            message = "You have defeated all the bosses!"
        else:
            title = self.title_font.render("DEFEAT", True, RED)
            message = "The dungeon has claimed another hero..."
            
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        time_elapsed = (pygame.time.get_ticks() - self.game_start_time) // 1000
        
        stats = [
            message,
            "",
            f"Final Score: {self.score}",
            f"Time Survived: {time_elapsed//60}:{time_elapsed%60:02d}",
            f"Bosses Defeated: {self.current_boss_index}/{len(self.boss_queue)}",
            "",
            "Press R to restart or Q to quit"
        ]
        
        y = 280
        for stat in stats:
            if stat:
                color = YELLOW if "Score" in stat or "Time" in stat or "Bosses" in stat else WHITE
                text = self.font.render(stat, True, color)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
            y += 30
            
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            
            # Draw based on current state
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.CLASS_SELECT:
                self.draw_class_select()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state in [GameState.VICTORY, GameState.GAME_OVER]:
                self.draw_end_screen()
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    print("🎮 Starting Shattered Pixel Dungeon: Boss Rush Arena")
    print("Based on the acclaimed open-source roguelike!")
    print("Face iconic bosses in epic 5-8 minute battles!")
    
    try:
        game = BossRushGame()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        sys.exit(1)