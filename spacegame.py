import pygame
import sys
import math
import random
import os

# Chỉ số
score = 0 
screen_shake = 0  
player_invincible = False  
player_invincible_time = 0  
player_health = 100  
player_money = 0
max_player_health = 100  
double_shot = False  
triple_shot = False  

pygame.init()
pygame.mixer.init()  

# Cấu hình màn hình
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Shooter")

# Wave transition effect
def show_wave_transition(wave_num):
    transition = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    font_large = pygame.font.SysFont(None, 100)
    font_medium = pygame.font.SysFont(None, 50)
    
    if wave_num % 5 == 0:
        wave_text = font_large.render(f"BOSS WAVE {wave_num}", True, (255, 50, 50))
        sub_text = font_medium.render("Prepare for battle!", True, (255, 100, 100))
    else:
        wave_text = font_large.render(f"Wave {wave_num}", True, (200, 200, 255))
        sub_text = font_medium.render("Get ready!", True, WHITE)
    
    # Animation
    for i in range(60):  
        screen.blit(background, (0, 0))
        
        for particle in particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                particles.remove(particle)
            else:
                particle.draw()
        
        alpha = 255
        if i < 15:  
            alpha = int(255 * i / 15)
        elif i >= 45:  
            alpha = int(255 * (60 - i) / 15)
        
        transition.fill((0, 0, 0, alpha))
        
        shadow_offset = 3
        shadow_text = wave_text.copy()
        shadow_text.set_alpha(alpha // 2)
        screen.blit(shadow_text, 
                  (screen_width//2 - wave_text.get_width()//2 + shadow_offset, 
                   screen_height//2 - wave_text.get_height()//2 - 30 + shadow_offset))
        
        wave_text_surf = wave_text.copy()
        wave_text_surf.set_alpha(alpha)
        screen.blit(wave_text_surf, 
                  (screen_width//2 - wave_text.get_width()//2, 
                   screen_height//2 - wave_text.get_height()//2 - 30))
                   
        shadow_sub = sub_text.copy()
        shadow_sub.set_alpha(alpha // 2)
        screen.blit(shadow_sub, 
                  (screen_width//2 - sub_text.get_width()//2 + shadow_offset, 
                   screen_height//2 + 30 + shadow_offset))
                   
        sub_text_surf = sub_text.copy()
        sub_text_surf.set_alpha(alpha)
        screen.blit(sub_text_surf, 
                  (screen_width//2 - sub_text.get_width()//2, 
                   screen_height//2 + 30))
        
        if random.random() < 0.3:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            color = (255, 50, 50) if wave_num % 5 == 0 else (200, 200, 255)
            particles.append(Particle(x, y, color, speed=1, size=3, lifetime=30))
        
        pygame.display.update()
        pygame.time.wait(16)  

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
PURPLE = (180, 60, 220)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Background
background = pygame.Surface((screen_width, screen_height))
background.fill((5, 5, 30))  
for _ in range(100):  
    x = random.randint(0, screen_width)
    y = random.randint(0, screen_height)
    radius = random.randint(1, 3)
    brightness = random.randint(150, 255)
    pygame.draw.circle(background, (brightness, brightness, brightness), (x, y), radius)

# Add some nebulas for visual interest :)
for _ in range(5):
    nebula_x = random.randint(0, screen_width)
    nebula_y = random.randint(0, screen_height)
    nebula_size = random.randint(50, 150)
    nebula_color = (
        random.randint(20, 70),
        random.randint(20, 70),
        random.randint(60, 120)
    )
    
    for i in range(30):
        size = nebula_size - i*2
        if size <= 0:
            break
        alpha = 200 - i*6
        if alpha < 0:
            alpha = 0
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*nebula_color, alpha), (0, 0, size, size))
        background.blit(s, (nebula_x - size//2, nebula_y - size//2))

particles = []

# Particle system
class Particle:
    def __init__(self, x, y, color, speed=1, size=3, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.speed_x = random.uniform(-speed, speed)
        self.speed_y = random.uniform(-speed, speed)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self):
        if self.lifetime > 0 and self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

# Player Skills System
class Skill:
    def __init__(self, name, key, cooldown, energy_cost, icon_color):
        self.name = name
        self.key = key 
        self.cooldown = cooldown 
        self.energy_cost = energy_cost
        self.last_used_time = 0
        self.is_active = False
        self.active_duration = 0  
        self.active_start_time = 0
        self.icon_color = icon_color
        self.level = 1 
        
    def can_use(self, current_time, current_energy):
        return (current_time - self.last_used_time >= self.cooldown and 
                current_energy >= self.energy_cost and
                not self.is_active)
                
    def use(self, current_time, current_energy):
        if self.can_use(current_time, current_energy):
            self.last_used_time = current_time
            if self.active_duration > 0:
                self.is_active = True
                self.active_start_time = current_time
            return True
        return False
        
    def update(self, current_time):
        if self.is_active and self.active_duration > 0:
            if current_time - self.active_start_time >= self.active_duration:
                self.is_active = False
                
    def get_cooldown_percentage(self, current_time):
        time_since_use = current_time - self.last_used_time
        return min(1.0, time_since_use / self.cooldown)
        
    def draw_icon(self, x, y, size=40):
        icon_bg = pygame.Surface((size, size), pygame.SRCALPHA)
        
        pygame.draw.rect(icon_bg, (*self.icon_color, 180), (0, 0, size, size), border_radius=5)
        
        current_time = pygame.time.get_ticks()
        cooldown_percent = self.get_cooldown_percentage(current_time)
        
        if cooldown_percent < 1.0:
            cooldown_height = int(size * (1 - cooldown_percent))
            pygame.draw.rect(icon_bg, (0, 0, 0, 150), 
                           (0, 0, size, cooldown_height), 
                           border_radius=5 if cooldown_height == size else 0)
            
        border_color = (255, 255, 255) if self.is_active else (150, 150, 150)
        pygame.draw.rect(icon_bg, border_color, (0, 0, size, size), width=2, border_radius=5)
            
        font = pygame.font.SysFont(None, 20)
        key_text = font.render(pygame.key.name(self.key).upper(), True, WHITE)
        icon_bg.blit(key_text, (size//2 - key_text.get_width()//2, size - key_text.get_height() - 5))
        
        for i in range(self.level):
            pygame.draw.circle(icon_bg, WHITE, (5 + i*8, 5), 3)
        
        screen.blit(icon_bg, (x, y))
        
        font = pygame.font.SysFont(None, 16)
        name_text = font.render(self.name, True, WHITE)
        screen.blit(name_text, (x, y + size + 2))
        
        energy_text = font.render(f"{self.energy_cost} E", True, (100, 200, 255))
        screen.blit(energy_text, (x + size - energy_text.get_width(), y + size + 2))

# Skill definitions
class DashSkill(Skill):
    def __init__(self):
        super().__init__("Dash", pygame.K_q, 3000, 20, BLUE)
        self.dash_speed = 15
        self.dash_duration = 200  
        self.active_duration = self.dash_duration
        
    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.cooldown = max(1500, self.cooldown - 500) 
            self.dash_speed += 5  
            return True
        return False

class BombSkill(Skill):
    def __init__(self):
        super().__init__("Bomb", pygame.K_e, 8000, 30, RED)
        self.radius = 100
        self.damage = 100
        
    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.radius += 50
            self.damage += 50
            return True
        return False
        
    def activate(self, player_x, player_y):
        for i in range(30):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, self.radius)
            particles.append(Particle(
                player_x + math.cos(angle) * distance,
                player_y + math.sin(angle) * distance,
                RED if i % 3 == 0 else YELLOW,
                speed=3,
                size=5,
                lifetime=30
            ))
        
        screen_shake = 15
        
        return player_x + player_width/2, player_y + player_height/2, self.radius, self.damage

class ShieldSkill(Skill):
    def __init__(self):
        super().__init__("Shield", pygame.K_r, 15000, 25, CYAN)
        self.duration = 5000  # 5 seconds
        self.active_duration = self.duration
        
    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.duration += 2000
            self.active_duration = self.duration
            return True
        return False

class MultiShotSkill(Skill):
    def __init__(self):
        super().__init__("Multi", pygame.K_f, 10000, 20, PURPLE)
        self.shots = 8
        self.active_duration = 0  
        
    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.shots += 4
            return True
        return False
        
    def activate(self, player_x, player_y):
        bullets_to_add = []
        center_x = player_x + player_width / 2
        center_y = player_y + player_height / 2
        
        for i in range(self.shots):
            angle = 2 * math.pi * i / self.shots
            direction = (math.cos(angle), math.sin(angle))
            
            bullet = Bullet(center_x, center_y, direction)
            bullet.color = PURPLE
            bullets_to_add.append(bullet)
            
        return bullets_to_add

# Player
player_width, player_height = 50, 50
player_x, player_y = (screen_width - player_width) // 2, (screen_height - player_height) // 2
player_speed = 5
player_slide_speed = player_speed*2  
player_direction = 0, 0  
player_is_sliding = False
slide_duration = 100  
slide_cooldown = 2000  
last_slide_time = pygame.time.get_ticks()
energy = 100  
energy_regen_rate = 10 
player_invincible = False
player_invincible_time = 0
player_invincible_duration = 1000 

# Player's skill (using E key)
player_skill = BombSkill()  
player_skill.key = pygame.K_e  
player_skill.level = 1  
player_skill.max_level = 5  

boss_kills = 0

enemy_speeds = [2, 3, 4, 5]

# Đạn
bullet_radius = 5
bullet_speed = 10
bullet_damage = 20
bullet_cooldown = 500  

# Game effect variables
screen_shake = 0
double_shot = False
triple_shot = False

# Sound effects
shoot_sound = None
hit_sound = None
enemy_death_sound = None
player_hit_sound = None

# Create simple placeholder graphics
player_img = pygame.Surface((player_width, player_height), pygame.SRCALPHA)
pygame.draw.polygon(player_img, BLUE, [(0, player_height), (player_width/2, 0), (player_width, player_height)])
pygame.draw.polygon(player_img, (100, 100, 255), [(10, player_height-10), (player_width/2, 10), (player_width-10, player_height-10)])

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.radius = bullet_radius
        self.damage = bullet_damage
        self.trail = []  
        self.color = (200, 200, 255)  

    def update(self):
        if len(self.trail) > 5:  
            self.trail.pop(0)
        self.trail.append((self.x, self.y))
        
        self.x += self.direction[0] * bullet_speed
        self.y += self.direction[1] * bullet_speed
        
        if random.random() < 0.3:
            particles.append(Particle(self.x, self.y, self.color, speed=0.5, size=2, lifetime=10))

    def draw(self):
        # Draw trail
        for i, pos in enumerate(self.trail):
            if len(self.trail) > 1:
                alpha = int(255 * (i / len(self.trail)))
                size = int(self.radius * (i / len(self.trail)))
                if size > 0:
                    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
                    screen.blit(s, (pos[0] - size, pos[1] - size))
        
        # Draw bullet
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Glow effect
        s = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, 100), (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(s, (self.x - self.radius * 2, self.y - self.radius * 2))

def select_item(item_index):
    global selected_items, items_to_sell
    if 0 <= item_index < len(items_to_sell):
        item = items_to_sell[item_index]
        item_data = shop_items[item]
        
        has_reached_max = (item_data["max_purchases"] != -1 and 
                         item_data["purchased"] >= item_data["max_purchases"])
        
        if not has_reached_max:
            if item in selected_items:
                selected_items.remove(item)
            else:
                if player_money >= item_data["price"]:
                    selected_items.append(item)

def buy_selected_items():
    global player_money, selected_items, items_to_sell
    
    total_cost = sum(shop_items[item]["price"] for item in selected_items)
    
    if player_money >= total_cost:
        player_money -= total_cost
        
        for item in selected_items[:]:
            apply_item_effect(item)
            shop_items[item]["purchased"] += 1
        
        for _ in range(20):
            particles.append(Particle(
                player_x + random.randint(0, player_width),
                player_y + random.randint(0, player_height),
                YELLOW,
                speed=2,
                size=4,
                lifetime=30
            ))
        
        selected_items.clear()
        
        items_to_sell = [item for item in items_to_sell if 
                       shop_items[item]["max_purchases"] == -1 or 
                       shop_items[item]["purchased"] < shop_items[item]["max_purchases"]]

def leave_shop():
    global is_wave_shop, selected_items, items_to_sell
    is_wave_shop = False
    selected_items = []
    items_to_sell = []

def apply_item_effect(item):
    global energy_regen_rate, bullet_speed, bullet_radius
    global bullet_cooldown, player_health, max_player_health
    global double_shot, triple_shot, player_invincible, player_invincible_time

    if item == "Health Upgrade":
        player_health = min(max_player_health, player_health + 25)
    elif item == "Energy Upgrade":
        energy_regen_rate += 5
    elif item == "Bullet Speed Upgrade":
        bullet_speed += 2
    elif item == "Bullet Size Upgrade":
        bullet_radius += 2
    elif item == "Double Shot":
        double_shot = True
        triple_shot = False  
    elif item == "Triple Shot":
        triple_shot = True
        double_shot = False 
    elif item == "Shield":
        player_invincible = True
        player_invincible_time = pygame.time.get_ticks()
    elif item == "Max Health Up":
        max_player_health += 25
        player_health = min(max_player_health, player_health + 25)
    elif item == "Fire Rate Up":
        bullet_cooldown = max(200, bullet_cooldown - 100)  
    elif item == "Skill Upgrade":
        # Upgrade the player's skill
        if player_skill.level < player_skill.max_level:
            player_skill.level += 1
            
            if isinstance(player_skill, BombSkill):
                player_skill.radius += 30
                player_skill.damage += 40
                player_skill.cooldown = max(3000, player_skill.cooldown - 500)
            
            for i in range(20):
                angle = 2 * math.pi * i / 20
                distance = 100
                particles.append(Particle(
                    player_x + player_width/2 + math.cos(angle) * distance,
                    player_y + player_height/2 + math.sin(angle) * distance,
                    (255, 100, 0),
                    speed=2,
                    size=4,
                    lifetime=40
                ))
        
    # Create particles to show effect
    for _ in range(20):
        particles.append(Particle(
            player_x + random.randint(0, player_width),
            player_y + random.randint(0, player_height),
            (200, 255, 200),
            speed=2,
            size=3,
            lifetime=30
        ))

def draw_player(x, y):
    center_x, center_y = x + player_width / 2, y + player_height / 2
    
    player_shape = pygame.Surface((player_width, player_height), pygame.SRCALPHA)
    
    if player_direction == (0, 0):  
        pygame.draw.polygon(player_shape, BLUE, [
            (player_width/2, 0),
            (player_width, player_height/2),
            (player_width/2, player_height),
            (0, player_height/2)
        ])
        pygame.draw.polygon(player_shape, (100, 100, 255), [
            (player_width/2, player_height/4),
            (player_width*3/4, player_height/2),
            (player_width/2, player_height*3/4),
            (player_width/4, player_height/2)
        ])
    else:
        dx, dy = player_direction
        angle = math.atan2(dy, dx)
        
        tip_x = player_width/2 + math.cos(angle) * player_width/2
        tip_y = player_height/2 + math.sin(angle) * player_height/2
        
        perp_angle = angle + math.pi/2
        perp_x = math.cos(perp_angle) * player_width/4
        perp_y = math.sin(perp_angle) * player_height/4
        
        back_x = player_width/2 - math.cos(angle) * player_width/3
        back_y = player_height/2 - math.sin(angle) * player_height/3
        
        pygame.draw.polygon(player_shape, BLUE, [
            (tip_x, tip_y),
            (back_x + perp_x, back_y + perp_y),
            (back_x - perp_x, back_y - perp_y)
        ])
        
        pygame.draw.polygon(player_shape, (100, 100, 255), [
            (player_width/2 + math.cos(angle) * player_width/4, 
             player_height/2 + math.sin(angle) * player_height/4),
            (back_x + perp_x/2, back_y + perp_y/2),
            (back_x - perp_x/2, back_y - perp_y/2)
        ])
    
    if player_direction != (0, 0):
        engine_x = center_x - math.cos(angle) * player_width/2
        engine_y = center_y - math.sin(angle) * player_height/2
        
        if random.random() < 0.3:
            particles.append(Particle(
                engine_x, engine_y,
                (100, 150, 255) if not player_is_sliding else (100, 200, 255),
                speed=1.5 if not player_is_sliding else 3,
                size=3 if not player_is_sliding else 5,
                lifetime=10 if not player_is_sliding else 15
            ))
    
    screen.blit(player_shape, (x, y))
    
    if player_is_sliding:
        glow = pygame.Surface((player_width*2, player_height*2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (100, 100, 255, 100), (0, 0, player_width*2, player_height*2))
        screen.blit(glow, (x - player_width/2, y - player_height/2))
        
        for _ in range(2):
            particles.append(Particle(
                x + random.randint(0, player_width),
                y + random.randint(0, player_height),
                (150, 150, 255),
                speed=2,
                size=4,
                lifetime=10
            ))
    
    if player_invincible:
        inv_intensity = (pygame.time.get_ticks() % 500) / 500.0  
        glow = pygame.Surface((player_width*2, player_height*2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 255, 255, int(100 * inv_intensity)), 
                          (0, 0, player_width*2, player_height*2))
        screen.blit(glow, (x - player_width/2, y - player_height/2))

def draw_energy_bar():
    energy_bar_width = 100
    energy_bar_height = 10
    energy_bar_x = 10
    energy_bar_y = 10
    
    for i in range(energy_bar_width):
        gradient_color = (
            int(20 + (i / energy_bar_width) * 30),
            int(20 + (i / energy_bar_width) * 30),
            int(60 + (i / energy_bar_width) * 60)
        )
        pygame.draw.line(screen, gradient_color, 
                        (energy_bar_x + i, energy_bar_y), 
                        (energy_bar_x + i, energy_bar_y + energy_bar_height))
    
    for i in range(int(energy)):
        gradient_color = (
            int(30 + (i / 100) * 50),  
            int(100 + (i / 100) * 100),
            int(200 + (i / 100) * 55)
        )
        pygame.draw.line(screen, gradient_color, 
                        (energy_bar_x + i, energy_bar_y), 
                        (energy_bar_x + i, energy_bar_y + energy_bar_height))
    
    pygame.draw.rect(screen, WHITE, 
                    (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height), 1)
    
    font = pygame.font.SysFont(None, 20)
    label = font.render("Energy", True, WHITE)
    screen.blit(label, (energy_bar_x + energy_bar_width + 5, energy_bar_y))
    
    current_time = pygame.time.get_ticks()
    if current_time - last_slide_time < slide_cooldown:
        cooldown_percent = (current_time - last_slide_time) / slide_cooldown
        cooldown_width = int(energy_bar_width * cooldown_percent)
        pygame.draw.rect(screen, (100, 100, 100), 
                        (energy_bar_x, energy_bar_y + energy_bar_height + 2, cooldown_width, 3))

def draw_health_bar():
    health_bar_width = 100
    health_bar_height = 10
    health_bar_x = 10
    health_bar_y = 30
    
    for i in range(health_bar_width):
        gradient_color = (
            int(40 + (i / health_bar_width) * 40),
            int(10 + (i / health_bar_width) * 30),
            int(10 + (i / health_bar_width) * 30)
        )
        pygame.draw.line(screen, gradient_color, 
                        (health_bar_x + i, health_bar_y), 
                        (health_bar_x + i, health_bar_y + health_bar_height))
    
    for i in range(min(int(player_health * health_bar_width / max_player_health), health_bar_width)):
        if player_health > 70:
            gradient_color = (
                int(100 + (i / 100) * 50),
                int(200 + (i / 100) * 55),
                int(30 + (i / 100) * 50)
            )
        elif player_health > 30:
            gradient_color = (
                int(200 + (i / 100) * 55),
                int(200 + (i / 100) * 55),
                int(30 + (i / 100) * 50)
            )
        else:
            gradient_color = (
                int(200 + (i / 100) * 55),
                int(30 + (i / 100) * 50),
                int(30 + (i / 100) * 50)
            )
        pygame.draw.line(screen, gradient_color, 
                        (health_bar_x + i, health_bar_y), 
                        (health_bar_x + i, health_bar_y + health_bar_height))
    
    pygame.draw.rect(screen, WHITE, 
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
    
    font = pygame.font.SysFont(None, 20)
    label = font.render("Health", True, WHITE)
    screen.blit(label, (health_bar_x + health_bar_width + 5, health_bar_y))

def game_over(score):
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill((0, 0, 0))
    
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        
        font = pygame.font.SysFont(None, 100)
        shadow_text = font.render("Game Over", True, (100, 0, 0))
        text = font.render("Game Over", True, RED)
        screen.blit(shadow_text, (screen_width//2 - text.get_width()//2 + 3, screen_height//2 - text.get_height()//2 + 3))
        screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - text.get_height()//2))
        
        font = pygame.font.SysFont(None, 50)
        shadow_score_text = font.render(f"Score: {score}", True, (100, 100, 100))
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(shadow_score_text, (screen_width//2 - score_text.get_width()//2 + 2, 
                                    screen_height//2 + score_text.get_height() + 2))
        screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, 
                            screen_height//2 + score_text.get_height()))
        
        pygame.display.update()
        pygame.time.wait(20)
    
    waiting = True
    font = pygame.font.SysFont(None, 30)
    restart_text = font.render("Press SPACE to restart or ESC to quit", True, WHITE)
    
    while waiting:
        screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, 
                                screen_height//2 + 150))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    reset_game()
                    waiting = False
                    return
        
        pygame.time.wait(50)

def reset_game():
    global player_x, player_y, player_health, energy, wave, score, player_money
    global bullets, enemies, enemies_for_money, boss_spawned, is_wave_shop
    global boss_kills, player_skill
    
    player_x, player_y = (screen_width - player_width) // 2, (screen_height - player_height) // 2
    player_health = 100
    energy = 100
    
    wave = 0
    score = 0
    player_money = 0
    boss_kills = 0
    
    player_skill.level = 1
    player_skill.radius = 100 
    player_skill.damage = 100
    player_skill.cooldown = 8000
    
    bullets = []
    enemies = []
    enemies_for_money = []
    boss_spawned = False
    is_wave_shop = False

def aim_closest_enemy(x, y):
    closest_distance = float('inf')
    closest_enemy = None
    for enemy in enemies:
        dx = enemy.x - x
        dy = enemy.y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance < closest_distance:
            closest_distance = distance
            closest_enemy = enemy
    if closest_enemy is not None:
        dx = closest_enemy.x - x
        dy = closest_enemy.y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        direction = dx / distance, dy / distance
        return direction
    return 0, 0
    
shop_items = {
    "Health Upgrade": {
        "price": 50,
        "description": "Restore 25 health points",
        "max_purchases": -1, 
        "purchased": 0
    },
    "Energy Upgrade": {
        "price": 30,
        "description": "Increase energy regeneration by 5",
        "max_purchases": 5,
        "purchased": 0
    },
    "Bullet Speed Upgrade": {
        "price": 20,
        "description": "Increase bullet speed by 2",
        "max_purchases": 3,
        "purchased": 0
    },
    "Bullet Size Upgrade": {
        "price": 15,
        "description": "Increase bullet size by 2",
        "max_purchases": 3,
        "purchased": 0
    },
    "Double Shot": {
        "price": 80,
        "description": "Fire two bullets at once",
        "max_purchases": 1,
        "purchased": 0
    },
    "Triple Shot": {
        "price": 150,
        "description": "Fire three bullets in a spread pattern",
        "max_purchases": 1,
        "purchased": 0
    },
    "Shield": {
        "price": 60,
        "description": "Temporary invincibility for 5 seconds",
        "max_purchases": -1, 
        "purchased": 0
    },
    "Max Health Up": {
        "price": 100,
        "description": "Increase maximum health by 25",
        "max_purchases": 3,
        "purchased": 0
    },
    "Fire Rate Up": {
        "price": 70,
        "description": "Decrease bullet cooldown by 100ms",
        "max_purchases": 3,
        "purchased": 0
    },
    "Skill Upgrade": {
        "price": 50,  
        "description": "Upgrade your E skill to next level",
        "max_purchases": -1,  
        "purchased": 0
    }
}

# Shop
selected_items = []  
max_player_health = 100  

def generate_shop_items():
    global items_to_sell
    all_available_items = []
    
    for item_name, item_data in shop_items.items():
        if item_name != "Skill Upgrade" and (item_data["max_purchases"] == -1 or item_data["purchased"] < item_data["max_purchases"]):
            all_available_items.append(item_name)
    
    # Select 3 random items
    num_random_items = min(3, len(all_available_items))
    if num_random_items > 0:
        random_items = random.sample(all_available_items, num_random_items)
        items_to_sell = random_items + ["Skill Upgrade"]
    else:
        items_to_sell = ["Skill Upgrade"]

def draw_shop_info():
    shop_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    shop_surface.fill((0, 0, 0, 200)) 
    screen.blit(shop_surface, (0, 0))
    
    font_large = pygame.font.SysFont(None, 60)
    header_text = font_large.render("SHOP", True, WHITE)
    screen.blit(header_text, (screen_width//2 - header_text.get_width()//2, 30))
    
    font_medium = pygame.font.SysFont(None, 40)
    wave_text = font_medium.render(f"Wave {wave} Completed!", True, (200, 200, 255))
    screen.blit(wave_text, (screen_width//2 - wave_text.get_width()//2, 100))
    
    money_text = font_medium.render(f"Your Money: {player_money}", True, YELLOW)
    screen.blit(money_text, (screen_width//2 - money_text.get_width()//2, 150))
    
    font = pygame.font.SysFont(None, 30)
    item_spacing = 80
    
    total_items_height = len(items_to_sell) * item_spacing
    start_y = screen_height // 2 - total_items_height // 2
    
    # Mouse interaction
    global shop_buttons
    shop_buttons = []
    
    for i, item in enumerate(items_to_sell):
        item_data = shop_items[item]
        
        price = item_data["price"]
        if item == "Skill Upgrade":
            if player_skill.level >= player_skill.max_level:
                has_reached_max = True
                price_text = "MAX LEVEL"
            else:
                has_reached_max = False
                price = 50 + boss_kills * 50
                price_text = f"{price} Money"
        else:
            has_reached_max = (item_data["max_purchases"] != -1 and 
                             item_data["purchased"] >= item_data["max_purchases"])
            price_text = f"{price} Money"
            
        can_afford = player_money >= price
        
        text_y = start_y + i * item_spacing
        
        button_width = 500
        button_height = 65
        button_x = screen_width//2 - button_width//2
        button_y = text_y - 10
        
        if item in selected_items:
            button_color = (100, 150, 100)  
        elif has_reached_max:
            button_color = (100, 100, 100) 
        elif can_afford:
            button_color = (50, 50, 80) 
        else:
            button_color = (80, 50, 50) 
        
        pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height), 0, 10)
        
        shop_buttons.append({
            "rect": pygame.Rect(button_x, button_y, button_width, button_height),
            "item": item,
            "index": i
        })
        
        if has_reached_max:
            text_color = (150, 150, 150) 
        elif can_afford:
            text_color = (200, 255, 200)  
        else:
            text_color = (255, 150, 150) 
        
        # Format
        item_text = font.render(f"{i + 1}. {item}: {price_text}", True, text_color)
        screen.blit(item_text, (screen_width//2 - item_text.get_width()//2, text_y))
        
        # Item description
        if item == "Skill Upgrade":
            desc_text = font.render(f"{item_data['description']} (Current: Level {player_skill.level}/{player_skill.max_level})", True, (180, 180, 180))
        else:
            desc_text = font.render(item_data["description"], True, (180, 180, 180))
        screen.blit(desc_text, (screen_width//2 - desc_text.get_width()//2, text_y + 25))
        
        if item != "Skill Upgrade" and item_data["max_purchases"] != -1:
            purchase_info = f"{item_data['purchased']}/{item_data['max_purchases']}"
            purchase_text = font.render(purchase_info, True, (150, 150, 150))
            screen.blit(purchase_text, (button_x + button_width - purchase_text.get_width() - 10, text_y))
    
    # Button
    buy_button_width = 300
    buy_button_height = 50
    buy_button_x = screen_width//2 - buy_button_width//2
    buy_button_y = screen_height - 120
    
    pygame.draw.rect(screen, (50, 100, 50) if selected_items else (70, 70, 70), 
                   (buy_button_x, buy_button_y, buy_button_width, buy_button_height), 0, 10)
    
    global buy_button_rect
    buy_button_rect = pygame.Rect(buy_button_x, buy_button_y, buy_button_width, buy_button_height)
    
    buy_text = font.render("Buy Selected Items", True, WHITE)
    screen.blit(buy_text, (screen_width//2 - buy_text.get_width()//2, buy_button_y + buy_button_height//2 - buy_text.get_height()//2))
    
    leave_button_width = 200
    leave_button_height = 40
    leave_button_x = screen_width//2 - leave_button_width//2
    leave_button_y = screen_height - 60
    
    pygame.draw.rect(screen, (100, 50, 50), 
                   (leave_button_x, leave_button_y, leave_button_width, leave_button_height), 0, 10)
    
    global leave_button_rect
    leave_button_rect = pygame.Rect(leave_button_x, leave_button_y, leave_button_width, leave_button_height)
    
    leave_text = font.render("Skip Shop", True, WHITE)
    screen.blit(leave_text, (screen_width//2 - leave_text.get_width()//2, leave_button_y + leave_button_height//2 - leave_text.get_height()//2))
    
    # Instructions
    instruction_y = screen_height - 200
    inst_font = pygame.font.SysFont(None, 25)
    
    inst1 = inst_font.render("Click on items or press 1-4 to select", True, (180, 180, 180))
    screen.blit(inst1, (screen_width//2 - inst1.get_width()//2, instruction_y))
    
    inst2 = inst_font.render("Press ENTER or click 'Buy Selected Items'", True, (180, 180, 180))
    screen.blit(inst2, (screen_width//2 - inst2.get_width()//2, instruction_y + 25))
    
    # Selected items
    if selected_items:
        selected_y = instruction_y - 40
        total_cost = sum(shop_items[item]["price"] for item in selected_items)
        selected_text = font.render(f"Selected: {', '.join(selected_items)} (Total: {total_cost})", True, YELLOW)
        screen.blit(selected_text, (screen_width//2 - selected_text.get_width()//2, selected_y))

# Tạo biến boss_spawned để theo dõi xem boss đã xuất hiện trong wave chia hết cho 5 chưa
boss_spawned = False

is_wave_shop = False  
items_to_sell = []    
selected_items = []   

# Enemny's design
enemy_colors = {'small': RED, 'medium': (255, 165, 0), 'large': (255, 0, 255), 'boss': (255, 0, 0)}

# Minion
enemy_widths = {'small': 30, 'medium': 40, 'large': 50, 'boss': 100}  # Đổi kích thước của từng loại kẻ địch
enemy_heights = {'small': 30, 'medium': 40, 'large': 50, 'boss': 100}

enemy_types = ['small', 'medium', 'large', 'boss']
enemy_spawn_rates = [0.6, 0.3, 0.1, 0]
enemy_spawn_rate_multiplier = 1.2
enemy_max_healths = {'small': 50, 'medium': 100, 'large': 150, 'boss': 500}

# Boss
boss_width, boss_height = 100, 100
boss_spawn_rate = 0  
boss_max_health = 500 

enemies_for_money = []

# Stats of enemy
SEPARATION_RADIUS = 50  
COHESION_RADIUS = 100   
ALIGNMENT_RADIUS = 80   
SEPARATION_FORCE = 1.5  
COHESION_FORCE = 0.8    
ALIGNMENT_FORCE = 1.0   

# Enemy
class Enemy:
    def __init__(self, enemy_type):
        self.enemy_type = enemy_type
        self.width = enemy_widths[enemy_type]  
        self.height = enemy_heights[enemy_type]  

        # Random pos
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, screen_width - self.width)
            self.y = -self.height
        elif side == 'bottom':
            self.x = random.randint(0, screen_width - self.width)
            self.y = screen_height
        elif side == 'left':
            self.x = -self.width
            self.y = random.randint(0, screen_height - self.height)
        else:
            self.x = screen_width
            self.y = random.randint(0, screen_height - self.height)

        self.health = enemy_max_healths[self.enemy_type]
        self.speed = enemy_speeds[enemy_types.index(self.enemy_type)]  

        self.money = self.health // 4        

        self.spawn_time = pygame.time.get_ticks()  
        self.can_drop_money = random.random() < 0.7  
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.pulse_size = 0
        self.pulse_direction = 1
        self.hit_flash = 0
        
        self.create_enemy_shape()
        
    def create_enemy_shape(self):
        if self.enemy_type == 'small':
            # Triangle enemy
            self.shape = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(self.shape, enemy_colors[self.enemy_type], 
                               [(0, self.height), (self.width/2, 0), (self.width, self.height)])
        elif self.enemy_type == 'medium':
            # Diamond enemy
            self.shape = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(self.shape, enemy_colors[self.enemy_type], 
                               [(self.width/2, 0), (self.width, self.height/2), 
                                (self.width/2, self.height), (0, self.height/2)])
        elif self.enemy_type == 'large':
            # Pentagon enemy
            self.shape = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(self.shape, enemy_colors[self.enemy_type], 
                               [(self.width/2, 0), (self.width, self.height/3), 
                                (self.width*0.8, self.height), (self.width*0.2, self.height),
                                (0, self.height/3)])
        else:  # boss
            # Star enemy for boss
            self.shape = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            center_x, center_y = self.width/2, self.height/2
            points = []
            for i in range(10):  # 5 pointed star (10 points)
                radius = self.width/2 if i % 2 == 0 else self.width/4
                angle = math.pi/2 + 2 * math.pi * i / 10
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(self.shape, enemy_colors[self.enemy_type], points)

    def update(self):
        # Di chuyển đến vị trí của người chơi
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance > 0:
            # Nếu cách xa người chơi, di chuyển theo hướng của người chơi
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed
        else:
            # Nếu đã đạt gần người chơi, thì di chuyển ngẫu nhiên
            self.x += random.uniform(-self.speed, self.speed)
            self.y += random.uniform(-self.speed, self.speed)

        # Kiểm tra va chạm với các kẻ địch khác
        for enemy in enemies:
            if enemy != self:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance < self.width:
                    # Tránh va chạm bằng cách di chuyển ra xa kẻ địch
                    self.x -= dx / distance * (self.width - distance) / 2
                    self.y -= dy / distance * (self.width - distance) / 2
        
        # Update animation
        self.animation_frame += self.animation_speed
        self.pulse_size += 0.1 * self.pulse_direction
        if self.pulse_size > 4:
            self.pulse_direction = -1
        elif self.pulse_size < 0:
            self.pulse_direction = 1
            
        # Decrease hit flash
        if self.hit_flash > 0:
            self.hit_flash -= 0.1

        self.existence_time = pygame.time.get_ticks()
        
    def draw(self):
        # Pulsating size for dynamic effect
        pulse = int(self.pulse_size)
        
        # Base enemy shape with rotation for some types
        if self.enemy_type in ['medium', 'large']:
            # Create a rotated copy of the shape
            angle = (self.animation_frame * 20) % 360  # Rotate medium and large enemies
            rotated = pygame.transform.rotate(self.shape, angle)
            # Get new rect to keep it centered
            rect = rotated.get_rect()
            rect.center = (self.x + self.width/2, self.y + self.height/2)
            screen.blit(rotated, (rect.x - pulse, rect.y - pulse))
        else:
            # Don't rotate small enemies and boss
            screen.blit(self.shape, (self.x - pulse, self.y - pulse))
        
        # Add glowing effect for money-dropping enemies
        if self.can_drop_money:
            glow = pygame.Surface((self.width + 10 + pulse*2, self.height + 10 + pulse*2), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 0, 100), (0, 0, self.width + 10 + pulse*2, self.height + 10 + pulse*2))
            screen.blit(glow, (self.x - 5 - pulse, self.y - 5 - pulse))
        
        # Flash effect when hit
        if self.hit_flash > 0:
            s = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, int(self.hit_flash * 200)), 
                            (0, 0, self.width + 20, self.height + 20))
            screen.blit(s, (self.x - 10, self.y - 10))
            
        # Occasional particle effects
        if random.random() < 0.05:
            particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                enemy_colors[self.enemy_type],
                speed=0.5,
                size=2,
                lifetime=20
            ))

    def draw_health_bar(self):
        health_bar_width = enemy_widths[self.enemy_type]
        health_bar_height = 5
        health_bar_x = self.x
        health_bar_y = self.y - 10
        
        # Health bar background
        pygame.draw.rect(screen, (60, 60, 60), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health bar fill
        health_percent = self.health / enemy_max_healths[self.enemy_type]
        bar_color = (
            min(255, int(255 * (1 - health_percent))),  # Red increases as health decreases
            min(255, int(255 * health_percent)),         # Green decreases as health decreases
            0
        )
        pygame.draw.rect(screen, bar_color, 
                        (health_bar_x, health_bar_y, health_percent * health_bar_width, health_bar_height))
                        
        # Health bar border
        pygame.draw.rect(screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 1)
        
    def take_damage(self, damage):
        self.health -= damage
        self.hit_flash = 1.0  # Set hit flash to full
        
        # Create hit particles
        for _ in range(5):
            particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                WHITE,
                speed=2,
                size=3,
                lifetime=10
            ))
            
    def drop_money(self):
        if self in enemies_for_money:
            global player_money
            time_decay = 0.002  # Tỷ lệ giảm số tiền theo thời gian tồn tại (có thể điều chỉnh).
            money_dropped = max(1, self.money - int(self.existence_time * time_decay))
            player_money += money_dropped
            
            # Create money particles
            for _ in range(10):
                particles.append(Particle(
                    self.x + random.randint(0, self.width),
                    self.y + random.randint(0, self.height),
                    YELLOW,
                    speed=1,
                    size=3,
                    lifetime=30
                ))
                
            enemies_for_money.remove(self)

# Boss
class Boss(Enemy):
    def __init__(self):
        super().__init__('boss')
        self.health = boss_max_health
        self.speed = 2  # Tốc độ di chuyển của boss (có thể điều chỉnh)
        self.attack_cooldown = 3000  # 3 seconds between attacks
        self.last_attack_time = pygame.time.get_ticks()
        self.pulse_size = 0
        self.pulse_direction = 1
        self.glow_intensity = 0
        self.glow_direction = 1
        
        # Boss phases and attacks
        self.max_health = boss_max_health
        self.phase = 1  # Boss starts in phase 1
        self.phase_changed = False
        self.attack_patterns = ['burst', 'spiral', 'wave', 'mines', 'laser']
        self.current_attack = None
        self.attack_timer = 0
        
        # Laser attack variables
        self.laser_target_x = 0
        self.laser_target_y = 0
        self.laser_charging = False
        self.laser_firing = False
        self.laser_width = 0
        self.laser_charge_time = 1500  # Time to charge laser
        self.laser_fire_time = 2000    # Time laser fires
        
        # Mining attack variables
        self.mines = []
        
        # Override shape with a more complex one
        self.create_boss_shape()
        
    def create_boss_shape(self):
        # Create a more detailed boss shape
        self.shape = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Main body (hexagon)
        center_x, center_y = self.width/2, self.height/2
        radius = self.width/2 - 5
        points = []
        for i in range(6):
            angle = 2 * math.pi * i / 6
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(self.shape, (180, 0, 0), points)
        
        # Inner circle
        pygame.draw.circle(self.shape, (255, 50, 50), (center_x, center_y), radius*0.7)
        
        # Core
        pygame.draw.circle(self.shape, (255, 200, 200), (center_x, center_y), radius*0.3)
        
        # Phase indicators
        for i in range(3):
            indicator_x = center_x - radius*0.5 + i*radius*0.5
            indicator_y = center_y + radius*0.5
            indicator_color = (255, 255, 0) if i < self.phase else (100, 100, 100)
            pygame.draw.circle(self.shape, indicator_color, (indicator_x, indicator_y), radius*0.1)

    def update(self):
        # Check for phase transitions
        health_percent = self.health / self.max_health
        new_phase = 3 if health_percent <= 0.3 else (2 if health_percent <= 0.7 else 1)
        
        if new_phase != self.phase and not self.phase_changed:
            self.phase = new_phase
            self.phase_changed = True
            
            # Create phase transition effect
            for _ in range(30):
                particles.append(Particle(
                    self.x + random.randint(0, self.width),
                    self.y + random.randint(0, self.height),
                    (255, 255, 0),
                    speed=3,
                    size=5,
                    lifetime=40
                ))
            
            # Add screen shake
            screen_shake = 10
            
            # Update boss shape
            self.create_boss_shape()
        else:
            self.phase_changed = False
        
        # Movement behavior depends on phase
        if self.phase == 1:
            # Phase 1: Move directly toward player
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance != 0:
                self.x += dx / distance * self.speed
                self.y += dy / distance * self.speed
        elif self.phase == 2:
            # Phase 2: Circle around player
            angle = pygame.time.get_ticks() / 1000  # Time-based angle
            distance = 200  # Distance to keep from player
            target_x = player_x + math.cos(angle) * distance
            target_y = player_y + math.sin(angle) * distance
            
            dx = target_x - self.x
            dy = target_y - self.y
            move_dist = math.sqrt(dx ** 2 + dy ** 2)
            
            if move_dist > self.speed:
                self.x += dx / move_dist * self.speed * 1.5
                self.y += dy / move_dist * self.speed * 1.5
        else:
            # Phase 3: Erratic movement
            current_time = pygame.time.get_ticks()
            angle = current_time / 200  # Faster oscillation
            
            # Move in a figure-8 pattern
            dx = math.sin(angle) * 5
            dy = math.sin(angle * 2) * 3
            
            # Ensure boss stays on screen
            new_x = self.x + dx
            new_y = self.y + dy
            
            if 0 <= new_x <= screen_width - self.width:
                self.x = new_x
            if 0 <= new_y <= screen_height - self.height:
                self.y = new_y
            
        # Update visual effects
        self.animation_frame += self.animation_speed * 0.5  # Slower animation for boss
        
        # Pulsating effect
        self.pulse_size += 0.15 * self.pulse_direction
        if self.pulse_size > 6:
            self.pulse_direction = -1
        elif self.pulse_size < 0:
            self.pulse_direction = 1
            
        # Glow effect
        self.glow_intensity += 0.05 * self.glow_direction
        if self.glow_intensity > 1:
            self.glow_direction = -1
        elif self.glow_intensity < 0.2:
            self.glow_direction = 1
            
        # Decrease hit flash
        if self.hit_flash > 0:
            self.hit_flash -= 0.05
            
        # Update laser targeting if charging
        if self.laser_charging:
            self.attack_timer -= 16  # ~60 FPS
            if self.attack_timer <= 0:
                self.laser_charging = False
                self.laser_firing = True
                self.attack_timer = self.laser_fire_time
                
                # Create laser particles
                laser_angle = math.atan2(self.laser_target_y - (self.y + self.height/2),
                                        self.laser_target_x - (self.x + self.width/2))
                for i in range(30):
                    dist = i * 20
                    particles.append(Particle(
                        self.x + self.width/2 + math.cos(laser_angle) * dist,
                        self.y + self.height/2 + math.sin(laser_angle) * dist,
                        (255, 0, 0),
                        speed=0.5,
                        size=8,
                        lifetime=40
                    ))
        
        # Update laser firing
        if self.laser_firing:
            self.attack_timer -= 16
            if self.attack_timer <= 0:
                self.laser_firing = False
        
        # Update mine positions
        for mine in self.mines[:]:
            mine['timer'] -= 16
            if mine['timer'] <= 0:
                # Explode mine
                for _ in range(15):
                    particles.append(Particle(
                        mine['x'], mine['y'],
                        (255, 100, 0),
                        speed=3,
                        size=4,
                        lifetime=30
                    ))
                self.mines.remove(mine)
                
                # Check if player is in explosion radius
                dx = player_x + player_width/2 - mine['x']
                dy = player_y + player_height/2 - mine['y']
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 100 and not player_invincible:  # 100px explosion radius
                    player_health -= 20
                    
                    # Add screen shake
                    screen_shake = 10
            
        # Check if boss can attack
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.use_skill()
            self.last_attack_time = current_time
            
        self.existence_time = pygame.time.get_ticks()
            
    def draw(self):
        # Pulsating size for dynamic effect
        pulse = int(self.pulse_size)
        
        # Rotated boss shape
        angle = (self.animation_frame * 5) % 360  # Slow rotation for boss
        rotated = pygame.transform.rotate(self.shape, angle)
        # Get new rect to keep it centered
        rect = rotated.get_rect()
        rect.center = (self.x + self.width/2, self.y + self.height/2)
        
        # Glow effect for boss
        glow_size = int(20 * self.glow_intensity)
        if glow_size > 0:
            glow = pygame.Surface((self.width + glow_size*2, self.height + glow_size*2), pygame.SRCALPHA)
            glow_color = (255, 50, 50, int(100 * self.glow_intensity))
            pygame.draw.ellipse(glow, glow_color, (0, 0, self.width + glow_size*2, self.height + glow_size*2))
            screen.blit(glow, (rect.x - glow_size, rect.y - glow_size))
        
        # Draw boss
        screen.blit(rotated, (rect.x - pulse, rect.y - pulse))
        
        # Flash effect when hit
        if self.hit_flash > 0:
            s = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
            pygame.draw.rect(s, (255, 255, 255, int(self.hit_flash * 200)), 
                            (0, 0, self.width + 40, self.height + 40))
            screen.blit(s, (self.x - 20, self.y - 20))
        
        # Boss particles
        if random.random() < 0.3:  # Boss emits more particles
            particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                (255, 50, 50),
                speed=1,
                size=3,
                lifetime=15
            ))
            
        # Draw laser warning indicator
        if self.laser_charging:
            # Draw line from boss to target
            pygame.draw.line(screen, (255, 0, 0, 128), 
                           (self.x + self.width/2, self.y + self.height/2),
                           (self.laser_target_x, self.laser_target_y), 2)
            
            # Draw target indicator
            target_pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 10
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.laser_target_x), int(self.laser_target_y)), 
                             int(10 + target_pulse), 2)
        
        # Draw laser beam
        if self.laser_firing:
            # Calculate angle and endpoints
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            angle = math.atan2(self.laser_target_y - center_y, 
                             self.laser_target_x - center_x)
            
            # Create points for a thick line
            length = 2000  # Long enough to go off screen
            end_x = center_x + math.cos(angle) * length
            end_y = center_y + math.sin(angle) * length
            
            # Draw the laser beam
            laser_width = 20
            points = []
            
            # Create perpendicular vectors for thickness
            perp_x = -math.sin(angle) * laser_width/2
            perp_y = math.cos(angle) * laser_width/2
            
            # Define four corners of the laser beam
            points.append((center_x + perp_x, center_y + perp_y))
            points.append((center_x - perp_x, center_y - perp_y))
            points.append((end_x - perp_x, end_y - perp_y))
            points.append((end_x + perp_x, end_y + perp_y))
            
            # Draw the laser as a polygon
            pygame.draw.polygon(screen, (255, 0, 0), points)
            
            # Draw inner beam
            inner_width = 10
            perp_x = -math.sin(angle) * inner_width/2
            perp_y = math.cos(angle) * inner_width/2
            
            inner_points = []
            inner_points.append((center_x + perp_x, center_y + perp_y))
            inner_points.append((center_x - perp_x, center_y - perp_y))
            inner_points.append((end_x - perp_x, end_y - perp_y))
            inner_points.append((end_x + perp_x, end_y + perp_y))
            
            pygame.draw.polygon(screen, (255, 200, 200), inner_points)
            
            # Check if player is hit by laser
            # Convert laser into line segments
            laser_segments = [
                ((center_x + perp_x, center_y + perp_y), (end_x + perp_x, end_y + perp_y)),
                ((center_x - perp_x, center_y - perp_y), (end_x - perp_x, end_y - perp_y)),
                ((center_x + perp_x, center_y + perp_y), (center_x - perp_x, center_y - perp_y)),
                ((end_x + perp_x, end_y + perp_y), (end_x - perp_x, end_y - perp_y))
            ]
            
            # Player hitbox
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            
            # Check for intersection
            if not player_invincible and player_rect.clipline((center_x, center_y), (end_x, end_y)):
                player_health -= 0.5  # Continuous damage while in laser
                screen_shake = max(screen_shake, 5)
                
                # Create hit particles
                if random.random() < 0.3:
                    particles.append(Particle(
                        player_x + random.randint(0, player_width),
                        player_y + random.randint(0, player_height),
                        (255, 100, 100),
                        speed=1,
                        size=3,
                        lifetime=10
                    ))
                
        # Draw mines
        for mine in self.mines:
            # Pulsating effect
            pulse = abs(math.sin(pygame.time.get_ticks() / 200 + mine['offset'])) * 5
            
            # Draw outer circle
            pygame.draw.circle(screen, (255, 100, 0), 
                             (int(mine['x']), int(mine['y'])), 
                             int(15 + pulse))
            
            # Draw inner circle
            pygame.draw.circle(screen, (255, 200, 0), 
                             (int(mine['x']), int(mine['y'])), 
                             int(10))
            
            # Draw countdown indicator
            remaining = mine['timer'] / 3000  # 3000ms total time
            pygame.draw.arc(screen, (255, 0, 0), 
                          (mine['x'] - 20, mine['y'] - 20, 40, 40),
                          0, remaining * 2 * math.pi, 3)

    # Thêm kỹ năng của boss ở đây (ví dụ: bắn đạn, tấn công mạnh, ...)
    def use_skill(self):
        # Random attack type based on phase
        if self.phase == 1:
            attack_type = random.choice(['burst', 'wave'])
        elif self.phase == 2:
            attack_type = random.choice(['burst', 'spiral', 'mines'])
        else:  # Phase 3
            attack_type = random.choice(['spiral', 'laser', 'mines', 'wave'])
            
        if attack_type == 'burst':
            self.burst_attack()
        elif attack_type == 'spiral':
            self.spiral_attack()
        elif attack_type == 'wave':
            self.wave_attack()
        elif attack_type == 'mines':
            self.mines_attack()
        elif attack_type == 'laser':
            self.laser_attack()
            
    def burst_attack(self):
        # Burst attack: shoot bullets in all directions
        directions = 8 if self.phase == 1 else (12 if self.phase == 2 else 16)
        
        for angle in range(0, 360, 360 // directions):
            rad_angle = math.radians(angle)
            direction = (math.cos(rad_angle), math.sin(rad_angle))
            
            # Create bullet with boss color
            bullet = Bullet(self.x + self.width/2, self.y + self.height/2, direction)
            bullet.color = (255, 50, 50)  # Red bullets for boss
            bullet.damage = 15 + 5 * self.phase  # Damage increases with phase
            bullets.append(bullet)
            
        # Visual effect for attack
        for _ in range(10):
            particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                (255, 200, 200),
                speed=2,
                size=4,
                lifetime=15
            ))
                
    def spiral_attack(self):
        # Create particles in spiral pattern
        center_x, center_y = self.x + self.width/2, self.y + self.height/2
        
        # Number of spiral arms increases with phase
        arms = self.phase
        bullets_per_arm = 8
        
        for arm in range(arms):
            start_angle = arm * (360 / arms)
            for i in range(bullets_per_arm):
                angle = math.radians(start_angle + i * 15)  # 15 degrees between bullets
                
                # Add delay for spiral effect
                delay = i * 100  # milliseconds between bullets
                
                # Schedule bullet creation
                global scheduled_bullets
                scheduled_bullets.append({
                    'x': center_x,
                    'y': center_y,
                    'angle': angle,
                    'delay': delay,
                    'color': (255, 50, 50),
                    'damage': 10 + 5 * self.phase
                })
                
        # Visual effect for attack start
        for _ in range(15):
            particles.append(Particle(
                center_x,
                center_y,
                (255, 50 + random.randint(0, 150), 50),
                speed=2,
                size=4,
                lifetime=20
            ))
                
    def wave_attack(self):
        # Wave attack: bullets towards player
        num_bullets = 5 + self.phase * 2 
        
        for _ in range(num_bullets):
            dx = player_x - (self.x + self.width/2)
            dy = player_y - (self.y + self.height/2)
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Add some randomness to direction
                rand_angle = random.uniform(-0.3, 0.3)
                dir_x = dx / distance * math.cos(rand_angle) - dy / distance * math.sin(rand_angle)
                dir_y = dx / distance * math.sin(rand_angle) + dy / distance * math.cos(rand_angle)
                
                # Create faster bullet with boss color
                bullet = Bullet(self.x + self.width/2, self.y + self.height/2, (dir_x, dir_y))
                bullet.color = (255, 50, 50)  # Red bullets for boss
                bullet.radius = bullet_radius * 1.5  # Larger bullets
                bullet.damage = 15 + 5 * self.phase
                bullets.append(bullet)
        
        # Visual effect for attack
        for _ in range(15):
            particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                (255, 200, 200),
                speed=2,
                size=4,
                lifetime=15
            ))
            
    def mines_attack(self):
        # Place mines around the arena
        num_mines = 3 + self.phase  # More mines in higher phases
        
        for _ in range(num_mines):
            # Find a position not too close to player or other mines
            while True:
                mine_x = random.randint(50, screen_width - 50)
                mine_y = random.randint(50, screen_height - 50)
                
                # Check distance from player
                dx = player_x + player_width/2 - mine_x
                dy = player_y + player_height/2 - mine_y
                dist_to_player = math.sqrt(dx**2 + dy**2)
                
                # Check distance from other mines
                too_close = False
                for mine in self.mines:
                    dx = mine['x'] - mine_x
                    dy = mine['y'] - mine_y
                    if math.sqrt(dx**2 + dy**2) < 100:
                        too_close = True
                        break
                
                if dist_to_player > 150 and not too_close:
                    break
            
            # Add mine
            self.mines.append({
                'x': mine_x,
                'y': mine_y,
                'timer': 3000,  # 3 seconds until explosion
                'offset': random.random() * math.pi * 2  # Random phase for visual effect
            })
            
            # Visual effect for mine placement
            for _ in range(10):
                particles.append(Particle(
                    mine_x, mine_y,
                    (255, 150, 0),
                    speed=1.5,
                    size=3,
                    lifetime=20
                ))
                
    def laser_attack(self):
        # Target player with a powerful laser
        center_x = self.x + self.width/2
        center_y = self.y + self.height/2
        
        # Set target slightly ahead of player's position (prediction)
        if player_direction != (0, 0):
            dx, dy = player_direction
            self.laser_target_x = player_x + player_width/2 + dx * 100
            self.laser_target_y = player_y + player_height/2 + dy * 100
        else:
            self.laser_target_x = player_x + player_width/2
            self.laser_target_y = player_y + player_height/2
        
        # Clamp target to screen bounds
        self.laser_target_x = max(0, min(screen_width, self.laser_target_x))
        self.laser_target_y = max(0, min(screen_height, self.laser_target_y))
        
        # Start charging laser
        self.laser_charging = True
        self.attack_timer = self.laser_charge_time
        
        # Visual effect for charging
        for _ in range(20):
            particles.append(Particle(
                center_x, center_y,
                (255, 50, 50),
                speed=1,
                size=3,
                lifetime=30
            ))
            
    def drop_money(self):
        if self in enemies_for_money:
            global player_money
            money_dropped = 100 + self.phase * 50  # More money for higher phase bosses
            player_money += money_dropped
            
            # Create money particles - more for boss
            for _ in range(25):
                particles.append(Particle(
                    self.x + random.randint(0, self.width),
                    self.y + random.randint(0, self.height),
                    (255, 255, 0),
                    speed=1.5,
                    size=4,
                    lifetime=40
                ))
                
            enemies_for_money.remove(self)

wave = 0

#=== LOOP ==
clock = pygame.time.Clock()
bullets = []
enemies = []
can_shoot = True
last_shot_time = pygame.time.get_ticks()

is_resting = False
rest_start_time = 0
rest_duration = 5000  # 5000 milliseconds (5 seconds) thời gian nghỉ giữa các wave

# Hàm tạo cục máu ngẫu nhiên
def spawn_health_pickup():
    x = random.randint(0, screen_width - 20)
    y = random.randint(0, screen_height - 20)
    return x, y

health_pickup_x, health_pickup_y = spawn_health_pickup()

# Add scheduled bullets for delayed shots
scheduled_bullets = []

# Initialize shop interaction variables
shop_buttons = []
buy_button_rect = pygame.Rect(0, 0, 0, 0)
leave_button_rect = pygame.Rect(0, 0, 0, 0)

# Main game loop
while True:
    # Get current time for timing operations
    current_time = pygame.time.get_ticks()
    
    # Apply screen shake effect
    if screen_shake > 0:
        shake_offset = (random.randint(int(-screen_shake), int(screen_shake)), 
                      random.randint(int(-screen_shake), int(screen_shake)))
        screen_shake -= 0.5  # Reduce shake intensity
    else:
        shake_offset = (0, 0)
    
    # Draw background first
    screen.blit(background, shake_offset)
    
    # Process scheduled bullets
    for bullet in scheduled_bullets[:]:
        bullet['delay'] -= 16  
        if bullet['delay'] <= 0:
            # Create the bullet
            direction = (math.cos(bullet['angle']), math.sin(bullet['angle']))
            new_bullet = Bullet(bullet['x'], bullet['y'], direction)
            new_bullet.color = bullet['color']
            new_bullet.damage = bullet['damage']
            bullets.append(new_bullet)
            scheduled_bullets.remove(bullet)
    
    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)
        else:
            particle.draw()

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # Handle key press events
        if event.type == pygame.KEYDOWN:
            # Shop key controls
            if is_wave_shop:
                if event.key == pygame.K_1 and len(items_to_sell) >= 1:
                    select_item(0)  
                elif event.key == pygame.K_2 and len(items_to_sell) >= 2:
                    select_item(1)  
                elif event.key == pygame.K_3 and len(items_to_sell) >= 3:
                    select_item(2)  
                elif event.key == pygame.K_4 and len(items_to_sell) >= 4:
                    select_item(3)  
                elif event.key == pygame.K_RETURN:  
                    buy_selected_items()
                    leave_shop()
                elif event.key == pygame.K_ESCAPE: 
                    leave_shop()
            # Skill activation with E key only
            else:
                if event.key == player_skill.key and player_skill.can_use(current_time, energy):
                    if player_skill.use(current_time, energy):
                        energy -= player_skill.energy_cost
                        
                        # Handle bomb skill effect
                        center_x, center_y, radius, damage = player_skill.activate(player_x, player_y)
                        
                        # Damage enemies in radius
                        for enemy in enemies[:]:
                            enemy_center_x = enemy.x + enemy.width / 2
                            enemy_center_y = enemy.y + enemy.height / 2
                            
                            distance = math.sqrt((enemy_center_x - center_x)**2 + 
                                              (enemy_center_y - center_y)**2)
                            
                            if distance <= radius:
                                # Calculate damage falloff based on distance
                                distance_factor = 1 - (distance / radius)
                                actual_damage = damage * distance_factor
                                
                                # Apply damage
                                enemy.take_damage(actual_damage)
                                if enemy.health <= 0:
                                    if enemy.can_drop_money:
                                        enemies_for_money.append(enemy)
                                    score += 10  # Add score for bomb kills
                                    enemies.remove(enemy)
        
        # Handle mouse click events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                if is_wave_shop:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in shop_buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            select_item(button["index"])
                            break
                    
                    # Check if buy button was clicked
                    if buy_button_rect.collidepoint(mouse_pos) and selected_items:
                        buy_selected_items()
                    
                    # Check if leave button was clicked
                    if leave_button_rect.collidepoint(mouse_pos):
                        leave_shop()

    # Check if player is invincible
    if player_invincible and current_time - player_invincible_time >= player_invincible_duration:
        player_invincible = False

    # If in wave shop, draw shop interface and skip rest of game logic
    if is_wave_shop:
        draw_shop_info()
        pygame.display.update()
        clock.tick(60)
        continue

    # Update skills
    player_skill.update(current_time)

    # Xử lý sự kiện phím di chuyển người chơi
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_x > 0:
        player_x -= player_speed
        if keys[pygame.K_w] and player_y > 0:
            player_y -= player_speed
            player_direction = -1, -1  # Đi chéo trái lên
        elif keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed
            player_direction = -1, 1  # Đi chéo trái xuống
        else:
            player_direction = -1, 0  # Đi sang trái
    elif keys[pygame.K_d] and player_x < screen_width - player_width:
        player_x += player_speed
        if keys[pygame.K_w] and player_y > 0:
            player_y -= player_speed
            player_direction = 1, -1  # Đi chéo phải lên
        elif keys[pygame.K_s] and player_y < screen_height - player_height:
            player_y += player_speed
            player_direction = 1, 1  # Đi chéo phải xuống
        else:
            player_direction = 1, 0  # Đi sang phải
    elif keys[pygame.K_w] and player_y > 0:
        player_y -= player_speed
        player_direction = 0, -1  # Đi lên
    elif keys[pygame.K_s] and player_y < screen_height - player_height:
        player_y += player_speed
        player_direction = 0, 1  # Đi xuống
    else:
        player_direction = 0, 0  # Đứng yên

    # Kiểm tra năng lượng để có thể lướt
    if keys[pygame.K_LSHIFT] and not player_is_sliding and energy >= 10:
        player_speed = player_slide_speed  
        player_is_sliding = True
        last_slide_time = pygame.time.get_ticks()
        energy -= 10

    # Kiểm tra thời gian lướt
    if current_time - last_slide_time >= slide_duration and player_is_sliding:
        player_speed = 5 
        player_is_sliding = False
    
    # Hồi phục năng lượng
    if energy < 100:
        if current_time - last_slide_time >= slide_cooldown:
            energy += energy_regen_rate / 60  

    # Kiểm tra thời gian delay giữa các viên đạn
    if current_time - last_shot_time >= bullet_cooldown:
        can_shoot = True

    # Xử lý sự kiện bắn đạn
    if keys[pygame.K_SPACE] and can_shoot:
        bullet_direction = aim_closest_enemy(player_x + player_width // 2, player_y + player_height // 2)
        
        if bullet_direction == (0, 0) and player_direction != (0, 0):
            dx, dy = player_direction
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                bullet_direction = (dx/magnitude, dy/magnitude)
        
        # If still no direction (player standing still and no enemies), shoot upward
        if bullet_direction == (0, 0):
            bullet_direction = (0, -1) 
        
        # Create bullet based on upgrades
        center_x = player_x + player_width // 2
        center_y = player_y + player_height // 2
        
        if triple_shot:
            # Create three bullets in a spread pattern
            main_bullet = Bullet(center_x, center_y, bullet_direction)
            
            # Calculate perpendicular direction for spread
            dx, dy = bullet_direction
            angle = math.atan2(dy, dx)
            
            # Left bullet (20 degrees to the left)
            left_angle = angle - math.radians(20)
            left_dir = (math.cos(left_angle), math.sin(left_angle))
            left_bullet = Bullet(center_x, center_y, left_dir)
            
            # Right bullet (20 degrees to the right)
            right_angle = angle + math.radians(20)
            right_dir = (math.cos(right_angle), math.sin(right_angle))
            right_bullet = Bullet(center_x, center_y, right_dir)
            
            bullets.append(main_bullet)
            bullets.append(left_bullet)
            bullets.append(right_bullet)
            
        elif double_shot:
            # Create two bullets side by side
            dx, dy = bullet_direction
            perpendicular_x = -dy * 0.3  # Perpendicular to direction
            perpendicular_y = dx * 0.3
            
            # Offset each bullet slightly to the side
            bullet1 = Bullet(center_x + perpendicular_x, center_y + perpendicular_y, bullet_direction)
            bullet2 = Bullet(center_x - perpendicular_x, center_y - perpendicular_y, bullet_direction)
            
            bullets.append(bullet1)
            bullets.append(bullet2)
        else:
            # Single bullet
            bullets.append(Bullet(center_x, center_y, bullet_direction))
            
        # Visual and audio feedback for shooting
        for _ in range(3):
            particles.append(Particle(
                center_x, center_y,
                (100, 150, 255),
                speed=2,
                size=3,
                lifetime=10
            ))
            
        can_shoot = False
        last_shot_time = pygame.time.get_ticks()

    # Update and draw bullets
    for bullet in bullets[:]:
        bullet.update()
        
        # Remove bullets that go off screen
        if (bullet.x < 0 or bullet.x > screen_width or 
            bullet.y < 0 or bullet.y > screen_height):
            bullets.remove(bullet)
        else:
            bullet.draw()

    # Check if we need to start a rest period
    if len(enemies) == 0 and not is_resting:
        is_resting = True
        rest_start_time = pygame.time.get_ticks()
        player_health = min(max_player_health, player_health + 20)

    if is_resting and current_time - rest_start_time >= rest_duration:
        is_resting = False
        wave += 1
        
        # Show wave transition
        show_wave_transition(wave)
        
        if wave % 5 == 0 and not boss_spawned:  # Boss wave
            boss = Boss()
            enemies.append(boss)
            boss_spawned = True
            
            # Screen shake effect
            screen_shake = 10
            
        elif wave % 5 == 1:  # Shop wave after boss
            is_wave_shop = True
            generate_shop_items()
            # Clear bullets when entering shop
            bullets.clear()
            
        else:  # Regular wave
            
            num_enemies = wave * 2
            for _ in range(num_enemies):
                adjusted_rates = [
                    max(0.2, 0.6 - wave * 0.02),  
                    min(0.5, 0.3 + wave * 0.01),  
                    min(0.3, 0.1 + wave * 0.01),  
                    0  
                ]
                
                # Normalize rates
                total = sum(adjusted_rates)
                normalized_rates = [r/total for r in adjusted_rates]
                
                enemy_type = random.choices(enemy_types, normalized_rates)[0]
                enemies.append(Enemy(enemy_type))
        
        # Generate health pickup for next rest period
        health_pickup_x, health_pickup_y = spawn_health_pickup()

    # Draw health pickup during rest periods
    if is_resting:
        # Draw health pickup as a glowing heart
        heart_size = 20
        heart_x = health_pickup_x
        heart_y = health_pickup_y
        
        # Pulsating effect
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.2 + 1.0
        
        # Glow
        glow = pygame.Surface((heart_size*3*pulse, heart_size*3*pulse), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (0, 255, 0, 50), 
                          (0, 0, heart_size*3*pulse, heart_size*3*pulse))
        screen.blit(glow, (heart_x + heart_size/2 - heart_size*3*pulse/2, 
                         heart_y + heart_size/2 - heart_size*3*pulse/2))
        
        # Heart shape
        pygame.draw.circle(screen, GREEN, (heart_x + heart_size/4, heart_y + heart_size/4), heart_size/4)
        pygame.draw.circle(screen, GREEN, (heart_x + heart_size*3/4, heart_y + heart_size/4), heart_size/4)
        pygame.draw.polygon(screen, GREEN, [
            (heart_x, heart_y + heart_size/4),
            (heart_x + heart_size, heart_y + heart_size/4),
            (heart_x + heart_size/2, heart_y + heart_size)
        ])

        # Particle effect
        if random.random() < 0.1:
            particles.append(Particle(
                heart_x + random.randint(0, heart_size),
                heart_y + random.randint(0, heart_size),
                GREEN,
                speed=0.5,
                size=2,
                lifetime=20
            ))

    # Kiểm tra va chạm giữa người chơi và cục máu
    if is_resting and player_x <= health_pickup_x + 20 and player_x + player_width >= health_pickup_x and \
            player_y <= health_pickup_y + 20 and player_y + player_height >= health_pickup_y:
        # Nếu người chơi va chạm với cục máu thì hồi phục 20 máu
        player_health = min(max_player_health, player_health + 20)
        
        # Create healing particles
        for _ in range(15):
            particles.append(Particle(
                health_pickup_x + random.randint(0, 20),
                health_pickup_y + random.randint(0, 20),
                GREEN,
                speed=1,
                size=3,
                lifetime=30
            ))
            
        # Tạo cục máu mới sau khi người chơi hồi phục
        health_pickup_x, health_pickup_y = spawn_health_pickup()

    # Kiểm tra xem còn kẻ địch nào là boss không, nếu không thì đánh dấu boss_spawned thành False để sẵn sàng spawn boss tiếp theo
    if not any(isinstance(enemy, Boss) for enemy in enemies):
        boss_spawned = False

    # Cập nhật vị trí địch và vẽ địch lên màn hình
    for enemy in enemies:
        enemy.update()
        enemy.draw()
        enemy.draw_health_bar()  # Vẽ thanh máu của kẻ địch

    # Kiểm tra va chạm giữa đạn và địch
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if (enemy.x <= bullet.x <= enemy.x + enemy.width and
                enemy.y <= bullet.y <= enemy.y + enemy.height):
                # Apply damage to enemy
                enemy.take_damage(bullet.damage)
                
                # Create hit effect
                for _ in range(5):
                    particles.append(Particle(
                        bullet.x, bullet.y,
                        WHITE,
                        speed=1,
                        size=2,
                        lifetime=10
                    ))
                
                # Remove bullet
                bullets.remove(bullet)
                
                # Check if enemy is defeated
                if enemy.health <= 0:
                    # Determine score based on enemy type
                    score_multiplier = 1
                    if enemy.enemy_type == 'small':
                        score_multiplier = 1
                    elif enemy.enemy_type == 'medium':
                        score_multiplier = 2
                    elif enemy.enemy_type == 'large':
                        score_multiplier = 3
                    elif enemy.enemy_type == 'boss':
                        score_multiplier = 5
                        screen_shake = 15  
                        boss_kills += 1
                    
                    # Add to score - score is global
                    score += 10 * score_multiplier
                    
                    # Handle money drops
                    if enemy.can_drop_money:
                        enemies_for_money.append(enemy)
                    
                    # Create death explosion
                    for _ in range(20):
                        particles.append(Particle(
                            enemy.x + random.randint(0, enemy.width),
                            enemy.y + random.randint(0, enemy.height),
                            enemy_colors[enemy.enemy_type],
                            speed=2,
                            size=4,
                            lifetime=30
                        ))
                    
                    # Remove enemy
                    enemies.remove(enemy)
                    break  # Break out of bullet loop once enemy is removed

    # Kiểm tra va chạm giữa người chơi và kẻ địch
    if not player_invincible:  
        for enemy in enemies[:]:
            if (player_x <= enemy.x + enemy.width and player_x + player_width >= enemy.x and
                player_y <= enemy.y + enemy.height and player_y + player_height >= enemy.y):
                # Calculate damage
                damage = enemy.health // 4  
                player_health -= damage
                
                # Create hit effect
                screen_shake = min(15, damage // 2) 
                
                # Temporary invincibility
                player_invincible = True
                player_invincible_time = pygame.time.get_ticks()
                
                # Create particles for hit effect
                for _ in range(15):
                    particles.append(Particle(
                        player_x + random.randint(0, player_width),
                        player_y + random.randint(0, player_height),
                        RED,
                        speed=2,
                        size=3,
                        lifetime=20
                    ))
                
                # Remove enemy
                enemies.remove(enemy)
                
                # Check if player died
                if player_health <= 0:
                    game_over(score)
                break  # Break after first collision

    # Xử lý việc rơi tiền khi kẻ địch bị tiêu diệt
    for enemy in enemies_for_money[:]:
        enemy.drop_money()
    
    # Draw player and UI
    draw_player(player_x, player_y)
    draw_energy_bar()
    draw_health_bar()

    # Draw single skill UI
    skill_bar_x = 10
    skill_bar_y = screen_height - 60
    
    # Draw skill with level indicator
    player_skill.draw_icon(skill_bar_x, skill_bar_y)

    # Hiển thị số vòng và điểm lên màn hình
    font = pygame.font.SysFont(None, 30)
    
    # Draw with shadow effect for better visibility
    shadow_offset = 1
    
    # Wave display
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    wave_shadow = font.render(f"Wave: {wave}", True, (50, 50, 50))
    screen.blit(wave_shadow, (10 + shadow_offset, screen_height - 120 + shadow_offset))
    screen.blit(wave_text, (10, screen_height - 120))
    
    # Score display
    score_text = font.render(f"Score: {score}", True, WHITE)
    score_shadow = font.render(f"Score: {score}", True, (50, 50, 50))
    screen.blit(score_shadow, (10 + shadow_offset, screen_height - 150 + shadow_offset))
    screen.blit(score_text, (10, screen_height - 150))
    
    # Money display
    money_text = font.render(f"Money: {player_money}", True, YELLOW)
    money_shadow = font.render(f"Money: {player_money}", True, (50, 50, 0))
    screen.blit(money_shadow, (10 + shadow_offset, screen_height - 180 + shadow_offset))
    screen.blit(money_text, (10, screen_height - 180))
    
    # Display wave rest timer if in rest period
    if is_resting:
        rest_remaining = rest_duration - (pygame.time.get_ticks() - rest_start_time)
        rest_seconds = math.ceil(rest_remaining / 1000)
        
        rest_text = font.render(f"Next wave in: {rest_seconds}s", True, (200, 200, 255))
        screen.blit(rest_text, (screen_width - rest_text.get_width() - 10, 10))

    # Display active power-ups
    power_up_y = 50
    if double_shot:
        double_text = font.render("Double Shot", True, (100, 200, 255))
        screen.blit(double_text, (screen_width - double_text.get_width() - 10, power_up_y))
        power_up_y += 25
        
    if triple_shot:
        triple_text = font.render("Triple Shot", True, (100, 200, 255))
        screen.blit(triple_text, (screen_width - triple_text.get_width() - 10, power_up_y))
        power_up_y += 25
        
    if player_invincible:
        inv_text = font.render("Shield Active", True, (255, 255, 200))
        screen.blit(inv_text, (screen_width - inv_text.get_width() - 10, power_up_y))

    skibidi = pygame.font.SysFont(None, 24)
    toilet = skibidi.render("@Qu4nh", True, (255, 255, 255))
    toilet.set_alpha(100)  
    screen.blit(toilet, (screen_width - toilet.get_width() - 10, screen_height - toilet.get_height() - 10))

    pygame.display.update()
    clock.tick(60)
