import random
import pygame
import sys
import json
import os

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
def landing_screen():
    screen.fill(black)
    font = pygame.font.Font('freesansbold.ttf', 32)
    title_text = font.render("Welcome to Snake Game", True, white)
    option1_text = font.render("Press 1 to Play Yourself", True, white)
    option2_text = font.render("Press 2 for RL Agent to Play", True, white)
    
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))
    screen.blit(option1_text, (screen_width // 2 - option1_text.get_width() // 2, 200))
    screen.blit(option2_text, (screen_width // 2 - option2_text.get_width() // 2, 300))
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # User chooses to play themselves
                    return 'user'
                elif event.key == pygame.K_2:  # User chooses the RL agent
                    return 'agent'

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

def read_high_scores(file_path="high_scores.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return an empty list if the file doesn't exist or is corrupted

def save_high_scores(scores, file_path="high_scores.json"):
    with open(file_path, "w") as file:
        json.dump(scores, file, indent=4)

def update_high_scores(new_score, player_name, file_path="high_scores.json"):
    scores = read_high_scores(file_path)
    scores.append({"name": player_name, "score": new_score})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:5]  # Keep top 5 scores
    save_high_scores(scores, file_path)
    return scores
def main():
    global snake_pos, snake_body, snake_direction, change_to, food_pos, food_spawn, score

    # Read the highest score at the start of the game (top 5)
    high_scores = read_high_scores()
    high_score = high_scores[0]["score"] if high_scores else 0  # Get the highest score from the list

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
            game_over()

        for segment in snake_body[1:]:
            if snake_pos[0] == segment[0] and snake_pos[1] == segment[1]:
                game_over()

        # Clear the screen
        screen.fill(black)

        # Draw the snake
        draw_snake(snake_body)

        # Draw the food
        draw_food(food_pos)

        # Display current score and highest score
        score_font = pygame.font.Font('freesansbold.ttf', 32)
        score_surface = score_font.render(f"Score : {score}  High Score : {high_score}", True, white)
        score_rect = score_surface.get_rect()
        screen.blit(score_surface, score_rect)

        pygame.display.update()
        clock.tick(10)

def game_over():
    global score

    # Display the "Game Over" message and input prompt for name
    screen.fill(black)
    font = pygame.font.Font('freesansbold.ttf', 32)
    game_over_text = font.render("Game Over! Enter Your Name:", True, red)
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 50))
    pygame.display.update()

    # Capture name input
    input_active = True
    player_name = ""
    input_font = pygame.font.Font('freesansbold.ttf', 32)
    input_box = pygame.Rect(screen_width // 2 - 100, 100, 200, 40)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to finish input
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  # Press Backspace to delete a character
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode  # Add character to the name

        # Render input box and player input
        screen.fill(black)
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 50))
        text_surface = input_font.render(player_name, True, white)
        width = max(200, text_surface.get_width() + 10)
        input_box.w = width
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, white, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

    # Update high scores and display them on the screen
    if player_name:
        update_high_scores(score, player_name)

    high_scores = read_high_scores()
    y_offset = 160
    for i, entry in enumerate(high_scores, start=1):
        score_text = font.render(f"{i}. {entry['name']} - {entry['score']}", True, white)
        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, y_offset))
        y_offset += 40

    # Display "Press Enter to Play Again or ESC to Quit"
    play_again_text = font.render("Press Enter to Play Again or ESC to Quit", True, white)
    screen.blit(play_again_text, (screen_width // 2 - play_again_text.get_width() // 2, y_offset + 40))

    pygame.display.update()

    # Wait for input to continue or quit, or timeout after 10 seconds
    start_time = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to play again
                    # Restart the game by re-executing the script
                    os.execv(sys.executable, ['python'] + sys.argv)
                elif event.key == pygame.K_ESCAPE:  # Press ESC to quit
                    pygame.quit()
                    sys.exit()

        # Check if 10 seconds have passed
        if pygame.time.get_ticks() - start_time > 10000:
            pygame.quit()
            sys.exit()

        clock.tick(30)


if __name__ == "__main__":
    choice = landing_screen()
    
    if choice == 'user':
        main()  # Start the game with user control
    elif choice == 'agent':
        # Import and start the RL agent's gameplay logic
        from rl_agent import rl_main  # Ensure rl_main.py exists in the rl_agent folder
        rl_main()  # Call the RL agent's main function