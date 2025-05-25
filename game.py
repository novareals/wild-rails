import pygame
import sys
import os
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
PLAYER_SPEED = 1.5
PROJECTILE_SPEED = 8
PROJECTILE_DAMAGE = 10
ZOMBIE_SPEED = 0.8

# Colors
DESERT_SAND = (238, 203, 173)
DARKER_SAND = (205, 175, 149)
CACTUS_GREEN = (34, 139, 34)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x
        self.y = start_y
        self.radius = 6
        
        # Calculate direction to target
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.vel_x = (dx / distance) * PROJECTILE_SPEED
            self.vel_y = (dy / distance) * PROJECTILE_SPEED
        else:
            self.vel_x = 0
            self.vel_y = 0
        
        self.active = True
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Remove if off screen
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False
    
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 150), (int(self.x), int(self.y)), self.radius - 2)

class Zombie:
    def __init__(self, x, y, wave):
        self.x = x
        self.y = y
        self.max_hp = 20 + (wave * 15)  # HP increases with each wave
        self.hp = self.max_hp
        self.speed = ZOMBIE_SPEED
        self.width = 48
        self.height = 48
        
        # Try to load zombie image
        try:
            self.image = pygame.image.load("Wild Rails/Zombie.png")
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Green placeholder if image not found
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((0, 150, 0))
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True
    
    def update(self, player_x, player_y):
        if not self.alive:
            return
        
        # Move towards player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, (int(self.x), int(self.y)))
            
            # Draw health bar
            bar_width = self.width
            bar_height = 6
            bar_x = int(self.x)
            bar_y = int(self.y) - 10
            
            # Background (red)
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            # Health (green)
            health_width = int((self.hp / self.max_hp) * bar_width)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.width = 64
        self.height = 64
        
        # Try to load the Torcher image, fallback to placeholder
        try:
            self.image = pygame.image.load("Wild Rails/Torcher.png")
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create a placeholder if image not found
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 100, 100))  # Red rectangle as placeholder
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def handle_input(self, keys):
        # WASD movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
        
        # Keep player on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def get_center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))

class WaveManager:
    def __init__(self):
        self.current_wave = 1
        self.zombies_per_wave = 5
        self.wave_active = False
        self.zombies_spawned = 0
        self.spawn_timer = 0
        self.spawn_delay = 120  # 2 seconds at 60 FPS
        
    def start_wave(self):
        self.wave_active = True
        self.zombies_spawned = 0
        self.spawn_timer = 0
        
    def spawn_zombie(self, zombies_list):
        if self.zombies_spawned < self.zombies_per_wave:
            # Spawn from random edge
            side = random.randint(0, 3)
            if side == 0:  # Top
                x = random.randint(0, SCREEN_WIDTH)
                y = -50
            elif side == 1:  # Right
                x = SCREEN_WIDTH + 50
                y = random.randint(0, SCREEN_HEIGHT)
            elif side == 2:  # Bottom
                x = random.randint(0, SCREEN_WIDTH)
                y = SCREEN_HEIGHT + 50
            else:  # Left
                x = -50
                y = random.randint(0, SCREEN_HEIGHT)
            
            zombie = Zombie(x, y, self.current_wave)
            zombies_list.append(zombie)
            self.zombies_spawned += 1
            self.spawn_timer = 0
    
    def update(self, zombies_list):
        if self.wave_active:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay and self.zombies_spawned < self.zombies_per_wave:
                self.spawn_zombie(zombies_list)
            
            # Check if wave is complete
            alive_zombies = [z for z in zombies_list if z.alive]
            if self.zombies_spawned >= self.zombies_per_wave and len(alive_zombies) == 0:
                self.wave_active = False
                if self.current_wave < 10:
                    self.current_wave += 1
                    self.zombies_per_wave += 2  # More zombies each wave
                return True  # Wave completed
        
        return False  # Wave not completed

