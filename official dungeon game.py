#fixed warped screen in fullscreen
#added 3 enemy types
#added wave system
#added wave number display
#enemy animations
#enemy and player spawn at random locations and enemy come from random locations every wave
#player attack cooldown in seconds currently 1ms
#more enemies every round that get stronger while player gets stronger
#player regenerates health after 5 seconds
#death menu with waves survived and restart option
#attack damage of player increase every round and enemy health increase and number of enemies increase every round
#added music for battle immersion
#Added lava in the map as obstacles

import pygame
import random
from pygame.locals import *
import json
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Load and play background music
MUSIC_PATH = r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\dungeon music(onepiece).mp3"  # Update with the correct path to your music file
pygame.mixer.music.load(MUSIC_PATH)
pygame.mixer.music.play(-1)  # Play the music indefinitely (loop)

# Game Constants
SCALE_FACTOR = 1.5  # Adjust this value to control the size of the tiles
SPRITE_SCALE_FACTOR = 3
SPRITE_SIZE = int(8 * SPRITE_SCALE_FACTOR * SCALE_FACTOR)
ATTACK_RANGE = 3  # Adjust range as needed
PLAYER_MOVEMENT_SPEED = 0.4  # Adjusted for slower movement
ENEMY_MOVEMENT_SPEED = 0.375  # Keep enemy speed as is
ENEMY_ATTACK_COOLDOWN_TIME = 5  # Cooldown time in frames (adjust as needed)
ENEMY_ATTACK_RANGE = 1  # Adjust range as needed

# Wave System Constants
INITIAL_ENEMIES_PER_WAVE = 3
ENEMY_INCREMENT_PER_WAVE = 3

# Window size
WIDTH = 1800
HEIGHT = 950

# Load custom font
CUSTOM_FONT_PATH = r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\fonts\Dungeon Depths.ttf"  # Update with correct path to font
font_size = 30
small_font_size = 20
custom_font = pygame.font.Font(CUSTOM_FONT_PATH, font_size)
small_custom_font = pygame.font.Font(CUSTOM_FONT_PATH, small_font_size)

# Increase dungeon dimensions
ROWS = 75
COLS = 150

