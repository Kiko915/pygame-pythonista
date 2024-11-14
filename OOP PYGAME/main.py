import pygame
import sys
import random
import pytmx

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 740
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Player settings
PLAYER_SIZE = 50
PLAYER_COLOR = RED
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_speed = 5

# Enemy settings
ENEMY_SIZE = 50
ENEMY_COLOR = BLACK
enemy_speed = 2

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

# Main game loop
def game_loop():
    global current_level, player_pos, enemy_speed

    clock = pygame.time.Clock()
    enemies = []

    # Load current level map
    tmx_data = load_map(levels[current_level])
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    camera = Camera(map_width, map_height)

    # Create enemies
    for _ in range(levels[current_level]["enemy_count"]):
        enemy_pos = [random.randint(0, SCREEN_WIDTH - ENEMY_SIZE), random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE)]
        enemies.append(enemy_pos)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            player_pos[0] += player_speed
        if keys[pygame.K_UP]:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN]:
            player_pos[1] += player_speed

        # Ensure the player does not move off the screen
        player_pos[0] = max(0, min(player_pos[0], SCREEN_WIDTH - PLAYER_SIZE))
        player_pos[1] = max(0, min(player_pos[1], SCREEN_HEIGHT - PLAYER_SIZE))

        screen.fill(WHITE)
        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE)
        camera.update(player_rect)
        draw_map(tmx_data, camera)

        player_surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        player_surface.fill(PLAYER_COLOR)
        screen.blit(player_surface, camera.apply(player_rect))
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

        pygame.display.flip()
        clock.tick(30)

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

# Start screen
def start_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("Press any key to start", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

if __name__ == "__main__":
    start_screen()
    game_loop()