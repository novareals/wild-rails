import pygame
import sys
import math
import random
import os
import json

# Initialize Pygame and audio
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
FPS = 60
PLAYER_SPEED = 1.5
PROJECTILE_SPEED = 8
PROJECTILE_DAMAGE = 10
ZOMBIE_SPEED = 0.8
MAX_INVENTORY = 4  # Maximum number of characters in inventory

# Rarity system
RARITIES = {
    "Common": {"color": (200, 200, 200), "chance": 0.40},
    "Rare": {"color": (30, 144, 255), "chance": 0.30},
    "Epic": {"color": (138, 43, 226), "chance": 0.15},
    "Legendary": {"color": (255, 165, 0), "chance": 0.10},
    "Mythic": {"color": (255, 0, 255), "chance": 0.04},
    "Godly": {"color": (255, 215, 0), "chance": 0.01}
}

# Character definitions
CHARACTERS = {
    "Torcher": {
        "name": "Torcher",
        "image": "Torcher.png",
        "damage": PROJECTILE_DAMAGE,
        "projectiles": 1,
        "price": 0,  # Free/default character
        "rarity": "Common",
        "description": "Default character with basic attack"
    },
    "Cowboy": {
        "name": "Cowboy",
        "image": "boy cow.png",
        "damage": PROJECTILE_DAMAGE * 2,
        "projectiles": 1,
        "price": 25,
        "rarity": "Rare",
        "description": "Higher damage than Torcher"
    },
    "Shotgunner": {
        "name": "Shotgunner",
        "image": "Shotgunner.png",
        "damage": PROJECTILE_DAMAGE * 3,
        "projectiles": 1,
        "price": 50,
        "rarity": "Epic",
        "description": "Higher damage than Cowboy"
    },
    "Mummy": {
        "name": "Mummy",
        "image": "Mummy.png",
        "damage": PROJECTILE_DAMAGE * 3,
        "projectiles": 1,
        "price": 50,
        "rarity": "Epic",
        "description": "Same power as Shotgunner"
    },
    "Horse": {
        "name": "Horse",
        "image": "Horse.png",
        "damage": PROJECTILE_DAMAGE * 5,
        "projectiles": 1,
        "price": 100,
        "rarity": "Legendary",
        "description": "Single high-damage bullet"
    },
    "Vampire": {
        "name": "Vampire",
        "image": "Vampire.png",
        "damage": PROJECTILE_DAMAGE * 4,
        "projectiles": 1,
        "price": 100,
        "rarity": "Legendary",
        "description": "Fast melee with red sword slash",
        "is_melee": True,
        "melee_range": 100,
        "melee_color": (255, 0, 0)
    },
    "Werewolf": {
        "name": "Werewolf",
        "image": "Werewolf.png",
        "damage": PROJECTILE_DAMAGE * 7,
        "projectiles": 1,
        "price": 200,
        "rarity": "Mythic",
        "description": "Large AOE damage",
        "is_aoe": True,
        "aoe_radius": 150
    },
    "Tesla": {
        "name": "Nikola Tesla",
        "image": "Nicola Tesla.png",
        "damage": PROJECTILE_DAMAGE * 10,
        "projectiles": 1,
        "price": 500,
        "rarity": "Godly",
        "description": "Largest AOE, highest damage",
        "is_aoe": True,
        "aoe_radius": 200
    }
}

# Enemy types based on character rarities
ENEMY_TYPES = {
    "Zombie": {
        "name": "Zombie",
        "image": "Zombie.png",
        "base_hp": 35,
        "rarity": "Common",
        "speed_multiplier": 1.0
    },
    "HorseZombie": {
        "name": "Horse Zombie",
        "image": "Zombie.png",  # Reusing image until new ones are added
        "base_hp": 70,
        "rarity": "Legendary",
        "speed_multiplier": 1.2
    },
    "MummyZombie": {
        "name": "Mummy Zombie",
        "image": "Zombie.png",  # Reusing image until new ones are added
        "base_hp": 50,
        "rarity": "Epic",
        "speed_multiplier": 0.8
    },
    "VampireZombie": {
        "name": "Vampire Zombie",
        "image": "Zombie.png",  # Reusing image until new ones are added
        "base_hp": 65,
        "rarity": "Legendary",
        "speed_multiplier": 1.5
    },
    "WerewolfZombie": {
        "name": "Werewolf Zombie",
        "image": "Zombie.png",  # Reusing image until new ones are added
        "base_hp": 90,
        "rarity": "Mythic",
        "speed_multiplier": 1.3
    },
    "TeslaZombie": {
        "name": "Tesla Zombie",
        "image": "Zombie.png",  # Reusing image until new ones are added
        "base_hp": 120,
        "rarity": "Godly",
        "speed_multiplier": 1.1
    }
}

