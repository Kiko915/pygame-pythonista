import pygame
import sys
import random
import pytmx
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 740
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CMSC 203 Top Down Pygame")

# Colors
WHITE = (158, 223, 156)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player settings
PLAYER_SIZE = 50
PLAYER_COLOR = RED
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5  # Increased player speed

# Enemy settings
ENEMY_SIZE = 50
ENEMY_COLOR = BLACK
enemy_speed = 2  # Increased enemy speed
MIN_DISTANCE_FROM_PLAYER = 200  # Minimum distance from player

# Levels
levels = [
    {"map": "level1.tmx", "enemy_count": 5},
    {"map": "level2.tmx", "enemy_count": 10},
    {"map": "level3.tmx", "enemy_count": 15}
]
current_level = 0

# Camera class
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.centerx + int(SCREEN_WIDTH / 2)
        y = -target.centery + int(SCREEN_HEIGHT / 2)

        x = min(0, x)  # Left
        y = min(0, y)  # Top
        x = max(-(self.width - SCREEN_WIDTH), x)  # Right
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Bottom

        self.camera = pygame.Rect(x, y, self.width, self.height)

# Load map
def load_map(level):
    try:
        tmx_data = pytmx.load_pygame(level["map"], pixelalpha=True)
    except Exception as e:
        print(f"Error loading map: {e}")
        pygame.quit()
        sys.exit()
    return tmx_data

# Draw map
def draw_map(tmx_data, camera):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, camera.apply(pygame.Rect(x * tmx_data.tilewidth, y * tmx_data.tileheight, tmx_data.tilewidth, tmx_data.tileheight)))

# Update player position without boundary collision
def update_player_position(keys, player_pos, player_speed):
    if keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += player_speed

def game_loop():
    global current_level, player_pos, enemy_speed, score, start_time, last_direction

    clock = pygame.time.Clock()
    enemies = []

    # Initialize score and start time
    score = 0
    start_time = pygame.time.get_ticks()  # Get the starting time for the score increment

    # Load current level map
    tmx_data = load_map(levels[current_level])
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    camera = Camera(map_width, map_height)

    # Load player animations
    animations = load_player_animations()
    last_direction = "down"  # Default direction

    # Create enemies
    for _ in range(levels[current_level]["enemy_count"]):
        while True:
            enemy_pos = [random.randint(0, SCREEN_WIDTH - ENEMY_SIZE), random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE)]
            distance = math.sqrt((enemy_pos[0] - player_pos[0]) ** 2 + (enemy_pos[1] - player_pos[1]) ** 2)
            if distance >= MIN_DISTANCE_FROM_PLAYER:
                enemies.append(enemy_pos)
                break

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE)
        update_player_position(keys, player_pos, player_speed)

        # Increment score every second
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if current_time - start_time >= 1000:  # Check if one second has passed
            score += 1  # Increment score by 1
            start_time = current_time  # Reset the start time

        screen.fill(WHITE)
        camera.update(player_rect)
        draw_map(tmx_data, camera)

        # Update and draw player animation
        player_image = update_player_animation(keys, animations)
        screen.blit(player_image, camera.apply(player_rect))

        enemy_surface = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        enemy_surface.fill(ENEMY_COLOR)
        for enemy_pos in enemies:
            enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], ENEMY_SIZE, ENEMY_SIZE)
            screen.blit(enemy_surface, camera.apply(enemy_rect))
            if player_pos[0] < enemy_pos[0]:
                enemy_pos[0] -= enemy_speed
            if player_pos[0] > enemy_pos[0]:
                enemy_pos[0] += enemy_speed
            if player_pos[1] < enemy_pos[1]:
                enemy_pos[1] -= enemy_speed
            if player_pos[1] > enemy_pos[1]:
                enemy_pos[1] += enemy_speed

            # Check for collision with player
            if player_rect.colliderect(enemy_rect):
                print("Player died!")
                pygame.quit()
                sys.exit()

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

        # Check for level completion
        if len(enemies) == 0:
            current_level += 1
            if current_level >= len(levels):
                print("You win!")
                pygame.quit()
                sys.exit()
            else:
                enemy_speed += 1
                game_loop()

# Helper function to load frames from a spritesheet
def load_frames_from_spritesheet(filename, rows, cols, scale_factor=2):
    sheet = pygame.image.load(filename).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // cols
    frame_height = sheet_height // rows
    frames = []
    for row in range(rows):
        for col in range(cols):
            frame = sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
            scaled_frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
            frames.append(scaled_frame)
    return frames

def load_player_animations():
    animations = {
        "left_idle": load_frames_from_spritesheet("player/leftidle.png", 1, 10),
        "left_run": load_frames_from_spritesheet("player/leftrun.png", 1, 10),
        "north_idle": load_frames_from_spritesheet("player/northidle.png", 1, 10),
        "north_run": load_frames_from_spritesheet("player/northrun.png", 1, 10),
        "right_idle": load_frames_from_spritesheet("player/rightidle.png", 1, 10),
        "right_run": load_frames_from_spritesheet("player/rightrun.png", 1, 10),
        "south_idle": load_frames_from_spritesheet("player/southidle.png", 1, 10),
        "south_run": load_frames_from_spritesheet("player/southrun.png", 1, 10),
    }
    return animations

# Update player animation based on movement
def update_player_animation(keys, animations):
    global last_direction
    if keys[pygame.K_LEFT]:
        last_direction = "left"
        return animations["left_run"][0]
    elif keys[pygame.K_RIGHT]:
        last_direction = "right"
        return animations["right_run"][0]
    elif keys[pygame.K_UP]:
        last_direction = "up"
        return animations["north_run"][0]
    elif keys[pygame.K_DOWN]:
        last_direction = "down"
        return animations["south_run"][0]
    else:
        if last_direction == "left":
            return animations["left_idle"][0]
        elif last_direction == "right":
            return animations["right_idle"][0]
        elif last_direction == "up":
            return animations["north_idle"][0]
        elif last_direction == "down":
            return animations["south_idle"][0]

def show_start_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("Select Level", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
    screen.blit(text, text_rect)

    level1_text = font.render("1. Level 1", True, BLACK)
    level1_rect = level1_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(level1_text, level1_rect)

    level2_text = font.render("2. Level 2", True, BLACK)
    level2_rect = level2_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
    screen.blit(level2_text, level2_rect)

    level3_text = font.render("3. Level 3", True, BLACK)
    level3_rect = level3_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
    screen.blit(level3_text, level3_rect)

    press_any_key_text = font.render("Press any key to start", True, BLACK)
    press_any_key_rect = press_any_key_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))
    screen.blit(press_any_key_text, press_any_key_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    return 0
                elif event.key == pygame.K_2:
                    return 1
                elif event.key == pygame.K_3:
                    return 2
                else:
                    waiting = False  # Exit the loop on any key press

    return 0  # Default to level 1 if no specific level is selected


# Start game
current_level = show_start_menu()
game_loop()
