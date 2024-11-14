import pygame
import random
import math

# Initialize Pygame and its sound mixer
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = 50  # This will be used for scaling the image
HITBOX_WIDTH, HITBOX_HEIGHT = 20, 30  # Size of the hitbox in front
ENEMY_SIZE = 40
SPEED = 5
ENEMY_SPEED = 2  # Speed at which enemies move towards the player

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
DARK_RED = (139, 0, 0)  # Dark red for the Fatality effect

# Load images
background_image_path = r"C:\Users\ASUS-Pc\Documents\LSPU Files\2nd Year\1st Sem\CMSC 203\PYGAME\PYGAME\image\characters\bg.png"  # Update to your actual path
player_image_path = r"C:\Users\ASUS-Pc\Documents\LSPU Files\2nd Year\1st Sem\CMSC 203\PYGAME\PYGAME\image\yato.png"  # Update to your actual player image path
enemy_image_path = r"C:\Users\ASUS-Pc\Documents\LSPU Files\2nd Year\1st Sem\CMSC 203\PYGAME\PYGAME\fuckibgfucksadassads\wawa.jpg"  # Update this path

# Load and scale background image
background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Scale to fit screen

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Game")

# Load custom font
custom_font_path = r"C:\Users\ASUS-Pc\Documents\LSPU Files\2nd Year\1st Sem\CMSC 203\PYGAME\PYGAME\font\mkmyth.ttf"  # Path to the custom font file
font = pygame.font.Font(custom_font_path, 150)  # Larger font for "Game Over"
score_font = pygame.font.Font(custom_font_path, 36)  # Font for the score
continue_font = pygame.font.Font(custom_font_path, 30)  # Smaller font for the continue prompt

# Load the "Fatality" sound effect
fatality_sound_path = r"C:\Users\ASUS-Pc\Documents\LSPU Files\2nd Year\1st Sem\CMSC 203\PYGAME\PYGAME\sound\fatality.wav"
fatality_sound = pygame.mixer.Sound(fatality_sound_path)

# Adjust sound volume if needed
fatality_sound.set_volume(0.8)  # Volume (0.0 to 1.0)

# Player class
class Player:
    def __init__(self):
        self.image = pygame.image.load(player_image_path)
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE, PLAYER_SIZE))  # Scale to fit
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def move(self, dx, dy):
        self.rect.x += dx * SPEED
        self.rect.y += dy * SPEED
        # Keep the player inside the window
        self.rect.clamp_ip(screen.get_rect())

    def draw(self):
        screen.blit(self.image, self.rect)  # Draw the player image

    def get_hitbox(self):
        # Return the hitbox rectangle (in front of the player)
        return pygame.Rect(self.rect.centerx - HITBOX_WIDTH // 2, self.rect.top - HITBOX_HEIGHT, HITBOX_WIDTH, HITBOX_HEIGHT)

# Enemy class
class Enemy:
    def __init__(self):
        # Load the enemy image (update the path to your actual image file)
        self.image = pygame.image.load(enemy_image_path)
        self.image = pygame.transform.scale(self.image, (ENEMY_SIZE, ENEMY_SIZE))  # Scale to fit

        # Randomly spawn the enemy at one of the screen edges
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            self.rect = pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), 0, ENEMY_SIZE, ENEMY_SIZE)
        elif edge == 'bottom':
            self.rect = pygame.Rect(random.randint(0, WIDTH - ENEMY_SIZE), HEIGHT - ENEMY_SIZE, ENEMY_SIZE, ENEMY_SIZE)
        elif edge == 'left':
            self.rect = pygame.Rect(0, random.randint(0, HEIGHT - ENEMY_SIZE), ENEMY_SIZE, ENEMY_SIZE)
        else:  # right
            self.rect = pygame.Rect(WIDTH - ENEMY_SIZE, random.randint(0, HEIGHT - ENEMY_SIZE), ENEMY_SIZE, ENEMY_SIZE)

    def move_towards(self, player_rect):
        # Move enemy towards the player
        enemy_center = self.rect.center
        player_center = player_rect.center

        # Calculate direction vector from enemy to player
        direction = (player_center[0] - enemy_center[0], player_center[1] - enemy_center[1])
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)

        # Normalize the direction vector and scale by enemy speed
        if distance != 0:  # Avoid division by zero
            direction = (direction[0] / distance, direction[1] / distance)  # Normalize
            self.rect.x += direction[0] * ENEMY_SPEED
            self.rect.y += direction[1] * ENEMY_SPEED

    def draw(self):
        # Draw the enemy image instead of a red rectangle
        screen.blit(self.image, self.rect)
def main():
    clock = pygame.time.Clock()

    # Function to reset the game state
    def reset_game():
        player = Player()
        enemies = []
        spawn_timer = 0
        score = 0
        return player, enemies, spawn_timer, score

    # Initialize game variables
    player, enemies, spawn_timer, score = reset_game()
    game_over = False

    while True:
        if game_over:
            # Handle input for restarting or exiting the game only in game-over state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Reset game state
                        player, enemies, spawn_timer, score = reset_game()
                        game_over = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            # Display "Game Over" screen
            screen.fill(DARK_RED)  # Dark red background
            game_over_text = font.render("FATALITY", True, WHITE)  # Dramatic text
            score_text = score_font.render(f"Final Score: {score}", True, WHITE)  # Display final score
            continue_text = continue_font.render("Press Space to Continue, Press Esc to Exit", True, WHITE)

            # Calculate text rectangles for positioning
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))  # Centered and spaced from the top
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Centered below the title
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))  # Centered below the score
            
            # Pulsing effect for the "FATALITY" text
            pulse_scale = 1 + 0.1 * math.sin(pygame.time.get_ticks() / 250)  # Pulsing effect
            pulsed_text = pygame.transform.scale(game_over_text, (int(game_over_text.get_width() * pulse_scale), 
                                                                   int(game_over_text.get_height() * pulse_scale)))
            pulsed_rect = pulsed_text.get_rect(center=text_rect.center)
            screen.blit(pulsed_text, pulsed_rect)
            screen.blit(score_text, score_rect)
            screen.blit(continue_text, continue_rect)

            pygame.display.flip()

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Movement
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            player.move(dx, dy)

            # Spawn enemies every second
            spawn_timer += clock.get_time()
            if spawn_timer > 1000:  # 1000 milliseconds
                enemies.append(Enemy())
                score += 1  # Increase score for each enemy spawned
                spawn_timer = 0

            # Move enemies towards the player
            for enemy in enemies:
                enemy.move_towards(player.rect)

            # Collision detection
            hitbox = player.get_hitbox()
            for enemy in enemies:
                if hitbox.colliderect(enemy.rect):
                    game_over = True
                    # Play "Fatality" sound effect when game ends
                    fatality_sound.play()

            # Drawing
            screen.blit(background_image, (0, 0))  # Draw the background first
            player.draw()  # Draw the player image
            pygame.draw.rect(screen, BLUE, hitbox)  # Draw hitbox in blue for visibility
            for enemy in enemies:
                enemy.draw()

            # Display the score
            score_text = score_font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))  # Display score at top left

            pygame.display.flip()

        clock.tick(FPS)

if __name__ == "__main__":
    main()