# Colors
COLORS = {
    'sand': (238, 203, 173),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'red': (255, 0, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gold': (255, 215, 0),
    'purple': (138, 43, 226),
    'orange': (255, 165, 0),
    'pink': (255, 0, 255),
    'blue': (30, 144, 255)
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
        self.save_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 200, 200, 40)
        self.load_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 250, 200, 40)
        
        # Load sounds
        self.background_music = pygame.mixer.Sound(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                  "Wild Rails", "o-bom-o-mal-e-o-feio-velho-oeste-desafio-dont-talk-duelo-desafio-armas.mp3"))
        self.shoot_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                             "Wild Rails", "westernsilah-online-audio-converter.mp3"))
        
        # Set background music to loop forever
        self.background_music.play(-1)  # -1 means loop indefinitely
        
        # Game state
        self.state = "menu"  # "menu", "playing", "game_over", "shop"
        
        # Player
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.player_size = 64
        self.player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 
                                     self.player_size, self.player_size)
        
        # Character selection and ownership
        self.owned_characters = ["Torcher"]  # Start with only Torcher
        self.selected_character = "Torcher"  # Default character
        
        # Shop system
        self.restock_timer = 0
        self.restock_interval = 5 * 60 * FPS  # 5 minutes in frames (at 60 FPS)
        self.available_characters = []
        self.shop_clickable_areas = {}  # Track clickable areas for characters
        self.shop_hover = None  # Track which character is being hovered
        
        # Load saved game data if available
        self.load_game()
        
        # Initialize shop
        self.restock_shop()  # Initial shop stock
        
        # Game objects
        self.projectiles = []  # [x, y, vel_x, vel_y, active]
        self.zombies = []      # [x, y, hp, max_hp, rect]
        
        # Wave management and currency
        self.wave = 1
        self.match_bonds = 0  # Bonds earned in current match
        self.permanent_bonds = 0  # Total bonds across all matches
        self.zombies_per_wave = 5
        self.zombies_spawned = 0
        self.spawn_timer = 0
        self.spawn_delay = 120  # 2 seconds at 60 FPS
        
        # Attack cooldown
        self.attack_cooldown = 0
        self.max_cooldown = 60  # 1 second at 60 FPS
        
        # Load assets
        # Create base folder path for images
        # Make sure to normalize path for Windows
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Script directory: {script_dir}")
        
        # Try both relative and absolute paths for better compatibility
        self.image_folder = os.path.normpath(os.path.join(script_dir, "Wild Rails"))
        print(f"Primary image folder path: {self.image_folder}")
        print(f"Images directory exists: {os.path.exists(self.image_folder)}")
        
        # Alternative path (just in case)
        alt_image_folder = os.path.normpath("C:\\Users\\kevin\\code\\wild-rails\\Wild Rails")
        print(f"Alternative image folder path: {alt_image_folder}")
        print(f"Alternative path exists: {os.path.exists(alt_image_folder)}")
        
        # Use the alternative path if the primary one doesn't exist
        if not os.path.exists(self.image_folder) and os.path.exists(alt_image_folder):
            print("Using alternative image folder path")
            self.image_folder = alt_image_folder
        
        # List files in the directory for debugging
        try:
            files_in_dir = os.listdir(self.image_folder)
            print(f"Files in directory: {files_in_dir}")
            
            # Check if expected image files exist
            expected_files = ["boy cow.png", "Torcher.png", "Zombie.png"]
            for file in expected_files:
                file_path = os.path.join(self.image_folder, file)
                if os.path.exists(file_path):
                    print(f"Found expected file: {file}")
                    print(f"File size: {os.path.getsize(file_path)} bytes")
                else:
                    print(f"WARNING: Expected file not found: {file}")
        except Exception as e:
            print(f"Error listing directory: {e}")
        
        # Load character images
        self.character_imgs = {}
        for character_id, character_data in CHARACTERS.items():
            image_path = character_data["image"]
            try:
                # Get the file name from the path
                filename = os.path.basename(image_path)
                # Create absolute path to the image
                abs_path = os.path.normpath(os.path.join(self.image_folder, filename))
                print(f"\nLoading {character_id} image from: {abs_path}")
                
                # Check if file exists before trying to load it
                if not os.path.exists(abs_path):
                    print(f"WARNING: File does not exist: {abs_path}")
                    
                    # Try direct hardcoded path as last resort
                    if character_id == "Cowboy":
                        direct_path = "C:\\Users\\kevin\\code\\wild-rails\\Wild Rails\\boy cow.png"
                        print(f"Trying direct path for Cowboy: {direct_path}")
                        if os.path.exists(direct_path):
                            print(f"Direct path exists, using it instead")
                            abs_path = direct_path
                    elif character_id == "Torcher":
                        direct_path = "C:\\Users\\kevin\\code\\wild-rails\\Wild Rails\\Torcher.png"
                        print(f"Trying direct path for Torcher: {direct_path}")
                        if os.path.exists(direct_path):
                            print(f"Direct path exists, using it instead")
                            abs_path = direct_path
                
                print(f"Final path: {abs_path}")
                print(f"File exists: {os.path.exists(abs_path)}")
                if os.path.exists(abs_path):
                    print(f"File size: {os.path.getsize(abs_path)} bytes")
                
                # Try to load the image with detailed error handling
                print("Attempting to load image...")
                try:
                    # First try loading without convert_alpha
                    original_img = pygame.image.load(abs_path)
                    print("Basic image loading successful")
                    
                    # Then try convert_alpha
                    try:
                        original_img = original_img.convert_alpha()
                        print("Convert alpha successful")
                    except Exception as conv_error:
                        print(f"Warning: convert_alpha failed: {conv_error}")
                        # Continue with unconverted image
                        
                    # Finally scale the image
                    self.character_imgs[character_id] = pygame.transform.scale(
                        original_img,
                        (self.player_size, self.player_size)
                    )
                    print(f"Successfully loaded and scaled {character_id} image")
                    
                except pygame.error as pe:
                    print(f"Pygame error during image loading: {pe}")
                    raise pe
                    
            except pygame.error as pe:
                print(f"Pygame error loading {character_id} image: {pe}")
                # Fallback colored rectangle if image not found
                temp_img = pygame.Surface((self.player_size, self.player_size), pygame.SRCALPHA)
                temp_img.fill((255, 100, 100))
                self.character_imgs[character_id] = temp_img
            except FileNotFoundError as fnf:
                print(f"File not found for {character_id} image: {fnf}")
                temp_img = pygame.Surface((self.player_size, self.player_size), pygame.SRCALPHA)
                temp_img.fill((255, 0, 0))
                self.character_imgs[character_id] = temp_img
            except Exception as e:
                print(f"Unexpected error loading {character_id} image: {e}")
                temp_img = pygame.Surface((self.player_size, self.player_size), pygame.SRCALPHA)
                temp_img.fill((255, 100, 100))
                self.character_imgs[character_id] = temp_img
        
        # Set current player image
        self.player_img = self.character_imgs[self.selected_character]
        
        # Load zombie image
        zombie_path = os.path.normpath(os.path.join(self.image_folder, "Zombie.png"))
        print(f"\nLoading zombie image from: {zombie_path}")
        print(f"Zombie image exists: {os.path.exists(zombie_path)}")
        
        # Try direct hardcoded path as last resort if needed
        if not os.path.exists(zombie_path):
            direct_path = "C:\\Users\\kevin\\code\\wild-rails\\Wild Rails\\Zombie.png"
            print(f"Trying direct path for Zombie: {direct_path}")
            if os.path.exists(direct_path):
                print(f"Direct path exists, using it instead")
                zombie_path = direct_path
        
        print(f"Final zombie path: {zombie_path}")
        print(f"File exists: {os.path.exists(zombie_path)}")
        
        if os.path.exists(zombie_path):
            print(f"File size: {os.path.getsize(zombie_path)} bytes")
            
        try:
            print("Attempting to load zombie image...")
            # First try loading without convert_alpha
            try:
                original_zombie = pygame.image.load(zombie_path)
                print("Basic zombie image loading successful")
                
                # Then try convert_alpha
                try:
                    original_zombie = original_zombie.convert_alpha()
                    print("Zombie convert alpha successful")
                except Exception as conv_error:
                    print(f"Warning: zombie convert_alpha failed: {conv_error}")
                    # Continue with unconverted image
                
                # Finally scale the image
                self.zombie_img = pygame.transform.scale(
                    original_zombie,
                    (48, 48)
                )
                print("Successfully loaded and scaled zombie image")
                
            except pygame.error as pe:
                print(f"Pygame error during zombie image loading: {pe}")
                raise pe
                
        except pygame.error as pe:
            print(f"Pygame error loading zombie image: {pe}")
            # Fallback to basic colored shape
            self.zombie_img = pygame.Surface((48, 48), pygame.SRCALPHA)
            self.zombie_img.fill((0, 150, 0))
        except FileNotFoundError as fnf:
            print(f"File not found for zombie image: {fnf}")
            self.zombie_img = pygame.Surface((48, 48), pygame.SRCALPHA)
            self.zombie_img.fill((0, 150, 0))
        except Exception as e:
            print(f"Unexpected error loading zombie image: {e}")
            # Fallback to basic colored shape
            self.zombie_img = pygame.Surface((48, 48), pygame.SRCALPHA)
            self.zombie_img.fill((0, 150, 0))
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
    
    def save_game(self):
        """Save game data to Wild Rails/Settings.json"""
        save_data = {
            "permanent_bonds": self.permanent_bonds,
            "owned_characters": self.owned_characters,
            "selected_character": self.selected_character
        }
        try:
            settings_path = os.path.join(self.image_folder, "Settings.json")
            with open(settings_path, "w") as f:
                json.dump(save_data, f, indent=4)
            print("Game saved successfully to Wild Rails/Settings.json")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self):
        """Load game data from Wild Rails/Settings.json"""
        try:
            settings_path = os.path.join(self.image_folder, "Settings.json")
            with open(settings_path, "r") as f:
                data = json.load(f)
                self.permanent_bonds = data.get("permanent_bonds", 0)
                self.owned_characters = data.get("owned_characters", ["Torcher"])
                self.selected_character = data.get("selected_character", "Torcher")
                print("Game loaded successfully from Wild Rails/Settings.json")
        except FileNotFoundError:
            print("No save file found, using default values")
            self.permanent_bonds = 0
            self.owned_characters = ["Torcher"]
            self.selected_character = "Torcher"
        except Exception as e:
            print(f"Error loading game: {e}")
            # Use default values on error
            self.permanent_bonds = 0
            self.owned_characters = ["Torcher"]
            self.selected_character = "Torcher"
    
    def restock_shop(self):
        """Restock the shop with new random characters based on rarity"""
        self.available_characters = []
        available_slots = 2  # Number of characters to show in shop
        
        # Get all unowned characters
        unowned = [char for char in CHARACTERS.keys() if char not in self.owned_characters]
        
        if unowned:
            # Create list of characters with their chances based on rarity
            char_chances = []
            for char in unowned:
                rarity = CHARACTERS[char]["rarity"]
                chance = RARITIES[rarity]["chance"]
                char_chances.append((char, chance))
            
            # Normalize chances
            total_chance = sum(chance for _, chance in char_chances)
            normalized_chances = [(char, chance/total_chance) for char, chance in char_chances]
            
            # Select random characters based on their chances
            while len(self.available_characters) < available_slots and unowned:
                # Random selection with weights
                rand_val = random.random()
                cumulative = 0
                for char, chance in normalized_chances:
                    cumulative += chance
                    if rand_val <= cumulative and char not in self.available_characters:
                        self.available_characters.append(char)
                        break
        
        # Reset restock timer
        self.restock_timer = 0
    
    def reset_game(self):
        """Reset game state for a new game"""
        self.wave = 1
        self.match_bonds = 0  # Reset match bonds but keep permanent bonds
        self.zombies_per_wave = 5
        self.zombies_spawned = 0
        self.spawn_timer = 0
        self.projectiles = []
        self.zombies = []
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.player_rect.x, self.player_rect.y = self.player_pos
        self.attack_cooldown = 0
        self.state = "playing"
        
        # Update player image based on selected character
        self.player_img = self.character_imgs[self.selected_character]
    
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
                
                # Get character-specific shooting behavior
                character = CHARACTERS[self.selected_character]
                num_projectiles = character["projectiles"]
                
                if num_projectiles == 1:
                    # Single projectile (Torcher)
                    # Store projectile as [x, y, vel_x, vel_y, active, damage]
                    self.projectiles.append([
                        player_center[0], player_center[1], 
                        vel_x, vel_y, True, character["damage"]
                    ])
                elif num_projectiles == 2:
                    # Two projectiles (Cowboy)
                    # Calculate perpendicular vector for spread
                    spread_distance = 10
                    perp_x, perp_y = -vel_y, vel_x  # Perpendicular to direction
                    # Normalize and scale for spread
                    perp_magnitude = math.sqrt(perp_x*perp_x + perp_y*perp_y)
                    perp_x = (perp_x / perp_magnitude) * spread_distance
                    perp_y = (perp_y / perp_magnitude) * spread_distance
                    
                    # Add two projectiles with slight offset
                    self.projectiles.append([
                        player_center[0] + perp_x/2, player_center[1] + perp_y/2,
                        vel_x, vel_y, True, character["damage"]
                    ])
                    self.projectiles.append([
                        player_center[0] - perp_x/2, player_center[1] - perp_y/2,
                        vel_x, vel_y, True, character["damage"]
                    ])
                
                # Play shoot sound
                self.shoot_sound.play()
                
                self.attack_cooldown = self.max_cooldown
    
    def update(self):
        """Update game state for one frame"""
        # Update shop restock timer
        self.restock_timer += 1
        if self.restock_timer >= self.restock_interval:
            self.restock_shop()
        
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
                    zombie[2] -= proj[5]  # Use projectile's damage value
                    proj[4] = False
                    self.projectiles.remove(proj)
                    break
            
            # Remove dead zombies and award bonds
            if zombie[2] <= 0:
                self.match_bonds += BONDS_PER_ZOMBIE  # Add bonds when zombie is killed
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
        title = self.big_font.render("WILD RAILS", True, COLORS['black'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(title, title_rect)
        
        # Menu options
        texts = [
            ("Press SPACE to Play", self.font, 50),
            ("Press S to Shop", self.font, 100),
            ("Press ESC to Quit", self.font, 150),
            ("Survive endless waves of zombies!", self.font, 250),
            ("Earn Bonds for each zombie killed", self.font, 300),
            (f"Inventory: {len(self.owned_characters)}/{MAX_INVENTORY} Characters", self.font, 350)
        ]
        
        for text, font, y_offset in texts:
            surf = font.render(text, True, COLORS['black'])
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
            self.screen.blit(surf, rect)
        
        # Draw save button
        pygame.draw.rect(self.screen, COLORS['green'], self.save_button_rect, border_radius=5)
        save_text = self.font.render("Save Game (K)", True, COLORS['white'])
        save_text_rect = save_text.get_rect(center=self.save_button_rect.center)
        self.screen.blit(save_text, save_text_rect)
        
        # Draw load button
        pygame.draw.rect(self.screen, COLORS['blue'], self.load_button_rect, border_radius=5)
        load_text = self.font.render("Load Game (L)", True, COLORS['white'])
        load_text_rect = load_text.get_rect(center=self.load_button_rect.center)
        self.screen.blit(load_text, load_text_rect)
    
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
            (f"Match Bonds: {self.match_bonds}", COLORS['gold']),
            (f"Total Bonds: {self.permanent_bonds + self.match_bonds}", COLORS['gold']),
            (f"Zombies: {len(self.zombies)}", COLORS['black']),
            (f"Character: {self.selected_character}", COLORS['black']),
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
        # Add match bonds to permanent bonds when game over
        self.permanent_bonds += self.match_bonds
        
        texts = [
            ("GAME OVER", self.big_font, COLORS['red'], -100),
            (f"Wave Reached: {self.wave}", self.font, COLORS['black'], -50),
            (f"Bonds Earned This Run: {self.match_bonds}", self.font, COLORS['gold'], 0),
            (f"Total Bonds: {self.permanent_bonds}", self.font, COLORS['gold'], 50),
            ("Press SPACE to return to Menu", self.font, COLORS['black'], 150),
            ("Press ESC to Quit", self.font, COLORS['black'], 200)
        ]
        
        for text, font, color, y_offset in texts:
            surf = font.render(text, True, color)
            rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
            self.screen.blit(surf, rect)
    
    def draw_shop(self):
        """Draw the shop screen with available characters"""
        # Title
        title = self.big_font.render("CHARACTER SHOP", True, COLORS['black'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)
        
        # Display current bonds and inventory space
        bonds_text = self.font.render(f"Your Bonds: {self.permanent_bonds}", True, COLORS['gold'])
        self.screen.blit(bonds_text, (SCREEN_WIDTH//2 - 100, 130))
        
        inventory_text = self.font.render(f"Inventory: {len(self.owned_characters)}/{MAX_INVENTORY} Characters", 
                                       True, COLORS['black'])
        self.screen.blit(inventory_text, (SCREEN_WIDTH//2 - 100, 170))
        
        # Display restock timer
        restock_minutes = (self.restock_interval - self.restock_timer) // (60 * FPS)
        restock_seconds = ((self.restock_interval - self.restock_timer) % (60 * FPS)) // FPS
        timer_text = self.font.render(f"Restock in: {restock_minutes}:{restock_seconds:02d}", True, COLORS['black'])
        self.screen.blit(timer_text, (SCREEN_WIDTH//2 - 100, 210))
        
        # Shop instructions
        instruction = self.font.render("Press ESC to return to menu", True, COLORS['black'])
        self.screen.blit(instruction, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 50))
        
        mouse_tip = self.font.render("Click on character to buy", True, COLORS['black'])
        self.screen.blit(mouse_tip, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 20))
        
        character_spacing = 250
        
        # Reset clickable areas
        self.shop_clickable_areas = {}
        
        # Display owned characters section
        owned_title = self.font.render("Your Characters:", True, COLORS['black'])
        self.screen.blit(owned_title, (50, 230))
        for i, char_id in enumerate(self.owned_characters):
            char_data = CHARACTERS[char_id]
            x_pos = 50 + (i % 3) * character_spacing  # Show 3 per row
            y_pos = 270 + (i // 3) * 220  # New row every 3 characters
            
            # Draw character card background based on rarity
            rarity = char_data["rarity"]
            rarity_color = RARITIES[rarity]["color"]
            
            # Define the character card rectangle
            card_rect = pygame.Rect(x_pos - 10, y_pos - 10, 220, 180)
            
            # Store the clickable area for selection
            self.shop_clickable_areas[f"owned_{i}"] = {
                "rect": card_rect,
                "type": "select",
                "character": char_id
            }
            
            # Highlight if this is the character being hovered
            if self.shop_hover == f"owned_{i}":
                pygame.draw.rect(self.screen, (220, 220, 220), 
                               (x_pos - 15, y_pos - 15, 230, 190), 
                               border_radius=7)
            
            pygame.draw.rect(self.screen, rarity_color, card_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['white'], 
                           (x_pos - 5, y_pos - 5, 210, 170), 
                           border_radius=3)
            
            # Draw character image
            self.screen.blit(self.character_imgs[char_id], (x_pos, y_pos))
            
            # Draw character name and rarity
            name_text = self.font.render(char_data["name"], True, COLORS['black'])
            self.screen.blit(name_text, (x_pos + 70, y_pos + 10))
            
            rarity_text = self.font.render(rarity, True, rarity_color)
            self.screen.blit(rarity_text, (x_pos + 70, y_pos + 40))
            
            # Draw character stats
            stats_text = self.font.render(f"DMG: {char_data['damage']}", True, COLORS['black'])
            self.screen.blit(stats_text, (x_pos + 70, y_pos + 70))
            
            # Show selected status or select button
            if char_id == self.selected_character:
                selected_text = self.font.render("SELECTED", True, COLORS['green'])
                self.screen.blit(selected_text, (x_pos + 70, y_pos + 100))
            else:
                select_text = self.font.render("Click to Select", True, COLORS['black'])
                self.screen.blit(select_text, (x_pos + 70, y_pos + 100))
            
            # Show sell button (don't allow selling the only character or the selected character)
            if len(self.owned_characters) > 1 and char_id != self.selected_character:
                # Calculate sell price (50% of purchase price)
                sell_price = CHARACTERS[char_id]["price"] // 2
                
                # Store the clickable area for selling
                sell_rect = pygame.Rect(x_pos + 70, y_pos + 130, 140, 30)
                self.shop_clickable_areas[f"sell_{i}"] = {
                    "rect": sell_rect,
                    "type": "sell",
                    "character": char_id,
                    "price": sell_price
                }
                
                # Draw sell button
                pygame.draw.rect(self.screen, COLORS['red'], sell_rect, border_radius=3)
                sell_text = self.font.render(f"Sell for {sell_price}", True, COLORS['white'])
                self.screen.blit(sell_text, (x_pos + 75, y_pos + 135))
        
        # Display available characters for purchase (only from restock)
        if self.available_characters:
            available_title = self.font.render("Available for Purchase:", True, COLORS['black'])
            self.screen.blit(available_title, (50, 500))
            
            for i, char_id in enumerate(self.available_characters):
                char_data = CHARACTERS[char_id]
                x_pos = 50 + i * character_spacing
                y_pos = 540
                
                # Draw character card background based on rarity
                rarity = char_data["rarity"]
                rarity_color = RARITIES[rarity]["color"]
                
                # Check if player can afford this character and has inventory space
                can_afford = self.permanent_bonds >= char_data['price']
                has_space = len(self.owned_characters) < MAX_INVENTORY
                can_buy = can_afford and has_space
                
                # Define the character card rectangle
                card_rect = pygame.Rect(x_pos - 10, y_pos - 10, 220, 180)
                
                # Store the clickable area for purchase
                self.shop_clickable_areas[f"available_{i}"] = {
                    "rect": card_rect,
                    "type": "buy",
                    "character": char_id,
                    "can_afford": can_afford,
                    "has_space": has_space
                }
                
                # Highlight if this is the character being hovered
                if self.shop_hover == f"available_{i}":
                    highlight_color = COLORS['green'] if can_buy else COLORS['red']
                    pygame.draw.rect(self.screen, highlight_color, 
                                   (x_pos - 15, y_pos - 15, 230, 190), 
                                   border_radius=7)
                
                pygame.draw.rect(self.screen, rarity_color, card_rect, border_radius=5)
                pygame.draw.rect(self.screen, COLORS['white'], 
                               (x_pos - 5, y_pos - 5, 210, 170), 
                               border_radius=3)
                
                # Draw character image
                self.screen.blit(self.character_imgs[char_id], (x_pos, y_pos))
                
                # Draw character name and rarity
                name_text = self.font.render(char_data["name"], True, COLORS['black'])
                self.screen.blit(name_text, (x_pos + 70, y_pos + 10))
                
                rarity_text = self.font.render(rarity, True, rarity_color)
                self.screen.blit(rarity_text, (x_pos + 70, y_pos + 40))
                
                # Draw character stats
                stats_text = self.font.render(f"DMG: {char_data['damage']}", True, COLORS['black'])
                self.screen.blit(stats_text, (x_pos + 70, y_pos + 70))
                
                # Show price
                price_text = self.font.render(f"{char_data['price']} Bonds", True, COLORS['gold'])
                self.screen.blit(price_text, (x_pos + 70, y_pos + 100))
                
                # Show buy button
                buy_text = self.font.render("Click to Buy", True, 
                                         COLORS['green'] if can_buy else COLORS['red'])
                self.screen.blit(buy_text, (x_pos + 70, y_pos + 130))
                
                # Add feedback messages
                if not can_afford:
                    insufficient_text = self.font.render("Not enough bonds!", True, COLORS['red'])
                    self.screen.blit(insufficient_text, (x_pos + 70, y_pos + 150))
                elif not has_space:
                    full_text = self.font.render("Inventory full!", True, COLORS['red'])
                    self.screen.blit(full_text, (x_pos + 70, y_pos + 150))
        else:
            no_stock_text = self.font.render("No characters available. Wait for restock.", True, COLORS['red'])
            self.screen.blit(no_stock_text, (SCREEN_WIDTH//2 - 180, 540))
    
    def draw(self):
        """Render the current game state"""
        self.screen.fill(COLORS['sand'])
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "shop":
            self.draw_shop()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Handle mouse movement for hover effects in shop
                elif event.type == pygame.MOUSEMOTION and self.state == "shop":
                    mouse_pos = pygame.mouse.get_pos()
                    self.shop_hover = None
                    
                    # Check if mouse is over any clickable area
                    for area_id, area_data in self.shop_clickable_areas.items():
                        if area_data["rect"].collidepoint(mouse_pos):
                            self.shop_hover = area_id
                            break
                
                # Handle mouse clicks in menu (for save/load buttons)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == "menu":
                    mouse_pos = pygame.mouse.get_pos()
                    if self.save_button_rect.collidepoint(mouse_pos):
                        if self.save_game():
                            print("Game saved successfully!")
                    elif self.load_button_rect.collidepoint(mouse_pos):
                        self.load_game()
                        print("Game loaded successfully!")
                        # Update player image after loading
                        self.player_img = self.character_imgs[self.selected_character]
                
                # Handle mouse clicks in shop
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == "shop":
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if any clickable area was clicked
                    for area_id, area_data in self.shop_clickable_areas.items():
                        if area_data["rect"].collidepoint(mouse_pos):
                            if area_data["type"] == "select":
                                # Select owned character
                                self.selected_character = area_data["character"]
                                self.player_img = self.character_imgs[self.selected_character]
                                print(f"Selected character: {self.selected_character}")
                            
                            elif area_data["type"] == "buy" and area_data["can_afford"] and area_data["has_space"]:
                                # Buy new character
                                char_id = area_data["character"]
                                char_price = CHARACTERS[char_id]["price"]
                                
                                self.permanent_bonds -= char_price
                                self.owned_characters.append(char_id)
                                self.available_characters.remove(char_id)
                                self.selected_character = char_id
                                self.player_img = self.character_imgs[char_id]
                                print(f"Purchased character: {char_id}")
                                
                                # Auto-save after purchase
                                self.save_game()
                            
                            elif area_data["type"] == "sell":
                                # Sell character
                                char_id = area_data["character"]
                                sell_price = area_data["price"]
                                
                                # Remove from owned characters and add bonds
                                self.owned_characters.remove(char_id)
                                self.permanent_bonds += sell_price
                                print(f"Sold character {char_id} for {sell_price} bonds")
                                
                                # Auto-save after selling
                                self.save_game()
                            break
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            # Add match bonds to permanent bonds when returning to menu
                            self.permanent_bonds += self.match_bonds
                            self.match_bonds = 0
                            self.state = "menu"
                            # Auto-save when returning to menu
                            self.save_game()
                        elif self.state == "shop":
                            self.state = "menu"
                            # Auto-save when leaving shop
                            self.save_game()
                        else:
                            # Auto-save before quitting
                            self.save_game()
                            self.running = False
                    elif event.key == pygame.K_SPACE:
                        if self.state == "menu":
                            self.reset_game()
                        elif self.state == "game_over":
                            self.state = "menu"
                        elif self.state == "playing":
                            self.shoot()
                    elif event.key == pygame.K_s and self.state == "menu":
                        self.state = "shop"
                    elif event.key == pygame.K_k and self.state == "menu":
                        # Save game with K key
                        self.save_game()
                    elif event.key == pygame.K_l and self.state == "menu":
                        # Load game with L key
                        self.load_game()
                        # Update player image after loading
                        self.player_img = self.character_imgs[self.selected_character]
                        
                    # Handle shop interactions with keyboard
                    if self.state == "shop":
                        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                            # Convert key to index (K_1 -> 0, K_2 -> 1, etc.)
                            char_index = event.key - pygame.K_1
                            
                            # Only use number keys for selecting owned characters
                            if char_index < len(self.owned_characters):
                                char_id = self.owned_characters[char_index]
                                self.selected_character = char_id
                                self.player_img = self.character_imgs[char_id]
                                print(f"Selected character: {char_id}")
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Stop music before quitting
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Print emoji instructions for copying
    emoji_instructions = """
🎮 Wild Rails - Zombie Survival 🧟
================================

📋 Controls:
🎯 WASD: Move character
🔫 SPACE: Shoot at mouse cursor
🛍️ S: Open shop from menu
💾 L: Load saved game
💾 K: Save game
❌ ESC: Return to menu/Quit

🎯 Objective: 
Survive endless waves and collect Bonds! 💰

⭐ Characters:
🔥 Torcher: Default character
🤠 Cowboy: 25 Bonds, higher damage
🔫 Shotgunner: 50 Bonds, epic damage
🧟 Mummy: 50 Bonds, epic damage
🐎 Horse: 100 Bonds, legendary damage
🧛 Vampire: 100 Bonds, melee attacks
🐺 Werewolf: 200 Bonds, AOE damage
⚡ Tesla: 500 Bonds, highest damage

💎 Rarities:
⚪ Common: 40% chance
🔷 Rare: 30% chance
🟣 Epic: 15% chance
🟡 Legendary: 10% chance
🔮 Mythic: 4% chance
✨ Godly: 1% chance

💰 Shop System:
- Shows 2 random characters
- Restocks every 5 minutes
- Max 4 characters in inventory
- Can sell characters for bonds
"""
    print(emoji_instructions)
    print("Starting game...")
    
    Game().run()
