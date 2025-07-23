#!/usr/bin/env python3
"""
SuperTuxKart: Kart Combat Arena Mini-Game

A 5-8 minute mini-game capturing SuperTuxKart's most exciting elements:
- Phase 1: Speed Circuit with drift-boost chains
- Phase 2: Arena Battle with powerup combat
- Phase 3: Final Showdown with shrinking arena

Based on comprehensive analysis of SuperTuxKart's 129MB open-source codebase.
Features authentic kart physics, powerup combat, and spectacular visual effects.
"""

import pygame
import math
import random
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import colorsys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60
GRID_SIZE = 32

# Colors (SuperTuxKart inspired)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
GREEN = (50, 220, 50)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
PURPLE = (200, 50, 200)
CYAN = (0, 200, 200)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Track colors
TRACK_COLOR = (80, 80, 80)
TRACK_BORDER = (200, 200, 0)
GRASS_COLOR = (40, 120, 40)
BOOST_PAD = (0, 255, 255)

class GamePhase(Enum):
    MENU = "menu"
    SPEED_CIRCUIT = "speed_circuit"
    PHASE_TRANSITION = "phase_transition"
    ARENA_BATTLE = "arena_battle"
    FINAL_SHOWDOWN = "final_showdown"
    GAME_OVER = "game_over"

class PowerupType(Enum):
    BOWLING = "bowling"
    CAKE = "cake"
    ZIPPER = "zipper"
    BUBBLEGUM = "bubblegum"
    PLUNGER = "plunger"
    NITRO = "nitro"

@dataclass
class Vector2D:
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector2D(self.x / length, self.y / length)
        return Vector2D(0, 0)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        # Apply gravity to some particles
        if self.color in [ORANGE, RED, YELLOW]:
            self.vy += 150 * dt
            
        return self.lifetime > 0
        
    def draw(self, screen, camera_x=0, camera_y=0):
        if self.lifetime <= 0:
            return
            
        # Fade out over time
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        alpha = max(0, min(255, alpha))
        
        # Create surface for alpha blending
        surf = pygame.Surface((self.size * 2, self.size * 2))
        surf.set_alpha(alpha)
        color = (*self.color, alpha) if len(self.color) == 3 else self.color
        pygame.draw.circle(surf, self.color, (self.size, self.size), self.size)
        
        screen.blit(surf, (int(self.x - camera_x - self.size), int(self.y - camera_y - self.size)))

