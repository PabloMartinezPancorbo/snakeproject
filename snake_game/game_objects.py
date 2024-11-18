import pygame
import random

# Initialize Pygame (only if not already initialized elsewhere)
pygame.init()

# Set up display variables
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)


# Clock
clock = pygame.time.Clock()

# Snake variables
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_direction = "RIGHT"
change_to = snake_direction

# Food variables
food_pos = [
    random.randrange(1, (screen_width // 10)) * 10,
    random.randrange(1, (screen_height // 10)) * 10,
]
food_spawn = True

# Score
score = 0


def draw_snake(snake_body):
    for pos in snake_body:
        pygame.draw.rect(screen, green, pygame.Rect(pos[0], pos[1], 10, 10))


def draw_food(food_pos):
    pygame.draw.rect(screen, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
