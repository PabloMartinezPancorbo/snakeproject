# rl_agent.py

import pygame
import sys
import random
import os
import json
import pickle
import math
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
    red,
)
from high_score_utils import read_high_scores, update_high_scores

# Agent folder setup
AGENT_FOLDER = "agents"
os.makedirs(AGENT_FOLDER, exist_ok=True)

# Initialize Q-table
Q_table = {}

# Agent-related functions


def create_agent(
    agent_name,
    learning_rate,
    discount_factor,
    exploration_rate,
    exploration_decay,
    min_exploration_rate,
):
    agent_data = {
        "name": agent_name,
        "learning_rate": learning_rate,
        "discount_factor": discount_factor,
        "exploration_rate": exploration_rate,
        "exploration_decay": exploration_decay,
        "min_exploration_rate": min_exploration_rate,
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
    with open(os.path.join(AGENT_FOLDER, f"{agent_data['name']}.json"), "w") as f:
        json.dump(agent_data, f)


def list_agents():
    agents = [
        f
        for f in os.listdir(AGENT_FOLDER)
        if f.endswith(".json") and not f.endswith("_q_table.pkl")
    ]
    return [agent.replace(".json", "") for agent in agents]


# Q-table functions


def save_q_table(agent_name):
    global Q_table
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


# Utility functions


def calculate_distance_to_food(snake_pos, food_pos):
    """Calculate the Euclidean distance from the snake's head to the food."""
    distance = math.sqrt(
        (snake_pos[0] - food_pos[0]) ** 2 + (snake_pos[1] - food_pos[1]) ** 2
    )
    return distance


def calculate_distance_to_wall(snake_pos, screen_width, screen_height):
    """Calculate the shortest distance from the snake's head to the nearest wall."""
    distance_left = snake_pos[0]
    distance_right = screen_width - snake_pos[0]
    distance_top = snake_pos[1]
    distance_bottom = screen_height - snake_pos[1]

    # Return the shortest distance to any wall
    return min(distance_left, distance_right, distance_top, distance_bottom)


def is_collision(point, snake_body):
    # Check if the point is hitting the wall
    if (
        point[0] < 0
        or point[0] >= screen_width
        or point[1] < 0
        or point[1] >= screen_height
    ):
        return True
    # Check if the point is hitting itself
    if point in snake_body[1:]:
        return True
    return False


def is_danger_straight(snake_pos, snake_body, snake_direction):
    x, y = snake_pos
    if snake_direction == "UP":
        x, y = x, y - 10
    elif snake_direction == "DOWN":
        x, y = x, y + 10
    elif snake_direction == "LEFT":
        x, y = x - 10, y
    elif snake_direction == "RIGHT":
        x, y = x + 10, y
    return is_collision([x, y], snake_body)


def is_danger_left(snake_pos, snake_body, snake_direction):
    x, y = snake_pos
    if snake_direction == "UP":
        x, y = x - 10, y
    elif snake_direction == "DOWN":
        x, y = x + 10, y
    elif snake_direction == "LEFT":
        x, y = x, y + 10
    elif snake_direction == "RIGHT":
        x, y = x, y - 10
    return is_collision([x, y], snake_body)


def is_danger_right(snake_pos, snake_body, snake_direction):
    x, y = snake_pos
    if snake_direction == "UP":
        x, y = x + 10, y
    elif snake_direction == "DOWN":
        x, y = x - 10, y
    elif snake_direction == "LEFT":
        x, y = x, y - 10
    elif snake_direction == "RIGHT":
        x, y = x, y + 10
    return is_collision([x, y], snake_body)


def get_state(snake_pos, snake_body, food_pos, snake_direction):
    # Danger indicators
    danger_straight = is_danger_straight(snake_pos, snake_body, snake_direction)
    danger_left = is_danger_left(snake_pos, snake_body, snake_direction)
    danger_right = is_danger_right(snake_pos, snake_body, snake_direction)

    # Food direction
    food_left = food_pos[0] < snake_pos[0]
    food_right = food_pos[0] > snake_pos[0]
    food_up = food_pos[1] < snake_pos[1]
    food_down = food_pos[1] > snake_pos[1]

    # Snake movement direction
    moving_left = snake_direction == "LEFT"
    moving_right = snake_direction == "RIGHT"
    moving_up = snake_direction == "UP"
    moving_down = snake_direction == "DOWN"

    state = (
        danger_straight,
        danger_left,
        danger_right,
        moving_left,
        moving_right,
        moving_up,
        moving_down,
        food_left,
        food_right,
        food_up,
        food_down,
    )
    return state


def choose_action(state, valid_actions, agent_data, mode):
    exploration_rate = agent_data["exploration_rate"] if mode == "learning" else 0.1
    if random.uniform(0, 1) < exploration_rate:
        return random.choice(valid_actions)
    else:
        state_actions = Q_table.get(state, {})
        if state_actions:
            return max(state_actions, key=state_actions.get)
        else:
            return random.choice(valid_actions)


def update_q_table(
    state,
    action,
    reward,
    next_state,
    agent_data,
    snake_pos,
    food_pos,
    next_snake_pos,
    next_food_pos,
):
    learning_rate = agent_data["learning_rate"]
    discount_factor = agent_data["discount_factor"]

    current_q = Q_table.get(state, {}).get(action, 0)
    max_future_q = max(Q_table.get(next_state, {}).values(), default=0)

    # Calculate the Euclidean distance to food
    current_distance = calculate_distance_to_food(snake_pos, food_pos)
    next_distance = calculate_distance_to_food(next_snake_pos, next_food_pos)
    distance_change = current_distance - next_distance

    # Reward for moving closer to the food
    if distance_change > 0:
        reward += 1  # Adjust this value as needed
    elif distance_change < 0:
        reward -= 1  # Penalize for moving away from food

    # Penalize collision
    if reward == -100:
        reward -= 100  # Additional penalty for dying

    # Small reward for survival
    reward += 0.1

    # Update Q-value using the Q-learning formula
    new_q = current_q + learning_rate * (
        reward + discount_factor * max_future_q - current_q
    )

    if state not in Q_table:
        Q_table[state] = {}
    Q_table[state][action] = new_q


def detect_loop(history, current_state, loop_threshold=5):
    # Check if the current state has appeared in the last `loop_threshold` moves
    recent_states = [
        h[0] for h in history[-loop_threshold:]
    ]  # Extract states from history
    return recent_states.count(current_state) > 1


def rl_main(agent_name, mode="learning"):
    agent_data = load_agent(agent_name)
    if not agent_data:
        return
    load_q_table(agent_name)

    # Load agent-specific parameters
    learning_rate = agent_data["learning_rate"]
    discount_factor = agent_data["discount_factor"]
    exploration_rate = agent_data["exploration_rate"]
    exploration_decay = agent_data["exploration_decay"]
    min_exploration_rate = agent_data["min_exploration_rate"]

    # Ask for the number of games in the Pygame window
    num_games = 1
    if mode == "learning":
        num_games = display_text_input("Enter the number of games to run:", 1)

    learning_speed = 100  # Speed for accelerated training

    for game_num in range(1, num_games + 1):
        session_cycles = 0
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
        agent_data["history"] = []

        while not game_over:
            state = get_state(snake_pos, snake_body, food_pos, snake_direction)
            valid_actions = ["UP", "DOWN", "LEFT", "RIGHT"]

            # Prevent reversing direction
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

            # Before moving the snake
            snake_pos_before_move = snake_pos.copy()

            # Move the snake
            if snake_direction == "UP":
                snake_pos[1] -= 10
            elif snake_direction == "DOWN":
                snake_pos[1] += 10
            elif snake_direction == "LEFT":
                snake_pos[0] -= 10
            elif snake_direction == "RIGHT":
                snake_pos[0] += 10

            # After moving the snake
            snake_pos_after_move = snake_pos.copy()

            # Update the snake body
            snake_body.insert(0, list(snake_pos_after_move))

            # Check for food consumption
            if (
                snake_pos_after_move[0] == food_pos[0]
                and snake_pos_after_move[1] == food_pos[1]
            ):
                score += 1
                reward = 10  # Reward for eating food
                food_spawn = False
            else:
                snake_body.pop()
                reward = -0.1  # Penalty for movement without food

            if not food_spawn:
                food_pos = [
                    random.randrange(1, (screen_width // 10)) * 10,
                    random.randrange(1, (screen_height // 10)) * 10,
                ]
            food_spawn = True

            if detect_loop(agent_data["history"], state):
                reward -= 5  # Penalize the agent for looping

            # Check for game over conditions
            if is_collision(snake_pos_after_move, snake_body):
                reward = -100  # Penalty for dying
                game_over = True

            # Calculate next_state with updated position and direction
            next_state = get_state(
                snake_pos_after_move, snake_body, food_pos, snake_direction
            )

            # Update Q-table
            update_q_table(
                state,
                action,
                reward,
                next_state,
                agent_data,
                snake_pos_before_move,
                food_pos,
                snake_pos_after_move,
                food_pos,
            )

            agent_data["history"].append((state, action, reward, next_state))

            if mode == "learning":
                exploration_rate = agent_data["exploration_rate"]
                exploration_rate = max(
                    agent_data["min_exploration_rate"],
                    exploration_rate * agent_data["exploration_decay"],
                )
                agent_data["exploration_rate"] = exploration_rate

            # Render the game in learning mode at accelerated speed
            screen.fill(black)
            draw_snake(snake_body)
            draw_food(food_pos)
            font = pygame.font.Font("freesansbold.ttf", 24)
            score_text = font.render(f"Score: {score}", True, white)
            session_text = font.render(
                f"Session: {game_num}/{num_games}", True, white
            )  # Display session number

            # Display score and session number
            screen.blit(score_text, (10, 10))
            screen.blit(session_text, (10, 40))

            pygame.display.update()

            clock.tick(learning_speed if mode == "learning" else 10)

        # End of the game logic
        session_cycles += 1
        if mode == "learning":
            agent_data["learning_cycles"] += 1
            save_agent(agent_data)

        save_q_table(agent_name)
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        leaderboard_name = (
            f"{agent_data['name']}-{agent_data['learning_cycles']}-{timestamp}"
        )
        update_high_scores(score, leaderboard_name)

    print("Learning session completed!")


def display_text_input(prompt, default_value):
    """Displays an input prompt on the screen and returns user input or a default value."""
    input_text = ""
    active = True
    font = pygame.font.Font("freesansbold.ttf", 24)
    input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2, 200, 40)

    while active:
        screen.fill(black)
        prompt_text = font.render(prompt, True, white)
        default_text = font.render(f"Default: {default_value}", True, white)
        screen.blit(
            prompt_text,
            (screen_width // 2 - prompt_text.get_width() // 2, screen_height // 2 - 50),
        )
        screen.blit(
            default_text,
            (
                screen_width // 2 - default_text.get_width() // 2,
                screen_height // 2 - 80,
            ),
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
                    if input_text == "":
                        return default_value
                    else:
                        try:
                            return type(default_value)(input_text)
                        except ValueError:
                            input_text = ""  # Clear invalid input
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        clock.tick(30)
