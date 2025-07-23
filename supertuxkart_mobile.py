#!/usr/bin/env python3
"""
SuperTuxKart Mobile: Kart Combat Arena
Android-optimized version with touch controls

Built with Kivy for cross-platform mobile deployment
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.event import EventDispatcher
from kivy.core.audio import SoundLoader

import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Mobile optimizations
Window.size = (720, 1280)  # Portrait mode for mobile

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

class MobileParticle:
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
        
        # Apply gravity
        if self.color in [(1, 0.5, 0, 1), (1, 0, 0, 1), (1, 1, 0, 1)]:
            self.vy -= 100 * dt
            
        return self.lifetime > 0

class MobilePowerup:
    def __init__(self, powerup_type: PowerupType, x: float, y: float):
        self.type = powerup_type
        self.x = x
        self.y = y
        self.collected = False
        self.bob_offset = 0
        self.spawn_time = 0
        
    def update(self, dt):
        self.spawn_time += dt
        self.bob_offset = math.sin(self.spawn_time * 3) * 5

class MobileProjectile:
    def __init__(self, x, y, angle, speed, projectile_type: PowerupType, owner_id):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.type = projectile_type
        self.owner_id = owner_id
        self.lifetime = 5.0
        self.active = True
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.active = False
            
        return self.active

class MobileKart:
    def __init__(self, x: float, y: float, color: Tuple[float, float, float, float], name: str, is_player: bool = False):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 200  # Reduced for mobile
        self.acceleration = 150
        self.turn_speed = 2.5
        self.color = color
        self.name = name
        self.is_player = is_player
        
        # Game mechanics
        self.current_powerup = None
        self.powerup_cooldown = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.friction = 0.95
        
        # Drift system
        self.drift_accumulator = 0
        self.drift_direction = 0
        self.nitro_boost = 0
        self.is_drifting = False
        
        # Battle stats
        self.lives = 3
        self.particles = []
        self.hit_effect_time = 0
        
        # AI
        self.ai_target_x = x
        self.ai_target_y = y
        self.ai_decision_timer = 0
        
        # Mobile touch controls
        self.touch_acceleration = 0
        self.touch_steering = 0
        
    def update(self, dt, touch_controls=None):
        # Update timers
        if self.powerup_cooldown > 0:
            self.powerup_cooldown -= dt
        if self.hit_effect_time > 0:
            self.hit_effect_time -= dt
        
        # Handle input
        if self.is_player and touch_controls:
            self._handle_touch_input(dt, touch_controls)
        else:
            self._handle_ai_input(dt)
            
        # Apply physics
        boost_multiplier = 1.0 + (self.nitro_boost * 0.4)
        if self.nitro_boost > 0:
            self.nitro_boost = max(0, self.nitro_boost - dt)
            
        self._update_physics(dt, boost_multiplier)
        
        # Update particles (simplified for mobile)
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Generate effects
        if self.is_drifting and self.speed > 30:
            self._create_drift_particles()
        if self.nitro_boost > 0:
            self._create_nitro_particles()
    
    def _handle_touch_input(self, dt, controls):
        # Use touch controls passed from game
        acceleration = controls.get('acceleration', 0)
        steering = controls.get('steering', 0)
        
        # Acceleration
        if acceleration > 0:
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt * acceleration)
        elif acceleration < 0:
            self.speed = max(-self.max_speed * 0.5, self.speed + self.acceleration * dt * acceleration)
        else:
            self.speed *= 0.98
            
        # Steering
        if self.speed > 10 and abs(steering) > 0.1:
            self.angle += self.turn_speed * dt * steering * (self.speed / self.max_speed)
            self._handle_drift(dt, steering)
        else:
            self._end_drift()
    
    def _handle_ai_input(self, dt):
        # Simplified AI for mobile performance
        self.ai_decision_timer += dt
        
        if self.ai_decision_timer > 1.0:
            self.ai_decision_timer = 0
            
            # Random movement
            self.ai_target_x = self.x + random.uniform(-150, 150)
            self.ai_target_y = self.y + random.uniform(-150, 150)
            
        # Move toward target
        dx = self.ai_target_x - self.x
        dy = self.ai_target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 20:
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - self.angle
            
            # Normalize angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            # Turn and accelerate
            if abs(angle_diff) > 0.2:
                turn_direction = 1 if angle_diff > 0 else -1
                self.angle += self.turn_speed * dt * turn_direction
                
            self.speed = min(self.max_speed, self.speed + self.acceleration * dt)
        else:
            self.speed *= 0.95
    
    def _handle_drift(self, dt, direction):
        if not self.is_drifting:
            self.is_drifting = True
            self.drift_direction = 1 if direction > 0 else -1
            self.drift_accumulator = 0
            
        if (self.drift_direction > 0 and direction > 0) or (self.drift_direction < 0 and direction < 0):
            self.drift_accumulator += dt
            
            if self.drift_accumulator > 0.8:
                self.nitro_boost = min(2.0, self.nitro_boost + 0.4)
                self.drift_accumulator = 0
    
    def _end_drift(self):
        self.is_drifting = False
        self.drift_direction = 0
    
    def _update_physics(self, dt, boost_multiplier):
        effective_speed = self.speed * boost_multiplier
        self.velocity_x = math.cos(self.angle) * effective_speed
        self.velocity_y = math.sin(self.angle) * effective_speed
        
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Keep in screen bounds
        self.x = max(30, min(Window.width - 30, self.x))
        self.y = max(30, min(Window.height - 30, self.y))
    
    def _create_drift_particles(self):
        # Simplified particles for mobile
        if len(self.particles) < 20:  # Limit particles
            particle = MobileParticle(
                self.x + random.uniform(-10, 10),
                self.y + random.uniform(-10, 10),
                random.uniform(-20, 20),
                random.uniform(-20, 20),
                (0.5, 0.5, 0.5, 0.7),
                0.5,
                3
            )
            self.particles.append(particle)
    
    def _create_nitro_particles(self):
        if len(self.particles) < 15:
            particle = MobileParticle(
                self.x + random.uniform(-5, 5),
                self.y + random.uniform(-5, 5),
                -self.velocity_x * 0.3 + random.uniform(-15, 15),
                -self.velocity_y * 0.3 + random.uniform(-15, 15),
                (0, 0.8, 1, 0.8),
                0.6,
                4
            )
            self.particles.append(particle)
    
    def use_powerup(self):
        if not self.current_powerup or self.powerup_cooldown > 0:
            return False
            
        self.powerup_cooldown = 1.0
        
        if self.current_powerup == PowerupType.ZIPPER:
            self.nitro_boost = min(2.5, self.nitro_boost + 1.2)
        elif self.current_powerup == PowerupType.NITRO:
            self.nitro_boost = min(2.5, self.nitro_boost + 1.8)
            
        self.current_powerup = None
        return True
    
    def take_damage(self):
        self.lives -= 1
        self.hit_effect_time = 1.0
        
        # Explosion particles
        for _ in range(10):  # Reduced for mobile
            particle = MobileParticle(
                self.x + random.uniform(-8, 8),
                self.y + random.uniform(-8, 8),
                random.uniform(-60, 60),
                random.uniform(-60, 60),
                random.choice([(1, 0, 0, 1), (1, 0.5, 0, 1), (1, 1, 0, 1)]),
                0.8,
                random.randint(4, 7)
            )
            self.particles.append(particle)
    
    def collect_powerup(self, powerup_type: PowerupType):
        self.current_powerup = powerup_type

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Game state
        self.phase = GamePhase.MENU
        self.phase_timer = 0
        self.game_start_time = 0
        
        # Game objects
        self.karts = []
        self.powerups = []
        self.projectiles = []
        self.particles = []
        
        # Camera (simplified for mobile)
        self.camera_x = 0
        self.camera_y = 0
        
        # Arena
        self.arena_radius = 250
        
        # Touch controls
        self.touch_controls = {
            'acceleration': 0,
            'steering': 0,
            'powerup': False
        }
        
        # UI elements
        self.setup_ui()
        
        # Start game loop
        Clock.schedule_interval(self.update, 1.0/30.0)  # 30 FPS for mobile
        
    def setup_ui(self):
        # Control buttons layout
        controls_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.15),
            pos_hint={'x': 0, 'y': 0}
        )
        
        # Steering buttons
        left_btn = Button(
            text='◄',
            size_hint=(0.2, 1),
            font_size='24sp'
        )
        left_btn.bind(on_press=lambda x: self.set_steering(-1))
        left_btn.bind(on_release=lambda x: self.set_steering(0))
        
        # Acceleration buttons
        accel_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 1))
        
        forward_btn = Button(
            text='▲ ACCEL',
            size_hint=(1, 0.5),
            font_size='16sp'
        )
        forward_btn.bind(on_press=lambda x: self.set_acceleration(1))
        forward_btn.bind(on_release=lambda x: self.set_acceleration(0))
        
        brake_btn = Button(
            text='▼ BRAKE',
            size_hint=(1, 0.5),
            font_size='16sp'
        )
        brake_btn.bind(on_press=lambda x: self.set_acceleration(-1))
        brake_btn.bind(on_release=lambda x: self.set_acceleration(0))
        
        accel_layout.add_widget(forward_btn)
        accel_layout.add_widget(brake_btn)
        
        # Right turn button
        right_btn = Button(
            text='►',
            size_hint=(0.2, 1),
            font_size='24sp'
        )
        right_btn.bind(on_press=lambda x: self.set_steering(1))
        right_btn.bind(on_release=lambda x: self.set_steering(0))
        
        # Powerup button
        powerup_btn = Button(
            text='POWER',
            size_hint=(0.2, 1),
            font_size='14sp'
        )
        powerup_btn.bind(on_press=self.use_powerup)
        
        # Add buttons to layout
        controls_layout.add_widget(left_btn)
        controls_layout.add_widget(accel_layout)
        controls_layout.add_widget(right_btn)
        controls_layout.add_widget(powerup_btn)
        
        self.add_widget(controls_layout)
        
        # Game info labels
        self.phase_label = Label(
            text='SuperTuxKart Mobile',
            size_hint=(1, 0.08),
            pos_hint={'x': 0, 'y': 0.92},
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.phase_label)
        
        self.stats_label = Label(
            text='',
            size_hint=(0.5, 0.1),
            pos_hint={'x': 0, 'y': 0.82},
            font_size='14sp',
            color=(1, 1, 1, 1),
            text_size=(Window.width * 0.5, None),
            halign='left'
        )
        self.add_widget(self.stats_label)
        
        # Menu button
        self.menu_button = Button(
            text='START GAME',
            size_hint=(0.6, 0.1),
            pos_hint={'x': 0.2, 'y': 0.4},
            font_size='18sp'
        )
        self.menu_button.bind(on_press=self.start_game)
        self.add_widget(self.menu_button)
    
    def set_acceleration(self, value):
        self.touch_controls['acceleration'] = value
    
    def set_steering(self, value):
        self.touch_controls['steering'] = value
    
    def use_powerup(self, instance):
        player_kart = next((k for k in self.karts if k.is_player), None)
        if player_kart:
            if player_kart.use_powerup():
                # Create projectile if applicable
                if player_kart.current_powerup in [PowerupType.BOWLING, PowerupType.CAKE, PowerupType.PLUNGER]:
                    projectile = MobileProjectile(
                        player_kart.x, player_kart.y, player_kart.angle, 150,
                        player_kart.current_powerup, id(player_kart)
                    )
                    self.projectiles.append(projectile)
    
    def start_game(self, instance):
        if self.phase == GamePhase.MENU:
            self.initialize_game()
            self.phase = GamePhase.SPEED_CIRCUIT
            self.phase_timer = 90.0  # Shorter for mobile
            self.menu_button.opacity = 0
            self.game_start_time = Clock.get_time()
        elif self.phase == GamePhase.GAME_OVER:
            self.phase = GamePhase.MENU
            self.menu_button.opacity = 1
            self.menu_button.text = 'START GAME'
    
    def initialize_game(self):
        self.karts = []
        self.powerups = []
        self.projectiles = []
        
        # Create player kart
        player_kart = MobileKart(
            Window.width * 0.2, Window.height * 0.5,
            (0, 0.4, 1, 1), "Player", True
        )
        self.karts.append(player_kart)
        
        # Create AI karts (fewer for mobile)
        ai_colors = [(1, 0.2, 0.2, 1), (0.2, 1, 0.2, 1), (1, 1, 0.2, 1)]
        for i in range(3):
            ai_kart = MobileKart(
                Window.width * 0.2 + (i + 1) * 50,
                Window.height * 0.5 + random.uniform(-30, 30),
                ai_colors[i],
                f"AI_{i+1}",
                False
            )
            self.karts.append(ai_kart)
        
        # Spawn powerups
        self.spawn_powerups()
    
    def spawn_powerups(self):
        powerup_types = list(PowerupType)
        for _ in range(6):  # Fewer powerups for mobile
            x = random.uniform(50, Window.width - 50)
            y = random.uniform(200, Window.height - 200)
            powerup_type = random.choice(powerup_types)
            self.powerups.append(MobilePowerup(powerup_type, x, y))
    
    def update(self, dt):
        if self.phase == GamePhase.MENU or self.phase == GamePhase.GAME_OVER:
            return
            
        # Update phase timer
        self.phase_timer -= dt
        
        # Phase transitions (simplified)
        if self.phase == GamePhase.SPEED_CIRCUIT and self.phase_timer <= 0:
            self.phase = GamePhase.ARENA_BATTLE
            self.phase_timer = 120.0
        elif self.phase == GamePhase.ARENA_BATTLE:
            living_karts = [k for k in self.karts if k.lives > 0]
            if len(living_karts) <= 1 or self.phase_timer <= 0:
                self.phase = GamePhase.GAME_OVER
                self.menu_button.opacity = 1
                self.menu_button.text = 'RESTART'
        
        # Update game objects
        for kart in self.karts:
            if kart.lives > 0:
                kart.update(dt, self.touch_controls if kart.is_player else None)
        
        for powerup in self.powerups:
            powerup.update(dt)
        
        self.projectiles = [p for p in self.projectiles if p.update(dt)]
        
        # Check collisions
        self.check_collisions()
        
        # Update camera to follow player
        player_kart = next((k for k in self.karts if k.is_player), None)
        if player_kart:
            self.camera_x = player_kart.x - Window.width // 2
            self.camera_y = player_kart.y - Window.height // 2
        
        # Respawn powerups
        if len(self.powerups) < 4 and random.random() < 0.02:
            self.spawn_powerups()
        
        # Remove collected powerups
        self.powerups = [p for p in self.powerups if not p.collected]
        
        # Update UI
        self.update_ui()
        
        # Trigger redraw
        self.canvas.clear()
        with self.canvas:
            self.draw_game()
    
    def check_collisions(self):
        # Powerup collection
        for kart in self.karts:
            if kart.lives > 0:
                for powerup in self.powerups:
                    if not powerup.collected:
                        distance = math.sqrt((kart.x - powerup.x)**2 + (kart.y - powerup.y)**2)
                        if distance < 25:
                            powerup.collected = True
                            kart.collect_powerup(powerup.type)
        
        # Projectile hits
        for projectile in self.projectiles[:]:
            for kart in self.karts:
                if kart.lives > 0 and id(kart) != projectile.owner_id:
                    distance = math.sqrt((kart.x - projectile.x)**2 + (kart.y - projectile.y)**2)
                    if distance < 20:
                        kart.take_damage()
                        projectile.active = False
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break
    
    def update_ui(self):
        # Phase label
        phase_names = {
            GamePhase.SPEED_CIRCUIT: "Speed Circuit",
            GamePhase.ARENA_BATTLE: "Arena Battle", 
            GamePhase.GAME_OVER: "Game Over"
        }
        self.phase_label.text = phase_names.get(self.phase, "SuperTuxKart Mobile")
        
        # Stats label
        player_kart = next((k for k in self.karts if k.is_player and k.lives > 0), None)
        if player_kart:
            stats_text = f"Lives: {player_kart.lives}\n"
            stats_text += f"Speed: {int(player_kart.speed)}\n"
            if player_kart.nitro_boost > 0:
                stats_text += f"Nitro: {player_kart.nitro_boost:.1f}\n"
            if player_kart.current_powerup:
                stats_text += f"Power: {player_kart.current_powerup.value}\n"
            stats_text += f"Time: {int(self.phase_timer)}"
            self.stats_label.text = stats_text
    
    def draw_game(self):
        # Draw background
        Color(0.2, 0.6, 0.2, 1)  # Green grass
        Rectangle(pos=(0, 0), size=(Window.width, Window.height))
        
        # Draw arena boundary for battle phase
        if self.phase == GamePhase.ARENA_BATTLE:
            Color(1, 1, 0, 1)  # Yellow boundary
            center_x = Window.width // 2 - self.camera_x
            center_y = Window.height // 2 - self.camera_y
            Line(circle=(center_x, center_y, 200), width=3)
        
        # Draw powerups
        for powerup in self.powerups:
            if not powerup.collected:
                # Powerup colors
                colors = {
                    PowerupType.BOWLING: (0.8, 0.2, 0.8, 1),
                    PowerupType.CAKE: (1, 0.6, 0, 1),
                    PowerupType.ZIPPER: (0, 1, 1, 1),
                    PowerupType.BUBBLEGUM: (0.2, 1, 0.2, 1),
                    PowerupType.PLUNGER: (1, 1, 0.2, 1),
                    PowerupType.NITRO: (0.2, 0.2, 1, 1)
                }
                
                color = colors.get(powerup.type, (1, 1, 1, 1))
                Color(*color)
                
                draw_x = powerup.x - self.camera_x
                draw_y = powerup.y - self.camera_y + powerup.bob_offset
                Rectangle(pos=(draw_x - 8, draw_y - 8), size=(16, 16))
        
        # Draw projectiles
        for projectile in self.projectiles:
            if projectile.active:
                Color(1, 0.5, 0, 1)  # Orange projectiles
                draw_x = projectile.x - self.camera_x
                draw_y = projectile.y - self.camera_y
                Ellipse(pos=(draw_x - 5, draw_y - 5), size=(10, 10))
        
        # Draw karts
        for kart in self.karts:
            if kart.lives > 0:
                # Draw particles first
                for particle in kart.particles:
                    Color(*particle.color)
                    p_x = particle.x - self.camera_x
                    p_y = particle.y - self.camera_y
                    Ellipse(pos=(p_x - particle.size, p_y - particle.size), 
                           size=(particle.size * 2, particle.size * 2))
                
                # Draw kart
                kart_color = (1, 0.2, 0.2, 1) if kart.hit_effect_time > 0 else kart.color
                Color(*kart_color)
                
                draw_x = kart.x - self.camera_x
                draw_y = kart.y - self.camera_y
                Ellipse(pos=(draw_x - 12, draw_y - 12), size=(24, 24))
                
                # Draw direction indicator
                Color(1, 1, 1, 1)
                end_x = draw_x + math.cos(kart.angle) * 15
                end_y = draw_y + math.sin(kart.angle) * 15
                Line(points=[draw_x, draw_y, end_x, end_y], width=2)
                
                # Draw drift indicator
                if kart.is_drifting:
                    Color(1, 1, 0, 0.5)
                    Ellipse(pos=(draw_x - 18, draw_y - 18), size=(36, 36))
                
                # Draw nitro indicator
                if kart.nitro_boost > 0:
                    Color(0, 1, 1, 0.7)
                    boost_size = 30 + kart.nitro_boost * 8
                    Ellipse(pos=(draw_x - boost_size//2, draw_y - boost_size//2), 
                           size=(boost_size, boost_size))

class SuperTuxKartMobileApp(App):
    def build(self):
        self.title = 'SuperTuxKart Mobile'
        game = GameWidget()
        return game
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass

if __name__ == '__main__':
    SuperTuxKartMobileApp().run()