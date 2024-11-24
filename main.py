import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game Settings
FPS = 60
PLAYER_SIZE = 40
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
CLONE_DELAY = 300  # Frames before the clone spawns
PLAYER_JUMP_HEIGHT = -15
PLATFORM_SPACING_MIN = 100
PLATFORM_SPACING_MAX = 120

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("You Are Your Own Enemy")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 24)

# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.vel_y = 0
        self.on_ground = False
        self.path = []  # Path for the clone to follow (frame by frame)
        self.last_position = (self.rect.x, self.rect.y)

    def update(self, keys, platforms):
        dx = 0
        self.vel_y += 0.8  # Gravity
        if self.vel_y > 10:
            self.vel_y = 10

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            dx = -5
        if keys[pygame.K_RIGHT]:
            dx = 5

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = PLAYER_JUMP_HEIGHT
            self.on_ground = False

        # Update position
        self.rect.x += dx
        self.rect.y += self.vel_y

        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Record path for the clone (frame by frame)
        if self.rect.x != self.last_position[0] or self.rect.y != self.last_position[1]:
            self.path.append((self.rect.x, self.rect.y, self.vel_y))  # Include velocity to track jumps
            self.last_position = (self.rect.x, self.rect.y)

class Clone(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(RED)
        # Start at the player's last position but offset slightly
        self.rect = self.image.get_rect(topleft=(path[0][0] + 50, path[0][1] - 30))  # Slight offset
        self.vel_y = path[0][2]  # Start with the same velocity as the player
        self.path = path
        self.index = 0

    def update(self, platforms):
        # Follow the path frame by frame
        if self.index < len(self.path):
            self.rect.topleft = (self.path[self.index][0], self.path[self.index][1])
            self.vel_y = self.path[self.index][2]  # Set velocity to match the player's at this point
            self.index += 1
        # Apply gravity for the clone (same as player)
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.y += self.vel_y

        # Platform collision for the clone
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.Surface((width, PLATFORM_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))

def generate_platforms():
    platforms = []
    platforms.append(Platform(0, SCREEN_HEIGHT - 10, SCREEN_WIDTH))  # Base floor
    y = SCREEN_HEIGHT - 100
    last_x = SCREEN_WIDTH // 2
    while y > -2000:
        x = random.randint(max(0, last_x - 200), min(SCREEN_WIDTH - PLATFORM_WIDTH, last_x + 200))
        platforms.append(Platform(x, y, PLATFORM_WIDTH))
        last_x = x
        y -= random.randint(PLATFORM_SPACING_MIN, PLATFORM_SPACING_MAX)
    return platforms

# Game Initialization
player = Player()
platforms = generate_platforms()
platform_group = pygame.sprite.Group(platforms)
clone = None
clone_group = pygame.sprite.Group()
player_group = pygame.sprite.Group(player)

# Game Loop
camera_y = 0
frame_count = 0
running = True

while running:
    keys = pygame.key.get_pressed()
    screen.fill(WHITE)

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player and platforms
    player_group.update(keys, platform_group)

    # Spawn clone after delay
    if frame_count == CLONE_DELAY and clone is None:
        clone = Clone(player.path[:])  # Clone follows player's recorded path
        clone_group.add(clone)

    # Update clone path continuously
    if clone:
        clone_group.update(platform_group)

    # Move platforms and clone with the camera
    offset = SCREEN_HEIGHT // 3 - player.rect.top
    if abs(offset) > 10:
        camera_y += offset
        player.rect.y += offset
        for platform in platform_group:
            platform.rect.y += offset
        for clone in clone_group:
            clone.rect.y += offset

    # Draw platforms, player, and clone
    platform_group.draw(screen)
    player_group.draw(screen)
    clone_group.draw(screen)

    # Collision with the clone
    if pygame.sprite.spritecollide(player, clone_group, False):
        running = False  # End game on collision

    # Display text
    score = abs(camera_y // 10)
    score_text = font.render(f"Score: {score}", True, BLACK)
    message = "I'm the organizer and only got 2 hours! :("
    message_text = font.render(message, True, RED)
    screen.blit(score_text, (10, 10))
    if score < 200:
        screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 50))

    pygame.display.flip()
    clock.tick(FPS)
    frame_count += 1

# End Screen
screen.fill(WHITE)
end_text = font.render("You are your own enemy!", True, BLACK)
score_text = font.render(f"Final Score: {score}", True, BLACK)
screen.blit(end_text, (SCREEN_WIDTH // 2 - end_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
pygame.display.flip()
pygame.time.wait(3000)

pygame.quit()
sys.exit()