class Powerup:
    def __init__(self, powerup_type: PowerupType, x: float, y: float):
        self.type = powerup_type
        self.x = x
        self.y = y
        self.collected = False
        self.spawn_time = pygame.time.get_ticks()
        self.bob_offset = 0
        
    def update(self, dt):
        # Bobbing animation
        self.bob_offset = math.sin((pygame.time.get_ticks() - self.spawn_time) * 0.005) * 5
        
    def draw(self, screen, camera_x=0, camera_y=0):
        if self.collected:
            return
            
        # Draw powerup box with type-specific color
        colors = {
            PowerupType.BOWLING: PURPLE,
            PowerupType.CAKE: ORANGE,
            PowerupType.ZIPPER: CYAN,
            PowerupType.BUBBLEGUM: GREEN,
            PowerupType.PLUNGER: YELLOW,
            PowerupType.NITRO: BLUE
        }
        
        color = colors.get(self.type, WHITE)
        size = 16
        
        # Draw with bobbing motion
        draw_x = int(self.x - camera_x - size // 2)
        draw_y = int(self.y - camera_y - size // 2 + self.bob_offset)
        
        pygame.draw.rect(screen, color, (draw_x, draw_y, size, size))
        pygame.draw.rect(screen, WHITE, (draw_x, draw_y, size, size), 2)
        
        # Draw type indicator
        font = pygame.font.Font(None, 16)
        text = font.render(self.type.value[0].upper(), True, BLACK)
        text_rect = text.get_rect(center=(draw_x + size//2, draw_y + size//2))
        screen.blit(text, text_rect)

class Projectile:
    def __init__(self, x, y, angle, speed, projectile_type: PowerupType, owner_id):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.type = projectile_type
        self.owner_id = owner_id
        self.lifetime = 5.0  # 5 seconds max
        self.active = True
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.active = False
            
        return self.active
        
    def draw(self, screen, camera_x=0, camera_y=0):
        if not self.active:
            return
            
        colors = {
            PowerupType.BOWLING: PURPLE,
            PowerupType.CAKE: ORANGE,
            PowerupType.PLUNGER: YELLOW
        }
        
        color = colors.get(self.type, WHITE)
        size = 8 if self.type == PowerupType.BOWLING else 6
        
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        pygame.draw.circle(screen, color, (draw_x, draw_y), size)
        pygame.draw.circle(screen, WHITE, (draw_x, draw_y), size, 2)

class Kart:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], name: str, is_player: bool = False):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 300  # pixels per second
        self.acceleration = 200
        self.turn_speed = 3.0
        self.color = color
        self.name = name
        self.is_player = is_player
        
        # Powerup system
        self.current_powerup = None
        self.powerup_cooldown = 0
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.friction = 0.95
        
        # Drift/Skid system
        self.drift_accumulator = 0
        self.drift_direction = 0  # -1 left, 1 right, 0 none
        self.nitro_boost = 0
        self.is_drifting = False
        
        # Battle stats
        self.lives = 3
        self.lap = 1
        self.checkpoint = 0
        
        # Visual effects
        self.particles = []
        self.hit_effect_time = 0
        
        # AI properties
        self.ai_target_x = x
        self.ai_target_y = y
        self.ai_decision_timer = 0
        
    def update(self, dt, keys_pressed=None, mouse_pos=None):
        # Update powerup cooldown
        if self.powerup_cooldown > 0:
            self.powerup_cooldown -= dt
            
        # Update hit effect
        if self.hit_effect_time > 0:
            self.hit_effect_time -= dt
        
        # Handle input (player or AI)
        if self.is_player and keys_pressed:
            self._handle_player_input(dt, keys_pressed)
        else:
            self._handle_ai_input(dt)
            
        # Apply nitro boost
        boost_multiplier = 1.0 + (self.nitro_boost * 0.5)
        if self.nitro_boost > 0:
            self.nitro_boost = max(0, self.nitro_boost - dt)
            
        # Physics update
        self._update_physics(dt, boost_multiplier)
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Generate drift particles
        if self.is_drifting and self.speed > 50:
            self._create_drift_particles()
            
        # Generate nitro particles
        if self.nitro_boost > 0:
            self._create_nitro_particles()
    
    def _handle_player_input(self, dt, keys_pressed):
        # Acceleration
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt)
        elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.speed = max(-self.max_speed * 0.5, self.speed - self.acceleration * dt)
        else:
            self.speed *= 0.98  # Natural deceleration
            
        # Turning
        if self.speed > 10:  # Only turn when moving
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                self.angle -= self.turn_speed * dt * (self.speed / self.max_speed)
                self._handle_drift(dt, -1)
            elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.angle += self.turn_speed * dt * (self.speed / self.max_speed)
                self._handle_drift(dt, 1)
            else:
                self._end_drift()
                
        # Use powerup
        if keys_pressed[pygame.K_SPACE] and self.current_powerup and self.powerup_cooldown <= 0:
            self._use_powerup()
    
    def _handle_ai_input(self, dt):
        # Simple AI: move toward target, use powerups occasionally
        self.ai_decision_timer += dt
        
        if self.ai_decision_timer > 0.5:  # Make decisions every 0.5 seconds
            self.ai_decision_timer = 0
            
            # Choose new target (random movement for arena)
            self.ai_target_x = self.x + random.uniform(-200, 200)
            self.ai_target_y = self.y + random.uniform(-200, 200)
            
            # Use powerup randomly
            if self.current_powerup and random.random() < 0.3:
                self._use_powerup()
        
        # Move toward target
        dx = self.ai_target_x - self.x
        dy = self.ai_target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 20:
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - self.angle
            
            # Normalize angle difference
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Turn toward target
            if abs(angle_diff) > 0.1:
                turn_direction = 1 if angle_diff > 0 else -1
                self.angle += self.turn_speed * dt * turn_direction
                self._handle_drift(dt, turn_direction)
            else:
                self._end_drift()
                
            # Accelerate
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt)
        else:
            self.speed *= 0.95
    
    def _handle_drift(self, dt, direction):
        if not self.is_drifting:
            self.is_drifting = True
            self.drift_direction = direction
            self.drift_accumulator = 0
            
        if self.drift_direction == direction:
            self.drift_accumulator += dt
            
            # Grant nitro boost for successful drifts
            if self.drift_accumulator > 1.0:  # 1 second of drifting
                self.nitro_boost = min(2.0, self.nitro_boost + 0.5)
                self.drift_accumulator = 0  # Reset to prevent constant boost
    
    def _end_drift(self):
        self.is_drifting = False
        self.drift_direction = 0
    
    def _update_physics(self, dt, boost_multiplier):
        # Convert speed and angle to velocity
        effective_speed = self.speed * boost_multiplier
        self.velocity_x = math.cos(self.angle) * effective_speed
        self.velocity_y = math.sin(self.angle) * effective_speed
        
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Keep in bounds (for arena phase)
        self.x = max(50, min(WINDOW_WIDTH - 50, self.x))
        self.y = max(50, min(WINDOW_HEIGHT - 50, self.y))
    
    def _create_drift_particles(self):
        for _ in range(2):
            # Create particles behind the kart
            offset_x = -math.cos(self.angle) * 20
            offset_y = -math.sin(self.angle) * 20
            
            particle = Particle(
                self.x + offset_x + random.uniform(-5, 5),
                self.y + offset_y + random.uniform(-5, 5),
                random.uniform(-30, 30),
                random.uniform(-30, 30),
                GRAY,
                0.5,
                random.randint(2, 4)
            )
            self.particles.append(particle)
    
    def _create_nitro_particles(self):
        for _ in range(3):
            offset_x = -math.cos(self.angle) * 25
            offset_y = -math.sin(self.angle) * 25
            
            particle = Particle(
                self.x + offset_x + random.uniform(-3, 3),
                self.y + offset_y + random.uniform(-3, 3),
                -self.velocity_x * 0.5 + random.uniform(-20, 20),
                -self.velocity_y * 0.5 + random.uniform(-20, 20),
                CYAN,
                0.8,
                random.randint(3, 6)
            )
            self.particles.append(particle)
    
    def _use_powerup(self):
        if not self.current_powerup:
            return
            
        self.powerup_cooldown = 1.0  # 1 second cooldown
        
        if self.current_powerup == PowerupType.ZIPPER:
            self.nitro_boost = min(3.0, self.nitro_boost + 1.5)
        elif self.current_powerup == PowerupType.NITRO:
            self.nitro_boost = min(3.0, self.nitro_boost + 2.0)
        elif self.current_powerup in [PowerupType.BOWLING, PowerupType.CAKE, PowerupType.PLUNGER]:
            # Create projectile (handled by game)
            pass
        elif self.current_powerup == PowerupType.BUBBLEGUM:
            # Drop bubblegum behind kart
            pass
            
        self.current_powerup = None
    
    def take_damage(self):
        self.lives -= 1
        self.hit_effect_time = 1.0
        
        # Create explosion particles
        for _ in range(20):
            particle = Particle(
                self.x + random.uniform(-10, 10),
                self.y + random.uniform(-10, 10),
                random.uniform(-100, 100),
                random.uniform(-100, 100),
                random.choice([RED, ORANGE, YELLOW]),
                1.0,
                random.randint(4, 8)
            )
            self.particles.append(particle)
    
    def collect_powerup(self, powerup_type: PowerupType):
        self.current_powerup = powerup_type
    
    def draw(self, screen, camera_x=0, camera_y=0):
        # Draw particles first (behind kart)
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)
            
        # Calculate draw position
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        # Hit effect (flash red)
        kart_color = RED if self.hit_effect_time > 0 else self.color
        
        # Draw kart body
        kart_size = 16
        pygame.draw.circle(screen, kart_color, (draw_x, draw_y), kart_size)
        pygame.draw.circle(screen, WHITE, (draw_x, draw_y), kart_size, 2)
        
        # Draw direction indicator
        end_x = draw_x + math.cos(self.angle) * kart_size
        end_y = draw_y + math.sin(self.angle) * kart_size
        pygame.draw.line(screen, WHITE, (draw_x, draw_y), (end_x, end_y), 3)
        
        # Draw drift indicators
        if self.is_drifting:
            drift_color = YELLOW if self.drift_accumulator > 0.5 else GRAY
            pygame.draw.circle(screen, drift_color, (draw_x, draw_y), kart_size + 5, 3)
        
        # Draw nitro boost indicator
        if self.nitro_boost > 0:
            boost_radius = int(kart_size + 8 + self.nitro_boost * 3)
            pygame.draw.circle(screen, CYAN, (draw_x, draw_y), boost_radius, 2)
        
        # Draw powerup indicator
        if self.current_powerup:
            colors = {
                PowerupType.BOWLING: PURPLE,
                PowerupType.CAKE: ORANGE,
                PowerupType.ZIPPER: CYAN,
                PowerupType.BUBBLEGUM: GREEN,
                PowerupType.PLUNGER: YELLOW,
                PowerupType.NITRO: BLUE
            }
            color = colors.get(self.current_powerup, WHITE)
            pygame.draw.rect(screen, color, (draw_x - 8, draw_y - 25, 16, 10))
        
        # Draw lives (for battle mode)
        if hasattr(self, 'lives') and self.lives > 0:
            for i in range(self.lives):
                life_x = draw_x - 10 + (i * 7)
                life_y = draw_y + 20
                pygame.draw.circle(screen, GREEN, (life_x, life_y), 3)

class SuperTuxKartMiniGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("SuperTuxKart: Kart Combat Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        
        self.phase = GamePhase.MENU
        self.phase_timer = 0
        self.game_start_time = 0
        
        # Game objects
        self.karts = []
        self.powerups = []
        self.projectiles = []
        self.particles = []
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Track progress
        self.circuit_laps_completed = 0
        self.battle_eliminations = 0
        
        # Arena bounds (for final phase)
        self.arena_radius = 300
        
    def initialize_game(self):
        self.karts = []
        self.powerups = []
        self.projectiles = []
        self.particles = []
        
        # Create player kart
        player_kart = Kart(200, 400, BLUE, "Player", True)
        self.karts.append(player_kart)
        
        # Create AI karts
        ai_colors = [RED, GREEN, YELLOW, PURPLE, ORANGE]
        for i in range(4):
            ai_kart = Kart(
                200 + (i + 1) * 60,
                400 + random.uniform(-50, 50),
                ai_colors[i % len(ai_colors)],
                f"AI_{i+1}",
                False
            )
            self.karts.append(ai_kart)
        
        self.game_start_time = pygame.time.get_ticks()
        
    def start_speed_circuit(self):
        self.phase = GamePhase.SPEED_CIRCUIT
        self.phase_timer = 120.0  # 2 minutes
        self.initialize_game()
        
        # Position karts for racing
        for i, kart in enumerate(self.karts):
            kart.x = 100
            kart.y = 300 + i * 40
            kart.angle = 0
            
        # Spawn initial powerups
        self.spawn_powerups_circuit()
        
    def start_arena_battle(self):
        self.phase = GamePhase.ARENA_BATTLE
        self.phase_timer = 180.0  # 3 minutes
        
        # Filter out eliminated karts
        self.karts = [kart for kart in self.karts if kart.lives > 0]
        
        # Position remaining karts in arena
        arena_center_x = WINDOW_WIDTH // 2
        arena_center_y = WINDOW_HEIGHT // 2
        
        for i, kart in enumerate(self.karts):
            angle = (i / len(self.karts)) * 2 * math.pi
            kart.x = arena_center_x + math.cos(angle) * 150
            kart.y = arena_center_y + math.sin(angle) * 150
            kart.angle = angle + math.pi  # Face center
            
        # Clear circuit powerups and spawn arena powerups
        self.powerups = []
        self.spawn_powerups_arena()
        
    def start_final_showdown(self):
        self.phase = GamePhase.FINAL_SHOWDOWN
        self.phase_timer = 120.0  # 2 minutes
        
        # Only keep top 2 karts
        surviving_karts = [kart for kart in self.karts if kart.lives > 0]
        surviving_karts.sort(key=lambda k: k.lives, reverse=True)
        self.karts = surviving_karts[:2]
        
        # Reset arena radius for shrinking effect
        self.arena_radius = 300
        
    def spawn_powerups_circuit(self):
        # Spawn powerups along the racing line
        powerup_types = list(PowerupType)
        for i in range(8):
            x = 200 + i * 150
            y = 300 + math.sin(i * 0.5) * 100
            powerup_type = random.choice(powerup_types)
            self.powerups.append(Powerup(powerup_type, x, y))
            
    def spawn_powerups_arena(self):
        # Spawn powerups randomly in arena
        arena_center_x = WINDOW_WIDTH // 2
        arena_center_y = WINDOW_HEIGHT // 2
        
        powerup_types = list(PowerupType)
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(50, 250)
            x = arena_center_x + math.cos(angle) * radius
            y = arena_center_y + math.sin(angle) * radius
            powerup_type = random.choice(powerup_types)
            self.powerups.append(Powerup(powerup_type, x, y))
    
    def update_game(self, dt, keys_pressed):
        # Update phase timer
        self.phase_timer -= dt
        
        # Phase transitions
        if self.phase == GamePhase.SPEED_CIRCUIT and self.phase_timer <= 0:
            self.phase = GamePhase.PHASE_TRANSITION
            self.phase_timer = 3.0  # 3 second transition
        elif self.phase == GamePhase.PHASE_TRANSITION and self.phase_timer <= 0:
            self.start_arena_battle()
        elif self.phase == GamePhase.ARENA_BATTLE:
            living_karts = [k for k in self.karts if k.lives > 0]
            if len(living_karts) <= 2 or self.phase_timer <= 0:
                self.start_final_showdown()
        elif self.phase == GamePhase.FINAL_SHOWDOWN:
            living_karts = [k for k in self.karts if k.lives > 0]
            if len(living_karts) <= 1 or self.phase_timer <= 0:
                self.phase = GamePhase.GAME_OVER
                
        # Update karts
        for kart in self.karts:
            if kart.lives > 0:
                kart.update(dt, keys_pressed if kart.is_player else None)
                
        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)
            
        # Check powerup collection
        for kart in self.karts:
            if kart.lives > 0:
                for powerup in self.powerups:
                    if not powerup.collected:
                        distance = math.sqrt((kart.x - powerup.x)**2 + (kart.y - powerup.y)**2)
                        if distance < 30:
                            powerup.collected = True
                            kart.collect_powerup(powerup.type)
                            
        # Handle projectile creation from powerup usage
        for kart in self.karts:
            if (kart.powerup_cooldown == 1.0 and  # Just used powerup
                kart.current_powerup is None and
                hasattr(kart, '_last_powerup_used')):
                
                if kart._last_powerup_used in [PowerupType.BOWLING, PowerupType.CAKE, PowerupType.PLUNGER]:
                    projectile = Projectile(
                        kart.x, kart.y, kart.angle, 200,
                        kart._last_powerup_used, id(kart)
                    )
                    self.projectiles.append(projectile)
                    
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.update(dt)]
        
        # Check projectile collisions
        for projectile in self.projectiles[:]:
            for kart in self.karts:
                if kart.lives > 0 and id(kart) != projectile.owner_id:
                    distance = math.sqrt((kart.x - projectile.x)**2 + (kart.y - projectile.y)**2)
                    if distance < 25:
                        kart.take_damage()
                        projectile.active = False
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break
                        
        # Update camera to follow player
        player_kart = next((k for k in self.karts if k.is_player), None)
        if player_kart:
            self.camera_x = player_kart.x - WINDOW_WIDTH // 2
            self.camera_y = player_kart.y - WINDOW_HEIGHT // 2
            
        # Shrink arena in final showdown
        if self.phase == GamePhase.FINAL_SHOWDOWN:
            self.arena_radius = max(100, 300 - (120 - self.phase_timer) * 2)
            
            # Damage karts outside arena
            arena_center_x = WINDOW_WIDTH // 2
            arena_center_y = WINDOW_HEIGHT // 2
            
            for kart in self.karts:
                if kart.lives > 0:
                    distance = math.sqrt((kart.x - arena_center_x)**2 + (kart.y - arena_center_y)**2)
                    if distance > self.arena_radius:
                        # Push kart back toward center
                        angle_to_center = math.atan2(arena_center_y - kart.y, arena_center_x - kart.x)
                        kart.x += math.cos(angle_to_center) * 50 * dt
                        kart.y += math.sin(angle_to_center) * 50 * dt
                        
                        # Damage over time
                        if random.random() < 0.02:  # 2% chance per frame
                            kart.take_damage()
        
        # Respawn powerups periodically
        if len(self.powerups) < 8 and random.random() < 0.01:
            if self.phase == GamePhase.SPEED_CIRCUIT:
                self.spawn_powerups_circuit()
            else:
                self.spawn_powerups_arena()
                
        # Remove collected powerups
        self.powerups = [p for p in self.powerups if not p.collected]
    
    def draw_track(self):
        if self.phase == GamePhase.SPEED_CIRCUIT:
            # Draw simple oval track
            track_points = []
            for i in range(100):
                angle = (i / 100) * 2 * math.pi
                x = 600 + math.cos(angle) * 400 - self.camera_x
                y = 400 + math.sin(angle) * 200 - self.camera_y
                track_points.append((x, y))
                
            if len(track_points) > 2:
                pygame.draw.lines(self.screen, TRACK_BORDER, True, track_points, 5)
        else:
            # Draw arena boundary
            arena_center_x = WINDOW_WIDTH // 2 - self.camera_x
            arena_center_y = WINDOW_HEIGHT // 2 - self.camera_y
            
            if self.phase == GamePhase.FINAL_SHOWDOWN:
                # Draw shrinking arena
                pygame.draw.circle(self.screen, RED, 
                                 (int(arena_center_x), int(arena_center_y)), 
                                 int(self.arena_radius), 3)
            else:
                # Draw full arena
                pygame.draw.circle(self.screen, TRACK_BORDER,
                                 (int(arena_center_x), int(arena_center_y)), 
                                 300, 3)
    
    def draw_ui(self):
        # Phase indicator
        phase_names = {
            GamePhase.SPEED_CIRCUIT: "Speed Circuit",
            GamePhase.PHASE_TRANSITION: "Entering Arena...",
            GamePhase.ARENA_BATTLE: "Arena Battle",
            GamePhase.FINAL_SHOWDOWN: "Final Showdown!",
            GamePhase.GAME_OVER: "Game Over"
        }
        
        phase_text = self.font.render(phase_names.get(self.phase, ""), True, WHITE)
        self.screen.blit(phase_text, (20, 20))
        
        # Timer
        if self.phase_timer > 0:
            timer_text = self.font.render(f"Time: {int(self.phase_timer)}", True, WHITE)
            self.screen.blit(timer_text, (20, 60))
            
        # Player stats
        player_kart = next((k for k in self.karts if k.is_player), None)
        if player_kart:
            # Lives
            lives_text = self.font.render(f"Lives: {player_kart.lives}", True, WHITE)
            self.screen.blit(lives_text, (20, 100))
            
            # Speed
            speed_text = self.small_font.render(f"Speed: {int(player_kart.speed)}", True, WHITE)
            self.screen.blit(speed_text, (20, 140))
            
            # Nitro
            if player_kart.nitro_boost > 0:
                nitro_text = self.small_font.render(f"Nitro: {player_kart.nitro_boost:.1f}", True, CYAN)
                self.screen.blit(nitro_text, (20, 160))
                
            # Current powerup
            if player_kart.current_powerup:
                powerup_text = self.small_font.render(f"Powerup: {player_kart.current_powerup.value}", True, YELLOW)
                self.screen.blit(powerup_text, (20, 180))
        
        # Leaderboard
        living_karts = [k for k in self.karts if k.lives > 0]
        living_karts.sort(key=lambda k: k.lives, reverse=True)
        
        leaderboard_y = WINDOW_HEIGHT - 200
        leaderboard_text = self.font.render("Survivors:", True, WHITE)
        self.screen.blit(leaderboard_text, (WINDOW_WIDTH - 200, leaderboard_y))
        
        for i, kart in enumerate(living_karts[:5]):
            y = leaderboard_y + 40 + i * 25
            name = kart.name if kart.name != "Player" else "YOU"
            kart_text = self.small_font.render(f"{name}: {kart.lives} lives", True, kart.color)
            self.screen.blit(kart_text, (WINDOW_WIDTH - 200, y))
        
        # Instructions
        if self.phase == GamePhase.SPEED_CIRCUIT:
            instructions = [
                "Collect powerups and learn to drift!",
                "Hold turns to build nitro boost",
                "WASD to move, SPACE to use powerup"
            ]
        elif self.phase in [GamePhase.ARENA_BATTLE, GamePhase.FINAL_SHOWDOWN]:
            instructions = [
                "Battle for survival!",
                "Hit enemies with powerups",
                "Last kart standing wins!"
            ]
        else:
            instructions = []
            
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(inst_text, (20, WINDOW_HEIGHT - 80 + i * 20))
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Title
        title = self.title_font.render("SUPERTUXKART", True, WHITE)
        subtitle = self.font.render("Kart Combat Arena", True, YELLOW)
        
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 280))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Description
        desc_lines = [
            "Experience SuperTuxKart's most thrilling moments!",
            "",
            "Phase 1: Master drift-boost racing on the speed circuit",
            "Phase 2: Survive intense powerup combat in the arena", 
            "Phase 3: Final showdown with shrinking battlefield",
            "",
            "Features authentic kart physics, spectacular effects,",
            "and the strategic powerup combat that made",
            "SuperTuxKart a 129MB racing masterpiece!",
            "",
            "Press SPACE to start your engines!"
        ]
        
        y_offset = 350
        for line in desc_lines:
            if line:
                color = YELLOW if "Phase" in line else WHITE
                text = self.small_font.render(line, True, color)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 25
    
    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # Determine winner
        living_karts = [k for k in self.karts if k.lives > 0]
        if living_karts:
            winner = max(living_karts, key=lambda k: k.lives)
            if winner.is_player:
                title_text = "VICTORY!"
                title_color = GREEN
            else:
                title_text = "DEFEAT"
                title_color = RED
        else:
            title_text = "DRAW"
            title_color = YELLOW
            
        title = self.title_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Game stats
        total_time = (pygame.time.get_ticks() - self.game_start_time) // 1000
        stats = [
            f"Total Game Time: {total_time // 60}:{total_time % 60:02d}",
            f"Karts Remaining: {len([k for k in self.karts if k.lives > 0])}",
            "",
            "Thank you for experiencing SuperTuxKart!",
            "Download the full game for 20+ tracks,",
            "multiplayer racing, and much more!",
            "",
            "Press R to restart or Q to quit"
        ]
        
        y_offset = 300
        for stat in stats:
            if stat:
                color = YELLOW if "SuperTuxKart" in stat or "Download" in stat else WHITE
                text = self.font.render(stat, True, color)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 40
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.phase == GamePhase.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_speed_circuit()
                elif self.phase == GamePhase.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.phase = GamePhase.MENU
                    elif event.key == pygame.K_q:
                        return False
                        
        return True
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            running = self.handle_events()
            
            keys_pressed = pygame.key.get_pressed()
            
            # Update game state
            if self.phase in [GamePhase.SPEED_CIRCUIT, GamePhase.ARENA_BATTLE, 
                             GamePhase.FINAL_SHOWDOWN, GamePhase.PHASE_TRANSITION]:
                self.update_game(dt, keys_pressed)
            
            # Draw everything
            self.screen.fill(GRASS_COLOR)
            
            if self.phase == GamePhase.MENU:
                self.draw_menu()
            elif self.phase == GamePhase.GAME_OVER:
                self.draw_game_over()
            else:
                # Draw track/arena
                self.draw_track()
                
                # Draw powerups
                for powerup in self.powerups:
                    powerup.draw(self.screen, self.camera_x, self.camera_y)
                
                # Draw projectiles
                for projectile in self.projectiles:
                    projectile.draw(self.screen, self.camera_x, self.camera_y)
                
                # Draw karts
                for kart in self.karts:
                    if kart.lives > 0:
                        kart.draw(self.screen, self.camera_x, self.camera_y)
                
                # Draw UI
                self.draw_ui()
                
                # Phase transition overlay
                if self.phase == GamePhase.PHASE_TRANSITION:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                    overlay.set_alpha(128)
                    overlay.fill(BLACK)
                    self.screen.blit(overlay, (0, 0))
                    
                    transition_text = self.title_font.render("ENTERING ARENA", True, RED)
                    text_rect = transition_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                    self.screen.blit(transition_text, text_rect)
            
            pygame.display.flip()
            
        pygame.quit()

if __name__ == "__main__":
    print("🏎️  SuperTuxKart: Kart Combat Arena")
    print("Based on the 129MB open-source racing masterpiece!")
    print("Experience authentic kart physics and spectacular powerup combat!")
    
    try:
        game = SuperTuxKartMiniGame()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()