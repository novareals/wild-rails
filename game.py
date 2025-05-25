import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
FPS = 60
PLAYER_SPEED = 1.5
PROJECTILE_SPEED = 8
PROJECTILE_DAMAGE = 10
ZOMBIE_SPEED = 0.8

# Colors
COLORS = {
    'sand': (238, 203, 173),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'red': (255, 0, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gold': (255, 215, 0)
}

# Currency system
BONDS_PER_ZOMBIE = 10  # Bonds earned per zombie kill

class Game:
    def __init__(self):
        # Setup display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Wild Rails - Zombie Survival")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = "menu"  # "menu", "playing", "game_over"
        
        # Player
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.player_size = 64
        self.player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 
                                     self.player_size, self.player_size)
        
        # Game objects
        self.projectiles = []  # [x, y, vel_x, vel_y, active]
        self.zombies = []      # [x, y, hp, max_hp, rect]
        
        # Wave management and currency
        self.wave = 1
        self.bonds = 0  # Initialize currency
        self.zombies_per_wave = 5
        self.zombies_spawned = 0
        self.spawn_timer = 0
        self.spawn_delay = 120  # 2 seconds at 60 FPS
        
        # Attack cooldown
        self.attack_cooldown = 0
        self.max_cooldown = 60  # 1 second at 60 FPS
        
        # Load assets
        try:
            self.player_img = pygame.transform.scale(
                pygame.image.load("Wild Rails/Torcher.png"),
                (self.player_size, self.player_size)
            )
            self.zombie_img = pygame.transform.scale(
                pygame.image.load("Wild Rails/Zombie.png"),
                (48, 48)
            )
        except (pygame.error, FileNotFoundError):
            # Fallback to basic colored shapes
            self.player_img = pygame.Surface((self.player_size, self.player_size))
            self.player_img.fill((255, 100, 100))
            self.zombie_img = pygame.Surface((48, 48))
            self.zombie_img.fill((0, 150, 0))
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
    
    def reset_game(self):
        """Reset game state for a new game"""
        self.wave = 1
        self.bonds = 0
        self.zombies_per_wave = 5
        self.zombies_spawned = 0
        self.spawn_timer = 0
        self.projectiles = []
        self.zombies = []
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.player_rect.x, self.player_rect.y = self.player_pos
        self.attack_cooldown = 0
        self.state = "playing"
    
    def spawn_zombie(self):
        """Create a zombie at a random edge of the screen"""
        if self.zombies_spawned >= self.zombies_per_wave:
            return
        
        # Randomly select an edge to spawn from
        side = random.randint(0, 3)
        if side == 0:  # Top
            x, y = random.randint(0, SCREEN_WIDTH), -50
        elif side == 1:  # Right
            x, y = SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Bottom
            x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50
        else:  # Left
            x, y = -50, random.randint(0, SCREEN_HEIGHT)
        
        # Create zombie with stats scaled to current wave
        # Exponential health scaling that makes zombies much tougher in later waves
        # Base health is 35 for wave 1 (same as original), then grows exponentially
        if self.wave == 1:
            max_hp = 35  # Keep original health for wave 1
        else:
            max_hp = int(35 * (1.25 ** (self.wave - 1)))  # 25% increase per wave
        zombie_rect = pygame.Rect(x, y, 48, 48)
        self.zombies.append([x, y, max_hp, max_hp, zombie_rect])
        self.zombies_spawned += 1
        self.spawn_timer = 0
    
    def shoot(self):
        """Create a projectile aimed at the mouse cursor"""
        if self.attack_cooldown <= 0:
            # Get player center and mouse position
            player_center = (self.player_pos[0] + self.player_size // 2, 
                           self.player_pos[1] + self.player_size // 2)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Calculate direction vector
            dx = mouse_x - player_center[0]
            dy = mouse_y - player_center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                vel_x = (dx / distance) * PROJECTILE_SPEED
                vel_y = (dy / distance) * PROJECTILE_SPEED
                
                # Store projectile as [x, y, vel_x, vel_y, active]
                self.projectiles.append([
                    player_center[0], player_center[1], 
                    vel_x, vel_y, True
                ])
                self.attack_cooldown = self.max_cooldown
    
    def update(self):
        """Update game state for one frame"""
        if self.state != "playing":
            return
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update player position based on keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_pos[1] -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_pos[1] += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_pos[0] -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_pos[0] += PLAYER_SPEED
        
        # Keep player on screen
        self.player_pos[0] = max(0, min(self.player_pos[0], SCREEN_WIDTH - self.player_size))
        self.player_pos[1] = max(0, min(self.player_pos[1], SCREEN_HEIGHT - self.player_size))
        self.player_rect.x, self.player_rect.y = self.player_pos
        
        # Update projectiles
        for proj in self.projectiles[:]:
            # Move projectile
            proj[0] += proj[2]  # x += vel_x
            proj[1] += proj[3]  # y += vel_y
            
            # Deactivate if off screen
            if (proj[0] < 0 or proj[0] > SCREEN_WIDTH or 
                proj[1] < 0 or proj[1] > SCREEN_HEIGHT):
                proj[4] = False
                self.projectiles.remove(proj)
        
        # Update zombies and check collisions
        for zombie in self.zombies[:]:
            # Move zombie towards player
            player_center = (self.player_pos[0] + self.player_size // 2, 
                           self.player_pos[1] + self.player_size // 2)
            dx = player_center[0] - zombie[0]
            dy = player_center[1] - zombie[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                zombie[0] += (dx / distance) * ZOMBIE_SPEED
                zombie[1] += (dy / distance) * ZOMBIE_SPEED
                zombie[4].x = int(zombie[0])
                zombie[4].y = int(zombie[1])
            
            # Check projectile hits
            for proj in self.projectiles[:]:
                if proj[4] and zombie[4].collidepoint(proj[0], proj[1]):
                    zombie[2] -= PROJECTILE_DAMAGE
                    proj[4] = False
                    self.projectiles.remove(proj)
                    break
            
            # Remove dead zombies and award bonds
            if zombie[2] <= 0:
                self.bonds += BONDS_PER_ZOMBIE  # Add bonds when zombie is killed
                self.zombies.remove(zombie)
                continue
            
            # Check player collision (game over if zombie touches player)
            if zombie[4].colliderect(self.player_rect):
                self.state = "game_over"
                return
        
        # Spawn new zombies
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay and self.zombies_spawned < self.zombies_per_wave:
            self.spawn_zombie()
        
        # Check wave completion - now endless
        if len(self.zombies) == 0 and self.zombies_spawned >= self.zombies_per_wave:
            self.wave += 1
            # Multiplicative scaling for zombie spawn count
            if self.wave == 2:
                self.zombies_per_wave += 2  # Keep original increment for wave 2
            else:
                # Multiply by 1.3 for exponential growth in later waves
                self.zombies_per_wave = int(self.zombies_per_wave * 1.3)
            self.zombies_spawned = 0
            self.spawn_timer = 0
    
    def draw_menu(self):
        """Draw the main menu screen"""
        # Title
        title = self.big_font.render("ZOMBIE SURVIVAL", True, COLORS['black'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        # Menu options
        texts = [
            ("Press SPACE to Play", self.font, 50),
            ("Press ESC to Quit", self.font, 100),
            ("Survive endless waves of zombies!", self.font, 200),
            ("Earn Bonds for each zombie killed", self.font, 250)
        ]
        
        for text, font, y_offset in texts:
            surf = font.render(text, True, COLORS['black'])
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
            self.screen.blit(surf, rect)
    
    def draw_game(self):
        """Draw the main gameplay screen"""
        # Draw game objects
        self.screen.blit(self.player_img, self.player_pos)
        
        # Draw active projectiles
        for proj in self.projectiles:
            if proj[4]:  # if active
                pygame.draw.circle(self.screen, COLORS['yellow'], 
                                 (int(proj[0]), int(proj[1])), 6)
        
        # Draw zombies with health bars
        for zombie in self.zombies:
            self.screen.blit(self.zombie_img, (int(zombie[0]), int(zombie[1])))
            
            # Health bar
            bar_width = 48
            pygame.draw.rect(self.screen, COLORS['red'],
                           (zombie[0], zombie[1] - 10, bar_width, 6))
            health_width = int((zombie[2] / zombie[3]) * bar_width)
            pygame.draw.rect(self.screen, COLORS['green'],
                           (zombie[0], zombie[1] - 10, health_width, 6))
        
        # Draw UI
        texts = [
            (f"Wave: {self.wave}", COLORS['black']),
            (f"Bonds: {self.bonds}", COLORS['gold']),
            (f"Zombies: {len(self.zombies)}", COLORS['black']),
            (f"{'READY TO FIRE' if self.attack_cooldown <= 0 else f'Cooldown: {self.attack_cooldown/60:.1f}s'}", 
             COLORS['green'] if self.attack_cooldown <= 0 else COLORS['red'])
        ]
        
        for i, (text, color) in enumerate(texts):
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (10, 10 + i * 40))
        
        # Draw crosshair at mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.line(self.screen, COLORS['red'],
                       (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
        pygame.draw.line(self.screen, COLORS['red'],
                       (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)
    
    def draw_game_over(self):
        """Draw the game over screen with statistics"""
        texts = [
            ("GAME OVER", self.big_font, COLORS['red'], -100),
            (f"Wave Reached: {self.wave}", self.font, COLORS['black'], 0),
            (f"Bonds Earned: {self.bonds}", self.font, COLORS['gold'], 50),
            ("Press SPACE to return to Menu", self.font, COLORS['black'], 150),
            ("Press ESC to Quit", self.font, COLORS['black'], 200)
        ]
        
        for text, font, color, y_offset in texts:
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
            self.screen.blit(surf, rect)
    
    def draw(self):
        """Render the current game state"""
        self.screen.fill(COLORS['sand'])
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "menu"
                        else:
                            self.running = False
                    elif event.key == pygame.K_SPACE:
                        if self.state == "menu":
                            self.reset_game()
                        elif self.state == "game_over":
                            self.state = "menu"
                        elif self.state == "playing":
                            self.shoot()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("Wild Rails - Zombie Survival")
    print("=" * 30)
    print("Controls:")
    print("- WASD: Move Torcher")
    print("- SPACE: Shoot projectile at mouse cursor")
    print("- ESC: Return to menu/Quit")
    print("\nObjective: Survive endless waves and collect Bonds!")
    print("Starting game...")
    
    Game().run()