# Adjust TILE_SIZE to fit the screen dimensions
TILE_SIZE = int(min(WIDTH // COLS, HEIGHT // ROWS) * SCALE_FACTOR)
SPRITE_SIZE = TILE_SIZE * SPRITE_SCALE_FACTOR

def load_dungeon_layout(file_path):
    with open(file_path, 'r') as file:
        layout = [list(map(int, line.strip())) for line in file]
    return layout

def adjust_dungeon_layout(file_path, rows, cols):
    # Create a new layout with 1s around the edge and 0s inside the middle
    layout = [[1 if r == 0 or r == rows - 1 or c == 0 or c == cols - 1 else 0 for c in range(cols)] for r in range(rows)]

    # Write the adjusted layout to the file
    with open(file_path, 'w') as file:
        for row in layout:
            file.write(''.join(map(str, row)) + '\n')

# Adjust the dungeon layout to fit the whole screen with 1s around the edge and 0s inside the middle
adjust_dungeon_layout(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\dungeongame_layout.txt", ROWS, COLS)

# Load the dungeon layout from the file
dungeon_layout = load_dungeon_layout(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\dungeongame_layout.txt")
print(f"Dungeon layout dimensions: {len(dungeon_layout)} rows, {len(dungeon_layout[0])} columns")

# Load image function
def load_image(file_path, scale_width=None, scale_height=None):
    try:
        image = pygame.image.load(file_path)
        if scale_width and scale_height:
            image = pygame.transform.scale(image, (scale_width, scale_height))
        return image
    except pygame.error as e:
        print(f"Failed to load image {file_path}: {e}")
        return None

def load_frames(directory, scale_width=None, scale_height=None):
    frames = []
    print(f"Loading frames from directory: {directory}")  # Debug statement
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".png"):
            frame = load_image(os.path.join(directory, filename), scale_width, scale_height)
            if frame:
                frames.append(frame)
                print(f"Loaded frame: {filename}")  # Debug statement
            else:
                print(f"Failed to load frame: {filename}")
        else:
            print(f"Skipping non-PNG file: {filename}")
    if not frames:
        print(f"No frames loaded from directory: {directory}")
    return frames


# Load tile images and scale them using SCALE_FACTOR
floor_image = load_image(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\other images\Dungeon_Floor.png", int(TILE_SIZE * SCALE_FACTOR), int(TILE_SIZE * SCALE_FACTOR))  # Update path

# Define the Animation class first
class Animation:
    def __init__(self, frames, frame_duration):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_since_last_frame = 0

    def update(self, dt):
        if not self.frames:
            return  # Do nothing if frames list is empty
        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.frame_duration:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_current_frame(self):
        if not self.frames:
            return None  # Return None if frames list is empty
        return self.frames[self.current_frame]

# Load animation frames
down_attack_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\DownAttack", SPRITE_SIZE, SPRITE_SIZE)
down_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\DownRun", SPRITE_SIZE, SPRITE_SIZE)
left_attack_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\LeftAttack", SPRITE_SIZE, SPRITE_SIZE)
left_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\LeftRun", SPRITE_SIZE, SPRITE_SIZE)
right_attack_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\RightAttack", SPRITE_SIZE, SPRITE_SIZE)
right_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\RightRun", SPRITE_SIZE, SPRITE_SIZE)
up_attack_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\UpAttack", SPRITE_SIZE, SPRITE_SIZE)
up_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\UpRun", SPRITE_SIZE, SPRITE_SIZE)

# Load demon running frames
demon_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Demon enemy", SPRITE_SIZE, SPRITE_SIZE)
demon_animations = {
    "run": Animation(demon_run_frames, 100)
}

# Load ogre running frames
ogre_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Goblin enemy", SPRITE_SIZE, SPRITE_SIZE)
ogre_animations = {
    "run": Animation(ogre_run_frames, 100)
}

# Load zombie running frames
zombie_run_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Zombie enemy", SPRITE_SIZE, SPRITE_SIZE)
zombie_animations = {
    "run": Animation(zombie_run_frames, 100)
}

# Load lava animation frames
lava_frames = load_frames(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\lava_images", int(TILE_SIZE * SCALE_FACTOR), int(TILE_SIZE * SCALE_FACTOR))  # Update path

# Initialize lava_animation
lava_animation = Animation(lava_frames, 100) if lava_frames else Animation([], 100)

# Check if lava_frames is empty
if not lava_frames:
    print("Error: No lava frames loaded. Please check the directory path and ensure it contains PNG files.")

# Load idle frame
idle_frame = load_image(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\Sprites\DownRun\DownRun1.png", SPRITE_SIZE, SPRITE_SIZE)

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.max_health = 100  # Store the maximum health
        self.position = [1, 1]  # Use integer values for position
        self.attack_power = 20  # Initial attack power
        self.last_attack_time = pygame.time.get_ticks()  # Track the time since the player last attacked
        self.last_damage_time = pygame.time.get_ticks()  # Track the time since the player last took damage
        self.last_input_time = pygame.time.get_ticks()  # Track the time since the last input
        self.idle_timeout = 3000  # 3 seconds in milliseconds
        self.regeneration_cooldown = 5000  # 5 seconds in milliseconds
        self.regeneration_rate = 1  # Health points to regenerate per interval
        self.animations = {
            "down_attack": Animation(down_attack_frames, 100),
            "down_run": Animation(down_run_frames, 100),
            "left_attack": Animation(left_attack_frames, 100),
            "left_run": Animation(left_run_frames, 100),
            "right_attack": Animation(right_attack_frames, 100),
            "right_run": Animation(right_run_frames, 100),
            "up_attack": Animation(up_attack_frames, 100),
            "up_run": Animation(up_run_frames, 100),
            "idle": Animation([idle_frame], 100)  # Single frame for idle
        }
        self.current_animation = self.animations["idle"]
        self.rect = pygame.Rect(self.position[1] * TILE_SIZE, self.position[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def move(self, dx, dy):
        new_row = self.position[0] + dy * PLAYER_MOVEMENT_SPEED
        new_col = self.position[1] + dx * PLAYER_MOVEMENT_SPEED
        if can_move_to(int(new_row), int(new_col)):
            self.position[0] = new_row
            self.position[1] = new_col
            self.rect.topleft = (self.position[1] * TILE_SIZE, self.position[0] * TILE_SIZE)
            if dx > 0:
                self.current_animation = self.animations["right_run"]
            elif dx < 0:
                self.current_animation = self.animations["left_run"]
            elif dy > 0:
                self.current_animation = self.animations["down_run"]
            elif dy < 0:
                self.current_animation = self.animations["up_run"]

    def attack(self):
        if self.current_animation in [self.animations["down_run"], self.animations["idle"]]:
            self.current_animation = self.animations["down_attack"]
        elif self.current_animation in [self.animations["left_run"], self.animations["idle"]]:
            self.current_animation = self.animations["left_attack"]
        elif self.current_animation in [self.animations["right_run"], self.animations["idle"]]:
            self.current_animation = self.animations["right_attack"]
        elif self.current_animation in [self.animations["up_run"], self.animations["idle"]]:
            self.current_animation = self.animations["up_attack"]

    def take_damage(self, damage):
        self.health -= damage
        self.last_damage_time = pygame.time.get_ticks()  # Reset the damage timer
        if self.health <= 0:
            self.health = 0

    def regenerate_health(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time >= self.regeneration_cooldown:
            self.health = min(self.health + self.regeneration_rate, self.max_health)

    def increase_attack_power(self, amount):
        self.attack_power += amount

    def update(self, dt):
        self.current_animation.update(dt)
        self.regenerate_health()  # Regenerate health if applicable

        # Check if the player should go idle
        current_time = pygame.time.get_ticks()
        if current_time - self.last_input_time >= self.idle_timeout:
            self.current_animation = self.animations["idle"]

    def get_current_frame(self):
        return self.current_animation.get_current_frame()

class Enemy:
    def __init__(self, id, health, attack_power, animations):
        self.id = id
        self.health = health
        self.max_health = health  # Store the maximum health
        self.attack_power = attack_power
        self.position = [5, 5]
        self.animations = animations
        self.current_animation = self.animations["run"]
        self.sprite_image = self.current_animation.get_current_frame()
        self.active = True
        self.attack_cooldown = 0  # Initialize attack cooldown
        self.velocity = [0, 0]  # Initialize velocity

    def update_position(self, player_position):
        if self.active:
            delta_x = player_position[1] - self.position[1]
            delta_y = player_position[0] - self.position[0]
            distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
            if distance != 0:
                direction_x = delta_x / distance
                direction_y = delta_y / distance

                # Apply steering behavior for smoother movement
                self.velocity[0] += direction_x * 0.1
                self.velocity[1] += direction_y * 0.1

                # Limit the velocity to the enemy movement speed
                speed = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
                if speed > ENEMY_MOVEMENT_SPEED:
                    self.velocity[0] = (self.velocity[0] / speed) * ENEMY_MOVEMENT_SPEED
                    self.velocity[1] = (self.velocity[1] / speed) * ENEMY_MOVEMENT_SPEED

                self.position[1] += self.velocity[0]
                self.position[0] += self.velocity[1]

            self.position[0] = max(0, min(self.position[0], ROWS - 1))
            self.position[1] = max(0, min(self.position[1], COLS - 1))
            self.sprite_image = self.current_animation.get_current_frame()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.active = False

    def attack_player(self, player):
        if self.attack_cooldown <= 0:
            player_row, player_col = player.position
            enemy_row, enemy_col = self.position
            distance = ((player_row - enemy_row) ** 2 + (player_col - enemy_col) ** 2) ** 0.5
            if distance <= ENEMY_ATTACK_RANGE:
                player.health -= self.attack_power
                print(f"The enemy attacked you! Your health is now {player.health}.")
                self.attack_cooldown = ENEMY_ATTACK_COOLDOWN_TIME  # Reset cooldown

    def update_cooldown(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def update(self, dt):
        self.current_animation.update(dt)
        self.sprite_image = self.current_animation.get_current_frame()

class DamageText:
    def __init__(self, text, position, duration=1000, font_size=20):
        self.text = text  # The text to display (e.g., "-10")
        self.position = position  # The position to display the text
        self.duration = duration  # The duration the text should be visible (in milliseconds)
        self.start_time = pygame.time.get_ticks()  # The time when the text was created
        self.alpha = 255  # The transparency of the text (255 is fully opaque)
        self.font_size = font_size  # The font size of the text
        self.font = pygame.font.Font(CUSTOM_FONT_PATH, self.font_size)  # The font used to render the text

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time  # Calculate the elapsed time since the text was created
        if elapsed_time > self.duration:
            self.alpha = 0  # Make the text fully transparent if the duration has passed
        else:
            self.alpha = 255 - int((elapsed_time / self.duration) * 255)  # Gradually fade out the text

    def draw(self, surface):
        if self.alpha > 0:  # Only draw the text if it is not fully transparent
            font_surface = self.font.render(self.text, True, (255, 0, 0))  # Render the text in red
            font_surface.set_alpha(self.alpha)  # Set the transparency of the text
            surface.blit(font_surface, self.position)  # Draw the text on the given surface at the specified position

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        # Apply the camera offset to the given rectangle
        return rect.move(self.camera.topleft)

    def update(self, target):
        # Calculate the new camera position based on the target's position
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit scrolling to map size
        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width - WIDTH), x)  # Right
        y = max(-(self.height - HEIGHT), y)  # Bottom

        # Update the camera rectangle with the new position
        self.camera = pygame.Rect(x, y, self.width, self.height)

# Create instances of Enemy and Player
enemy = Enemy(1, 10, 1, {"run": Animation(down_run_frames, 100)})  # Example initialization
player = None

# Initialize the enemies list
enemies = []

damage_texts = []

def draw_dungeon(camera):
    for row in range(len(dungeon_layout)):
        for col in range(len(dungeon_layout[0])):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if dungeon_layout[row][col] == 1:
                current_frame = lava_animation.get_current_frame()
                if (current_frame):
                    screen.blit(current_frame, camera.apply(tile_rect).topleft)
                else:
                    print("Warning: No current frame for lava animation.")
            else:
                screen.blit(floor_image, camera.apply(tile_rect).topleft)

def draw_player(camera):
    if player:
        sprite_x = int(player.position[1] * TILE_SIZE)
        sprite_y = int(player.position[0] * TILE_SIZE)
        screen.blit(player.get_current_frame(), camera.apply(pygame.Rect(sprite_x, sprite_y, TILE_SIZE, TILE_SIZE)).topleft)

def draw_enemy(camera):
    if enemy.active:
        sprite_x = int(enemy.position[1] * TILE_SIZE)
        sprite_y = int(enemy.position[0] * TILE_SIZE)
        screen.blit(enemy.sprite_image, camera.apply(pygame.Rect(sprite_x, sprite_y, TILE_SIZE, TILE_SIZE)).topleft)

def draw_enemies(camera):
    for enemy in enemies:
        if enemy.active:
            sprite_x = int(enemy.position[1] * TILE_SIZE)
            sprite_y = int(enemy.position[0] * TILE_SIZE)
            screen.blit(enemy.sprite_image, camera.apply(pygame.Rect(sprite_x, sprite_y, TILE_SIZE, TILE_SIZE)).topleft)

def draw_health(camera):
    x_offset = 20  # Adjust this value to control the horizontal offset

    if player:
        sprite_x = int(player.position[1] * TILE_SIZE)
        sprite_y = int(player.position[0] * TILE_SIZE)
        health_bar_width = 50  # Width of the health bar
        health_bar_height = 5  # Height of the health bar
        health_bar_offset = 7  # Offset above the player sprite
        health_bar_rect = pygame.Rect(sprite_x + (TILE_SIZE - health_bar_width) // 2 + x_offset, sprite_y - health_bar_height - health_bar_offset, health_bar_width, health_bar_height)
        draw_health_bar(screen, camera.apply(health_bar_rect).topleft, health_bar_width, health_bar_height, player.health, 100)

    for enemy in enemies:
        if enemy.active:
            sprite_x = int(enemy.position[1] * TILE_SIZE)
            sprite_y = int(enemy.position[0] * TILE_SIZE)
            health_bar_width = 50  # Width of the health bar
            health_bar_height = 5  # Height of the health bar
            health_bar_offset = 8  # Offset above the enemy sprite
            health_bar_rect = pygame.Rect(sprite_x + (TILE_SIZE - health_bar_width) // 2 + x_offset, sprite_y - health_bar_height - health_bar_offset, health_bar_width, health_bar_height)
            draw_health_bar(screen, camera.apply(health_bar_rect).topleft, health_bar_width, health_bar_height, enemy.health, enemy.max_health)  # Use enemy's max health

def draw_health_bar(surface, position, width, height, health, max_health):
    """Draw a health bar on the given surface."""
    x, y = position
    # Calculate the health bar width based on the current health
    health_bar_width = int(width * (health / max_health))

    # Draw the background of the health bar (empty health)
    pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))

    # Draw the foreground of the health bar (current health)
    pygame.draw.rect(surface, (0, 255, 0), (x, y, health_bar_width, height))

def update_gameplay(dt):
    global player, mouse_click

    if player:
        if player.health <= 0:
            display_game_over()
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # Handle movement
        if keys[K_LEFT] or keys[K_a]:
            dx -= 1
        if keys[K_RIGHT] or keys[K_d]:
            dx += 1
        if keys[K_UP] or keys[K_w]:
            dy -= 1
        if keys[K_DOWN] or keys[K_s]:
            dy += 1

        if dx != 0 or dy != 0 or pygame.mouse.get_pressed()[0]:
            player.last_input_time = pygame.time.get_ticks()  # Update the last input time

        player.move(dx, dy)  # Move the player based on input

        for enemy in enemies:
            enemy.update_position(player.position)  # Update enemy position
            enemy.update(dt)  # Update enemy animation

        # Check for attacking the enemy with left-click
        if pygame.mouse.get_pressed()[0]:  # Left-click to attack
            if not mouse_click:  # Only attack if mouse wasn't clicked previously
                player.attack()
                if can_attack_enemy():
                    attack_enemy()
                mouse_click = True  # Set click state to True to prevent continuous attacking
        else:
            mouse_click = False  # Reset click state when mouse is not pressed

        # Enemy attacks player if in range and cooldown has passed
        for enemy in enemies:
            if can_enemy_attack_player(enemy) and enemy.attack_cooldown <= 0:
                enemy.attack_player(player)
                player.take_damage(enemy.attack_power)  # Call take_damage when the player is attacked

            # Update enemy attack cooldown
            enemy.update_cooldown()

        # Update player animation
        player.update(dt)

        print(f"Player position: {player.position}, Health: {player.health}")  # Debug print

def can_attack_enemy():
    """Check if the player is within the attack range of any enemy."""
    player_row, player_col = player.position
    for enemy in enemies:
        if enemy.active:
            enemy_row, enemy_col = enemy.position
            distance = ((player_row - enemy_row) ** 2 + (player_col - enemy_col) ** 2) ** 0.5
            if distance <= ATTACK_RANGE:
                return True
    return False

def can_enemy_attack_player(enemy):
    """Check if the enemy is within the attack range of the player and is active."""
    if not enemy.active:
        return False
    player_row, player_col = player.position
    enemy_row, enemy_col = enemy.position
    distance = ((player_row - enemy_row) ** 2 + (player_col - enemy_col) ** 2) ** 0.5
    return distance <= ENEMY_ATTACK_RANGE

def attack_enemy():
    """Execute an attack on the nearest enemy."""
    if not any(enemy.active for enemy in enemies):
        return  # Do nothing if all enemies are already dead

    damage = player.attack_power  # Use player's attack power for damage

    # Find the nearest enemy within attack range
    player_row, player_col = player.position
    for enemy in enemies:
        if enemy.active:
            enemy_row, enemy_col = enemy.position
            distance = ((player_row - enemy_row) ** 2 + (player_col - enemy_col) ** 2) ** 0.5
            if distance <= ATTACK_RANGE:
                print(f"Attempting to attack the enemy! Current enemy health: {enemy.health}")

                # Create a DamageText instance with the damage dealt at a random position near the player
                sprite_x = int(player.position[1] * TILE_SIZE)
                sprite_y = int(player.position[0] * TILE_SIZE)
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-20, 20)
                damage_texts.append(DamageText(f"-{damage}", (sprite_x + offset_x, sprite_y + offset_y - 20), font_size=15))

                enemy.take_damage(damage)
                print(f"You attacked the enemy for {damage} damage. Enemy health is now {enemy.health}.")
                if enemy.health <= 0:
                    enemy.active = False  # Mark the enemy as inactive if defeated
                    print("The enemy has been defeated!")
                break

def display_game_over():
    """Display the game over screen."""
    screen.fill((0, 0, 0))
    game_over_text = custom_font.render("You Died", True, (255, 0, 0))
    rounds_survived_text = custom_font.render(f"Rounds Survived: {current_wave}", True, (255, 255, 255))
    try_again_text = custom_font.render("Try Again", True, (255, 255, 255))

    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    rounds_survived_rect = rounds_survived_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    try_again_rect = try_again_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(rounds_survived_text, rounds_survived_rect)
    screen.blit(try_again_text, try_again_rect)

    return try_again_rect

def can_move_to(new_row, new_col):
    """Check if the player can move to a new tile."""
    if 0 <= new_row < len(dungeon_layout) and 0 <= new_col < len(dungeon_layout[0]):
        return dungeon_layout[new_row][new_col] == 0  # Check if the tile is empty (floor)
    return False

# Function to find an empty tile in the dungeon layout
def find_empty_tile():
    for row in range(len(dungeon_layout)):
        for col in range(len(dungeon_layout[0])):
            if dungeon_layout[row][col] == 0:  # Check if the tile is empty (floor)
                return row, col
    return None, None  # Return None if no empty tile is found

import random

def find_empty_tile(avoid_positions=None):
    if avoid_positions is None:
        avoid_positions = []
    empty_tiles = [(row, col) for row in range(len(dungeon_layout)) for col in range(len(dungeon_layout[0])) if dungeon_layout[row][col] == 0 and (row, col) not in avoid_positions]
    if empty_tiles:
        return random.choice(empty_tiles)
    return None, None  # Return None if no empty tile is found

# Function to restart the game by resetting the player and enemy
def restart_game():
    """Reset the game state for a new game."""
    global player, enemies, current_wave, enemies_per_wave, time_since_last_wave
    avoid_positions = []

    # Find positions for the enemies first
    for _ in range(INITIAL_ENEMIES_PER_WAVE):
        enemy_row, enemy_col = find_empty_tile(avoid_positions)
        if enemy_row is not None and enemy_col is not None:
            avoid_positions.append((enemy_row, enemy_col))

    # Find a position for the player that is not in the avoid_positions
    player_row, player_col = find_empty_tile(avoid_positions)
    if player_row is not None and player_col is not None:
        player = Player("Player")
        player.position = [player_row, player_col]  # Set player position to the empty tile
    else:
        print("No empty tile found for player spawn.")

    # Reset wave system
    current_wave = 1
    enemies_per_wave = INITIAL_ENEMIES_PER_WAVE
    time_since_last_wave = 0
    spawn_wave(enemies_per_wave)

# Function to draw the start screen with title, play, and help options
def draw_start_screen():
    screen.fill((0, 0, 0))
    title_text = custom_font.render("Dungeon Crawler", True, (255, 255, 255))
    play_text = custom_font.render("Play", True, (255, 255, 255))
    help_text = custom_font.render("Help", True, (255, 255, 255))

    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
    play_rect = play_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    help_rect = help_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60))

    screen.blit(title_text, title_rect)
    screen.blit(play_text, play_rect)
    screen.blit(help_text, help_rect)

    return play_rect, help_rect

# Function to create a fade-in effect when starting the game
def fade_in():
    camera = Camera(len(dungeon_layout[0]) * TILE_SIZE, len(dungeon_layout[0]) * TILE_SIZE)
    fade_surface = pygame.Surface((screen.get_width(), screen.get_height()))
    fade_surface.fill((0, 0, 0))
    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))
        draw_dungeon(camera)
        draw_health(camera)
        draw_player(camera)
        draw_enemies(camera)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)

def spawn_wave(num_enemies):
    """Spawn a new wave of enemies."""
    global enemies
    enemies = []
    avoid_positions = []

    for _ in range(num_enemies):
        enemy_row, enemy_col = find_empty_tile(avoid_positions)
        if enemy_row is not None and enemy_col is not None:
            avoid_positions.append((enemy_row, enemy_col))
            # Randomly choose an enemy type
            enemy_type = random.choice(["demon", "ogre", "zombie"])
            base_health = 100 + (current_wave - 1) * 30  # Increase health by 5 every wave
            if enemy_type == "demon":
                new_enemy = Enemy(_, health=base_health, attack_power=1.5, animations=demon_animations)
            elif enemy_type == "ogre":
                new_enemy = Enemy(_, health=base_health, attack_power=1.5, animations=ogre_animations)
            elif enemy_type == "zombie":
                new_enemy = Enemy(_, health=base_health, attack_power=1.5, animations=zombie_animations)
            new_enemy.position = [enemy_row, enemy_col]
            enemies.append(new_enemy)
        else:
            print("No empty tile found for enemy spawn.")

def game_loop():
    global player, screen, TILE_SIZE, SPRITE_SIZE, mouse_click, current_wave, enemies_per_wave, dungeon_layout
    game_state = "start"
    player_name = "Player"  # Default player name
    clock = pygame.time.Clock()
    mouse_click = False  # Initialize mouse_click

    # Wave system variables
    current_wave = 1
    enemies_per_wave = INITIAL_ENEMIES_PER_WAVE

    # Reload the dungeon layout from the file
    dungeon_layout = load_dungeon_layout(r"\\tct.systems\whs\students\2018\18charalambousja\Documents\Downloads\Dungeon-Crawler-FINAL\dungeongame_layout.txt")
    print(f"Dungeon layout dimensions: {len(dungeon_layout)} rows, {len(dungeon_layout[0])} columns")

    # Initialize the player
    player_row, player_col = find_empty_tile()
    if player_row is not None and player_col is not None:
        player = Player(player_name)
        player.position = [player_row, player_col]  # Set player position to the empty tile
    else:
        print("No empty tile found for player spawn.")

    camera = Camera(len(dungeon_layout[0]) * TILE_SIZE, len(dungeon_layout[0]) * TILE_SIZE)

    # Spawn the first wave
    spawn_wave(enemies_per_wave)

    while True:
        dt = clock.tick(60)  # Get the time passed since the last frame in milliseconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if game_state == "help":
                    if event.key == K_h:
                        game_state = "start"
                elif game_state == "playing":
                    if event.key == K_r:
                        restart_game()
                        game_state = "playing"
                    elif event.key == K_h:
                        game_state = "help"

            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                TILE_SIZE = int(min(WIDTH // COLS, HEIGHT // ROWS) * SCALE_FACTOR)
                SPRITE_SIZE = TILE_SIZE * SPRITE_SCALE_FACTOR
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "start":
                    mouse_pos = event.pos
                    if play_rect.collidepoint(mouse_pos):
                        game_state = "playing"
                        fade_in()
                    elif help_rect.collidepoint(mouse_pos):
                        game_state = "help"
                elif game_state == "game_over":
                    mouse_pos = event.pos
                    if try_again_rect.collidepoint(mouse_pos):
                        restart_game()
                        game_state = "playing"

        if game_state == "start":
            play_rect, help_rect = draw_start_screen()
        elif game_state == "help":
            draw_help_screen()
        elif game_state == "playing":
            screen.fill((0, 0, 0))  # Clear the screen
            update_gameplay(dt)  # Update gameplay
            lava_animation.update(dt)  # Update lava animation
            camera.update(player)
            draw_dungeon(camera)
            draw_health(camera)
            draw_player(camera)
            draw_enemies(camera)  # Draw multiple enemies
            draw_wave_number()  # Draw the wave number

            # Update and draw damage texts
            for damage_text in damage_texts:
                damage_text.update()
                damage_text.draw(screen)
            damage_texts[:] = [dt for dt in damage_texts if dt.alpha > 0]  # Remove faded texts

            # Handle wave system
            if not any(enemy.active for enemy in enemies):  # Check if all enemies are defeated
                current_wave += 1
                enemies_per_wave += ENEMY_INCREMENT_PER_WAVE
                player.increase_attack_power(30)  # Increase player's attack power by 3
                spawn_wave(enemies_per_wave)

            if player.health <= 0:
                game_state = "game_over"
                try_again_rect = display_game_over()

        pygame.display.flip()  # Refresh the display

# Set up pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Dungeon Crawler Game")

# Function to display the help screen
def draw_help():
    """Display the help screen."""
    screen.fill((0, 0, 0))
    help_text = custom_font.render("Help Section", True, (255, 255, 255))
    instructions_text = small_custom_font.render("Press H to return to the game", True, (255, 255, 255))
    screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT // 2 + 40))

# Function to draw the help screen with instructions
def draw_help_screen():
    screen.fill((0, 0, 0))
    help_text = custom_font.render("Help Section", True, (255, 255, 255))
    instructions_text = small_custom_font.render("Press H to return to the start screen", True, (255, 255, 255))
    movement_text = small_custom_font.render("Movement: Arrow keys or WASD", True, (255, 255, 255))
    attack_text = small_custom_font.render("Attack: Left-click to attack", True, (255, 255, 255))
    aim_text = small_custom_font.render("Aim: Defeat the enemies and survive as long as possible", True, (255, 255, 255))
    wave_text = small_custom_font.render("Waves: Enemies get stronger and more numerous each wave", True, (255, 255, 255))
    health_text = small_custom_font.render("Health: Regenerates after 5 seconds without taking damage", True, (255, 255, 255))
    cooldown_text = small_custom_font.render("Cooldown: You can attack again immediately after finishing an attack", True, (255, 255, 255))

    screen.blit(help_text, (screen.get_width() // 2 - help_text.get_width() // 2, screen.get_height() // 2 - 150))
    screen.blit(movement_text, (screen.get_width() // 2 - movement_text.get_width() // 2, screen.get_height() // 2 - 90))
    screen.blit(attack_text, (screen.get_width() // 2 - attack_text.get_width() // 2, screen.get_height() // 2 - 60))
    screen.blit(aim_text, (screen.get_width() // 2 - aim_text.get_width() // 2, screen.get_height() // 2 - 30))
    screen.blit(wave_text, (screen.get_width() // 2 - wave_text.get_width() // 2, screen.get_height() // 2))
    screen.blit(health_text, (screen.get_width() // 2 - health_text.get_width() // 2, screen.get_height() // 2 + 30))
    screen.blit(cooldown_text, (screen.get_width() // 2 - cooldown_text.get_width() // 2, screen.get_height() // 2 + 60))
    screen.blit(instructions_text, (screen.get_width() // 2 - instructions_text.get_width() // 2, screen.get_height() // 2 + 120))

# Define tile size
TILE_WIDTH = 32  # Update with the actual width of a single tile in the sprite sheet
TILE_HEIGHT = 32  # Update with the actual height of a single tile in the sprite sheet

def draw_wave_number():
    """Draw the current wave number at the top center of the screen."""
    wave_text = custom_font.render(f"Wave: {current_wave}", True, (255, 255, 255))
    wave_rect = wave_text.get_rect(center=(screen.get_width() // 2, 30))
    screen.blit(wave_text, wave_rect)

# Start game loop
game_loop()  # Run the main game loop
