import pygame
import sys
import random
import os
import json
from datetime import datetime
from game_objects import (
    screen,
    screen_width,
    screen_height,
    clock,
    draw_snake,
    draw_food,
    black,
    white,
    green,
)
from rl_agent import rl_main, list_agents, create_agent
from high_score_utils import read_high_scores, update_high_scores

# Initialize Pygame
pygame.init()

# Define additional colors
red = (255, 0, 0)

# High score file
HIGH_SCORES_FILE = "high_scores.json"


def view_high_scores():
    high_scores = read_high_scores()
    screen.fill(black)
    font = pygame.font.Font("freesansbold.ttf", 32)
    title_text = font.render("High Scores", True, white)
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

    if high_scores:
        y_offset = 120
        score_font = pygame.font.Font("freesansbold.ttf", 28)
        for i, entry in enumerate(high_scores, start=1):
            score_text = score_font.render(
                f"{i}. {entry['name']} - {entry['score']}", True, white
            )
            screen.blit(
                score_text, (screen_width // 2 - score_text.get_width() // 2, y_offset)
            )
            y_offset += 40
    else:
        no_scores_text = font.render("No high scores yet!", True, white)
        screen.blit(
            no_scores_text, (screen_width // 2 - no_scores_text.get_width() // 2, 150)
        )

    # Prompt to return to the landing screen
    prompt_text = font.render("Press Enter to Return", True, white)
    screen.blit(
        prompt_text,
        (screen_width // 2 - prompt_text.get_width() // 2, screen_height - 100),
    )

    pygame.display.update()

    # Wait for the user to press Enter to return to the landing screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    choice = landing_screen()
                    if choice == "user":
                        main()
                    elif choice == "agent_options":
                        handle_agent_options()
                    elif choice == "view_scores":
                        view_high_scores()
                    return  # Exit the function after handling the choice
        clock.tick(30)


def game_over(score):
    # Display the "Game Over" message
    screen.fill(black)
    font = pygame.font.Font("freesansbold.ttf", 32)
    game_over_text = font.render("Game Over! Enter Your Name:", True, red)
    screen.blit(
        game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 50)
    )
    pygame.display.update()

    # Capture name input
    input_active = True
    player_name = ""
    input_font = pygame.font.Font("freesansbold.ttf", 32)
    input_box = pygame.Rect(screen_width // 2 - 100, 100, 200, 40)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to finish input
                    input_active = False
                elif (
                    event.key == pygame.K_BACKSPACE
                ):  # Press Backspace to delete a character
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode  # Add character to the name

        # Render input box and player input
        screen.fill(black)
        screen.blit(
            game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 50)
        )
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
    font = pygame.font.Font("freesansbold.ttf", 24)
    for i, entry in enumerate(high_scores, start=1):
        score_text = font.render(
            f"{i}. {entry['name']} - {entry['score']}", True, white
        )
        screen.blit(
            score_text, (screen_width // 2 - score_text.get_width() // 2, y_offset)
        )
        y_offset += 30

    # Display "Press Enter to Play Again or ESC to Quit"
    font = pygame.font.Font("freesansbold.ttf", 28)
    play_again_text = font.render(
        "Press Enter to Play Again or ESC to Quit", True, white
    )
    screen.blit(
        play_again_text,
        (screen_width // 2 - play_again_text.get_width() // 2, y_offset + 20),
    )

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
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                elif event.key == pygame.K_ESCAPE:  # Press ESC to quit
                    pygame.quit()
                    sys.exit()

        # Check if 10 seconds have passed
        if pygame.time.get_ticks() - start_time > 10000:
            pygame.quit()
            sys.exit()

        clock.tick(30)


def landing_screen():
    screen.fill(black)
    font = pygame.font.Font("freesansbold.ttf", 32)
    title_text = font.render("Welcome to Snake Game", True, white)
    option1_text = font.render("Press 1 to Play Yourself", True, white)
    option2_text = font.render("Press 2 for Agent Options", True, white)
    option3_text = font.render("Press 3 to View High Scores", True, white)

    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 80))
    screen.blit(option1_text, (screen_width // 2 - option1_text.get_width() // 2, 180))
    screen.blit(option2_text, (screen_width // 2 - option2_text.get_width() // 2, 230))
    screen.blit(option3_text, (screen_width // 2 - option3_text.get_width() // 2, 280))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # User chooses to play themselves
                    return "user"
                elif event.key == pygame.K_2:  # User chooses agent options
                    return "agent_options"
                elif event.key == pygame.K_3:  # User wants to view high scores
                    return "view_scores"


def agent_options_screen():
    agents = list_agents()
    selected_agent = None

    while True:
        screen.fill(black)
        font = pygame.font.Font("freesansbold.ttf", 28)
        title_text = font.render("Agent Options", True, white)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

        if agents:
            agent_texts = []
            for i, agent in enumerate(agents, start=1):
                agent_text = font.render(f"{i}. {agent}", True, white)
                agent_texts.append(agent_text)
                screen.blit(agent_text, (100, 100 + i * 40))
            create_agent_text = font.render(
                "Press C to Create a New Agent", True, white
            )
            screen.blit(create_agent_text, (100, 100 + (len(agents) + 2) * 40))
        else:
            no_agents_text = font.render("No Agents Found", True, white)
            screen.blit(
                no_agents_text,
                (screen_width // 2 - no_agents_text.get_width() // 2, 150),
            )
            create_agent_text = font.render(
                "Press C to Create a New Agent", True, white
            )
            screen.blit(
                create_agent_text,
                (screen_width // 2 - create_agent_text.get_width() // 2, 200),
            )

        back_text = font.render("Press B to Go Back", True, white)
        screen.blit(
            back_text,
            (screen_width // 2 - back_text.get_width() // 2, screen_height - 50),
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if agents and pygame.K_1 <= event.key <= pygame.K_9:
                    index = event.key - pygame.K_1
                    if index < len(agents):
                        selected_agent = agents[index]
                        mode = mode_selection_screen()
                        if mode:
                            rl_main(selected_agent, mode)
                            return
                elif event.key == pygame.K_c:
                    agent_name = text_input_screen("Enter Agent Name:")
                    if agent_name:
                        create_agent(agent_name)
                        agents = list_agents()  # Refresh the agent list
                elif event.key == pygame.K_b:
                    return  # Go back to the landing screen


def mode_selection_screen():
    while True:
        screen.fill(black)
        font = pygame.font.Font("freesansbold.ttf", 32)
        title_text = font.render("Select Mode", True, white)
        option1_text = font.render("Press L for Learning Mode", True, white)
        option2_text = font.render("Press S for Static Mode", True, white)
        back_text = font.render("Press B to Go Back", True, white)

        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 100))
        screen.blit(
            option1_text, (screen_width // 2 - option1_text.get_width() // 2, 200)
        )
        screen.blit(
            option2_text, (screen_width // 2 - option2_text.get_width() // 2, 250)
        )
        screen.blit(back_text, (screen_width // 2 - back_text.get_width() // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    return "learning"
                elif event.key == pygame.K_s:
                    return "static"
                elif event.key == pygame.K_b:
                    return None  # Go back to agent options


def text_input_screen(prompt):
    input_text = ""
    active = True
    font = pygame.font.Font("freesansbold.ttf", 32)
    input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2, 200, 40)

    while active:
        screen.fill(black)
        prompt_text = font.render(prompt, True, white)
        screen.blit(
            prompt_text,
            (screen_width // 2 - prompt_text.get_width() // 2, screen_height // 2 - 50),
        )

        # Render the current input text
        txt_surface = font.render(input_text, True, white)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, white, input_box, 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                    return input_text
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode


def main():
    global snake_pos, snake_body, snake_direction, change_to, food_pos, food_spawn, score

    # Initialize variables
    snake_pos = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]
    snake_direction = "RIGHT"
    change_to = snake_direction
    food_pos = [
        random.randrange(1, (screen_width // 10)) * 10,
        random.randrange(1, (screen_height // 10)) * 10,
    ]
    food_spawn = True
    score = 0

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

        # Ensure the snake does not move in the opposite direction instantaneously
        if change_to == "UP" and snake_direction != "DOWN":
            snake_direction = "UP"
        if change_to == "DOWN" and snake_direction != "UP":
            snake_direction = "DOWN"
        if change_to == "LEFT" and snake_direction != "RIGHT":
            snake_direction = "LEFT"
        if change_to == "RIGHT" and snake_direction != "LEFT":
            snake_direction = "RIGHT"

        # Move the snake in the specified direction
        if snake_direction == "UP":
            snake_pos[1] -= 10
        if snake_direction == "DOWN":
            snake_pos[1] += 10
        if snake_direction == "LEFT":
            snake_pos[0] -= 10
        if snake_direction == "RIGHT":
            snake_pos[0] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [
                random.randrange(1, (screen_width // 10)) * 10,
                random.randrange(1, (screen_height // 10)) * 10,
            ]
        food_spawn = True

        # Game Over conditions
        if (
            snake_pos[0] < 0
            or snake_pos[0] >= screen_width
            or snake_pos[1] < 0
            or snake_pos[1] >= screen_height
        ):
            game_over(score)
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(score)

        # Display background and elements
        screen.fill(black)
        draw_snake(snake_body)
        draw_food(food_pos)

        # Show score during gameplay
        font = pygame.font.Font("freesansbold.ttf", 24)
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(10)


def handle_agent_options():
    agents = list_agents()
    if agents:
        print("\nExisting Agents:")
        for i, agent in enumerate(agents, start=1):
            print(f"{i}. {agent}")
        print("Press C to create a new agent")

        agent_selected = False
        while not agent_selected:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # Create a new agent
                    agent_name = input("Enter a name for the new agent: ")
                    create_agent(agent_name)
                    print(f"Agent {agent_name} created.")
                    break
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    agent_index = event.key - pygame.K_1
                    if agent_index < len(agents):
                        selected_agent = agents[agent_index]
                        mode = input("Choose mode (learning/static): ").lower()
                        rl_main(selected_agent, mode)
                        agent_selected = True
                        break
    else:
        print("No agents found. Press C to create a new agent.")
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    agent_name = input("Enter a name for the new agent: ")
                    create_agent(agent_name)
                    print(f"Agent {agent_name} created.")
                    break


if __name__ == "__main__":
    while True:
        choice = landing_screen()

        if choice == "user":
            main()  # Start the game for the player
        elif choice == "agent_options":
            agent_options_screen()
        elif choice == "view_scores":
            view_high_scores()
