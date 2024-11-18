import random
import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)

# Snake initial position and properties
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_direction = "RIGHT"
change_to = snake_direction

# Food position and properties
food_pos = [random.randrange(1, (screen_width//10)) * 10, random.randrange(1, (screen_height//10)) * 10]
food_spawn = True

# Score
score = 0

# Clock to control game speed
clock = pygame.time.Clock()

def draw_snake(snake_body):
    for pos in snake_body:
        pygame.draw.rect(screen, green, (pos[0], pos[1], 10, 10))

def draw_food(food_pos):
    pygame.draw.rect(screen, white, (food_pos[0], food_pos[1], 10, 10))

def text_objects(text, font):
    text_surface = font.render(text, True, black)
    return text_surface, text_surface.get_rect()

def message_display(text):
    large_font = pygame.font.Font('freesansbold.ttf', 115)
    text_surf, text_rect = text_objects(text, large_font)
    text_rect.center = ((screen_width/2), (screen_height/2))
    screen.blit(text_surf, text_rect)
    pygame.display.update()
    pygame.time.wait(2000)

def game_over():
    message_display("Game Over")
    pygame.quit()
    sys.exit()

def read_high_score(file_path="high_score.txt"):
    try:
        with open(file_path, "r") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0  # Default to 0 if the file is missing or corrupted

def save_high_score(score, file_path="high_score.txt"):
    with open(file_path, "w") as file:
        file.write(str(score))

def main():
    global snake_pos, snake_body, snake_direction, change_to, food_pos, food_spawn, score

    # Read the highest score at the start of the game
    high_score = read_high_score()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and not (snake_direction == "DOWN"):
                    change_to = "UP"
                elif event.key == pygame.K_DOWN and not (snake_direction == "UP"):
                    change_to = "DOWN"
                elif event.key == pygame.K_LEFT and not (snake_direction == "RIGHT"):
                    change_to = "LEFT"
                elif event.key == pygame.K_RIGHT and not (snake_direction == "LEFT"):
                    change_to = "RIGHT"

        snake_direction = change_to

        # Move the snake
        snake_pos[0] += 10 * (snake_direction == "RIGHT") - 10 * (snake_direction == "LEFT")
        snake_pos[1] += 10 * (snake_direction == "DOWN") - 10 * (snake_direction == "UP")

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, (screen_width//10)) * 10, random.randrange(1, (screen_height//10)) * 10]
        food_spawn = True

        # Game Over conditions
        if snake_pos[0] < 0 or snake_pos[0] >= screen_width or snake_pos[1] < 0 or snake_pos[1] >= screen_height:
            if score > high_score:
                save_high_score(score)
                high_score = score  # Update high_score for display purposes
            game_over()

        for segment in snake_body[1:]:
            if snake_pos[0] == segment[0] and snake_pos[1] == segment[1]:
                if score > high_score:
                    save_high_score(score)
                    high_score = score  # Update high_score for display purposes
                game_over()

        # Clear the screen
        screen.fill(black)

        # Draw the snake
        draw_snake(snake_body)

        # Draw the food
        draw_food(food_pos)

        # Display score and high score
        score_font = pygame.font.Font('freesansbold.ttf', 32)
        score_surface = score_font.render(f"Score : {score}  High Score : {high_score}", True, white)
        score_rect = score_surface.get_rect()
        screen.blit(score_surface, score_rect)

        pygame.display.update()

        clock.tick(10)



if __name__ == "__main__":
    main()