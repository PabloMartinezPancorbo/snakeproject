import pygame
import sys
import random
import os
import json
from datetime import datetime
import numpy as np
import pickle  # Import pickle for serialization

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
    red,  # Ensure red is imported
)
from high_score_utils import read_high_scores, update_high_scores

AGENT_FOLDER = "agents"
os.makedirs(AGENT_FOLDER, exist_ok=True)

# Initialize Q-table
Q_table = {}
learning_rate = 0.1
discount_factor = 0.9
exploration_rate = 1.0
exploration_decay = 0.995
min_exploration_rate = 0.01


def list_agents():
    agents = [
        f
        for f in os.listdir(AGENT_FOLDER)
        if f.endswith(".json") and not f.endswith("_q_table.pkl")
    ]
    return [agent.replace(".json", "") for agent in agents]


def create_agent(
    agent_name, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0
):
    agent_data = {
        "name": agent_name,
        "learning_rate": learning_rate,
        "discount_factor": discount_factor,
        "exploration_rate": exploration_rate,
        "learning_cycles": 0,
        "history": [],
    }
    with open(os.path.join(AGENT_FOLDER, f"{agent_name}.json"), "w") as f:
        json.dump(agent_data, f)


def load_agent(agent_name):
    try:
        with open(os.path.join(AGENT_FOLDER, f"{agent_name}.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Agent {agent_name} not found.")
        return None


def save_agent(agent_data):
    # Removed the increment of learning_cycles from here
    with open(os.path.join(AGENT_FOLDER, f"{agent_data['name']}.json"), "w") as f:
        json.dump(agent_data, f)


def save_q_table(agent_name):
    try:
        with open(os.path.join(AGENT_FOLDER, f"{agent_name}_q_table.pkl"), "wb") as f:
            pickle.dump(Q_table, f)
    except Exception as e:
        print(f"Error saving Q-table: {e}")


def load_q_table(agent_name):
    global Q_table
    try:
        with open(os.path.join(AGENT_FOLDER, f"{agent_name}_q_table.pkl"), "rb") as f:
            Q_table = pickle.load(f)
    except FileNotFoundError:
        Q_table = {}
    except Exception as e:
        print(f"Error loading Q-table: {e}")
        Q_table = {}


def get_state(snake_pos, snake_body, food_pos):
    return (snake_pos[0], snake_pos[1], food_pos[0], food_pos[1])


def choose_action(state, valid_actions, agent_data, mode):
    exploration_rate = agent_data["exploration_rate"] if mode == "learning" else 0.1
    if random.uniform(0, 1) < exploration_rate:
        return random.choice(valid_actions)
    else:
        return max(
            Q_table.get(state, {}),
            key=Q_table.get(state, {}).get,
            default=random.choice(valid_actions),
        )


def update_q_table(state, action, reward, next_state):
    current_q = Q_table.get(state, {}).get(action, 0)
    max_future_q = max(Q_table.get(next_state, {}).values(), default=0)
    new_q = current_q + learning_rate * (
        reward + discount_factor * max_future_q - current_q
    )
    if state not in Q_table:
        Q_table[state] = {}
    Q_table[state][action] = new_q


def agent_update_prompt():
    while True:
        screen.fill(black)
        font = pygame.font.Font("freesansbold.ttf", 28)
        prompt_text = font.render("Update Agent with Learnings?", True, white)
        option_yes = font.render("Press Y for Yes", True, white)
        option_no = font.render("Press N for No", True, white)

        screen.blit(
            prompt_text, (screen_width // 2 - prompt_text.get_width() // 2, 150)
        )
        screen.blit(option_yes, (screen_width // 2 - option_yes.get_width() // 2, 200))
        screen.blit(option_no, (screen_width // 2 - option_no.get_width() // 2, 250))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return "yes"
                elif event.key == pygame.K_n:
                    return "no"
        clock.tick(30)


def agent_game_over(score, agent_data, session_cycles):
    # Display the "Game Over" message
    screen.fill(black)
    font = pygame.font.Font("freesansbold.ttf", 32)
    game_over_text = font.render("Game Over!", True, red)
    score_text = font.render(f"Agent's Score: {score}", True, white)
    session_cycles_text = font.render(
        f"Learning Cycles This Session: {session_cycles}", True, white
    )
    total_cycles_text = font.render(
        f"Total Learning Cycles: {agent_data['learning_cycles']}", True, white
    )
    prompt_text = font.render(
        "Press Enter to Play Again or ESC to Main Menu", True, white
    )

    screen.blit(
        game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 50)
    )
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 120))
    screen.blit(
        session_cycles_text,
        (screen_width // 2 - session_cycles_text.get_width() // 2, 170),
    )
    screen.blit(
        total_cycles_text, (screen_width // 2 - total_cycles_text.get_width() // 2, 220)
    )
    screen.blit(prompt_text, (screen_width // 2 - prompt_text.get_width() // 2, 300))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "play_again"
                elif event.key == pygame.K_ESCAPE:
                    return "main_menu"
        clock.tick(30)


def rl_main(agent_name, mode="learning"):
    agent_data = load_agent(agent_name)
    if not agent_data:
        return
    load_q_table(agent_name)

    # Initialize variables for the session
    session_cycles = 0
    running = True

    while running:
        # Initialize variables for the game
        snake_pos = [100, 50]
        snake_body = [[100, 50], [90, 50], [80, 50]]
        snake_direction = "RIGHT"
        food_pos = [
            random.randrange(1, (screen_width // 10)) * 10,
            random.randrange(1, (screen_height // 10)) * 10,
        ]
        food_spawn = True
        score = 0

        game_over = False

        while not game_over:
            state = get_state(snake_pos, snake_body, food_pos)
            valid_actions = ["UP", "DOWN", "LEFT", "RIGHT"]

            # Prevent the snake from reversing direction
            if snake_direction == "UP":
                valid_actions.remove("DOWN")
            elif snake_direction == "DOWN":
                valid_actions.remove("UP")
            elif snake_direction == "LEFT":
                valid_actions.remove("RIGHT")
            elif snake_direction == "RIGHT":
                valid_actions.remove("LEFT")

            action = choose_action(state, valid_actions, agent_data, mode)
            snake_direction = action

            # Move the snake
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
                reward = 10
                food_spawn = False
            else:
                snake_body.pop()
                reward = -0.1

            if not food_spawn:
                food_pos = [
                    random.randrange(1, (screen_width // 10)) * 10,
                    random.randrange(1, (screen_height // 10)) * 10,
                ]
            food_spawn = True

            # Check for game over conditions
            if (
                snake_pos[0] < 0
                or snake_pos[0] >= screen_width
                or snake_pos[1] < 0
                or snake_pos[1] >= screen_height
                or snake_pos in snake_body[1:]
            ):
                reward = -100
                game_over = True
                break

            next_state = get_state(snake_pos, snake_body, food_pos)
            update_q_table(state, action, reward, next_state)

            agent_data["history"].append((state, action, reward, next_state))

            # Decay exploration rate in learning mode
            if mode == "learning":
                agent_data["exploration_rate"] = max(
                    min_exploration_rate,
                    agent_data["exploration_rate"] * exploration_decay,
                )

            # Draw elements on the screen
            screen.fill(black)
            draw_snake(snake_body)
            draw_food(food_pos)

            # Show score during gameplay
            font = pygame.font.Font("freesansbold.ttf", 24)
            score_text = font.render(f"Score: {score}", True, white)
            screen.blit(score_text, (10, 10))

            pygame.display.update()
            clock.tick(10)

        # After game over
        session_cycles += 1
        save_q_table(agent_name)
        if mode == "learning":
            agent_data["learning_cycles"] += 1  # Increment learning cycles here
            save_agent(agent_data)
        elif mode == "static":
            update_prompt = agent_update_prompt()
            if update_prompt == "yes":
                save_agent(agent_data)

        # Create leaderboard entry
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        leaderboard_name = (
            f"{agent_data['name']}-{agent_data['learning_cycles']}-{timestamp}"
        )

        # Update high scores
        update_high_scores(score, leaderboard_name)

        # Display game over screen
        choice = agent_game_over(score, agent_data, session_cycles)
        if choice == "play_again":
            continue  # Start a new game in the same session
        elif choice == "main_menu":
            running = False  # Exit the loop to return to main menu

    # Return to main menu
    return