class DesertEnvironment:
    def __init__(self):
        self.cacti = []
        self.rocks = []
        self.generate_environment()
    
    def generate_environment(self):
        # Generate some cacti
        for _ in range(15):
            x = random.randint(0, SCREEN_WIDTH - 20)
            y = random.randint(0, SCREEN_HEIGHT - 40)
            self.cacti.append({'x': x, 'y': y, 'height': random.randint(20, 40)})
        
        # Generate some rocks
        for _ in range(25):
            x = random.randint(0, SCREEN_WIDTH - 15)
            y = random.randint(0, SCREEN_HEIGHT - 15)
            size = random.randint(8, 20)
            self.rocks.append({'x': x, 'y': y, 'size': size})
    
    def draw(self, screen):
        # Draw desert floor texture
        for x in range(0, SCREEN_WIDTH, 50):
            for y in range(0, SCREEN_HEIGHT, 50):
                # Add some variation to the sand
                if (x + y) % 100 == 0:
                    pygame.draw.circle(screen, DARKER_SAND, (x + 25, y + 25), 20)
        
        # Draw rocks
        for rock in self.rocks:
            pygame.draw.circle(screen, (139, 69, 19), (rock['x'], rock['y']), rock['size'])
            pygame.draw.circle(screen, (160, 82, 45), (rock['x'], rock['y']), rock['size'] - 2)
        
        # Draw cacti
        for cactus in self.cacti:
            # Cactus body
            pygame.draw.rect(screen, CACTUS_GREEN, 
                           (cactus['x'], cactus['y'], 15, cactus['height']))
            # Cactus arms
            pygame.draw.rect(screen, CACTUS_GREEN, 
                           (cactus['x'] - 8, cactus['y'] + cactus['height']//3, 8, 15))
            pygame.draw.rect(screen, CACTUS_GREEN, 
                           (cactus['x'] + 15, cactus['y'] + cactus['height']//2, 8, 12))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Wild Rails - Zombie Survival")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game objects
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.environment = DesertEnvironment()
        self.wave_manager = WaveManager()
        self.projectiles = []
        self.zombies = []
        
        # Game state
        self.game_state = "waiting"  # "waiting", "playing", "game_over", "victory"
        
        # Attack cooldown system
        self.attack_cooldown = 0
        self.max_attack_cooldown = 60  # 1 second at 60 FPS
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "waiting":
                        self.game_state = "playing"
                        self.wave_manager.start_wave()
                    elif self.game_state == "playing" and self.attack_cooldown <= 0:
                        self.shoot_projectile()
                        self.attack_cooldown = self.max_attack_cooldown  # Start cooldown
    
    def shoot_projectile(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center = self.player.get_center()
        projectile = Projectile(player_center[0], player_center[1], mouse_x, mouse_y)
        self.projectiles.append(projectile)
    
    def update(self):
        if self.game_state == "playing":
            # Update attack cooldown
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
                
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            
            # Update projectiles
            for projectile in self.projectiles[:]:
                projectile.update()
                if not projectile.active:
                    self.projectiles.remove(projectile)
            
            # Update zombies
            player_center = self.player.get_center()
            for zombie in self.zombies:
                zombie.update(player_center[0], player_center[1])
            
            # Check projectile-zombie collisions
            for projectile in self.projectiles[:]:
                for zombie in self.zombies[:]:
                    if (zombie.alive and projectile.active and
                        zombie.rect.collidepoint(int(projectile.x), int(projectile.y))):
                        zombie.take_damage(PROJECTILE_DAMAGE)
                        projectile.active = False
                        self.projectiles.remove(projectile)
                        break
            
            # Remove dead zombies
            self.zombies = [z for z in self.zombies if z.alive]
            
            # Check player-zombie collisions
            for zombie in self.zombies:
                if zombie.alive and self.player.rect.colliderect(zombie.rect):
                    self.game_state = "game_over"
            
            # Update wave manager
            wave_completed = self.wave_manager.update(self.zombies)
            if wave_completed and self.wave_manager.current_wave > 10:
                self.game_state = "victory"
            elif wave_completed:
                # Brief pause between waves, then start next wave
                pygame.time.wait(1000)
                self.wave_manager.start_wave()
    
    def draw(self):
        # Clear screen with desert background
        self.screen.fill(DESERT_SAND)
        
        # Draw environment
        self.environment.draw(self.screen)
        
        if self.game_state == "playing":
            # Draw game objects
            self.player.draw(self.screen)
            
            for zombie in self.zombies:
                zombie.draw(self.screen)
            
            for projectile in self.projectiles:
                projectile.draw(self.screen)
            
            # Draw UI
            wave_text = self.font.render(f"Wave: {self.wave_manager.current_wave}/10", True, BLACK)
            self.screen.blit(wave_text, (10, 10))
            
            zombies_left = len([z for z in self.zombies if z.alive])
            zombies_text = self.font.render(f"Zombies: {zombies_left}", True, BLACK)
            self.screen.blit(zombies_text, (10, 50))
            
            # Draw attack cooldown indicator
            if self.attack_cooldown > 0:
                cooldown_text = self.font.render(f"Cooldown: {self.attack_cooldown/60:.1f}s", True, RED)
                self.screen.blit(cooldown_text, (10, 90))
            else:
                ready_text = self.font.render("READY TO FIRE", True, (0, 255, 0))
                self.screen.blit(ready_text, (10, 90))
            
            # Draw crosshair at mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, RED, (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
            pygame.draw.line(self.screen, RED, (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)
            
        elif self.game_state == "waiting":
            title_text = self.big_font.render("ZOMBIE SURVIVAL", True, BLACK)
            start_text = self.font.render("Press SPACE to start Wave 1", True, BLACK)
            controls_text = [
                "WASD - Move Torcher",
                "SPACE - Shoot yellow projectile at cursor",
                "Survive 10 waves to win!"
            ]
            
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            
            self.screen.blit(title_text, title_rect)
            self.screen.blit(start_text, start_rect)
            
            for i, control in enumerate(controls_text):
                text = self.font.render(control, True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20 + i*30))
                self.screen.blit(text, text_rect)
        
        elif self.game_state == "game_over":
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press ESC to quit", True, BLACK)
            
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
        
        elif self.game_state == "victory":
            victory_text = self.big_font.render("VICTORY!", True, (0, 255, 0))
            congrats_text = self.font.render("You survived all 10 waves!", True, BLACK)
            
            victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            
            self.screen.blit(victory_text, victory_rect)
            self.screen.blit(congrats_text, congrats_rect)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    print("Wild Rails - Zombie Survival")
    print("=" * 30)
    print("Images needed:")
    print("- Wild Rails/Torcher.png (player)")
    print("- Wild Rails/Zombie.png (enemies)")
    print("\nControls:")
    print("- WASD: Move Torcher")
    print("- SPACE: Shoot projectile at mouse cursor")
    print("- ESC: Quit game")
    print("\nObjective: Survive 10 waves of zombies!")
    print("Starting game...")
    
    game = Game()
    game.run()