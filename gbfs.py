import tkinter as tk
import sys
import re
from queue import PriorityQueue
import time

# Initialize the GUI window and grid frame
window = None
grid_frame = None

def read_input_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def extract_grid_dimensions(line):
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        return None

def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'  # Place the robot at the initial state
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'  # Place the goals
    return grid

def place_blocks(grid, blocks):
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'  # Place blocks as obstacles

def manhattan_distance(point, goals):
    # Start with a large number representing infinity
    closest_distance = float('inf')
    # Iterate over each goal and update the closest distance
    for goal in goals:
        distance = abs(point[0] - goal[0]) + abs(point[1] - goal[1])
        if distance < closest_distance:
            closest_distance = distance
    return closest_distance

def greedy_best_first_search(grid, start, goal_states, use_gui=True, visualization_speed=0.5):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {start: None}
    visited = set()
    num_visited_nodes = 0  # Initialize visited nodes counter

    while not open_set.empty():
        _, current = open_set.get()
        num_visited_nodes += 1  # Increment visited nodes counter

        if current in goal_states:
            path = reconstruct_path(came_from, current)
            directions = get_path_directions(path)  # Get directions from the path
            print(f"Goal Node: {current}")
            print(f"Visited Nodes: {num_visited_nodes}")
            print(f"Path Directions: {directions}")
            if use_gui:
                update_gui(grid, path=path + [current], visited=visited, current=current, start=start, goal_states=goal_states, sleep_time=visualization_speed)
            return True, path, current, num_visited_nodes, directions

        visited.add(current)
        if use_gui:
            update_gui(grid, path=[], visited=visited, current=current, start=start, goal_states=goal_states, sleep_time=visualization_speed)

        for dx, dy in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] != 'X' and neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                open_set.put((manhattan_distance(neighbor, goal_states), neighbor))

    if use_gui:
        update_gui(grid, path=[], visited=visited, current=None, start=start, goal_states=goal_states, sleep_time=visualization_speed)
    return False, [], None, num_visited_nodes, []

def init_gui(grid, start, goal_states):
    global window, grid_frame
    window = tk.Tk()
    window.title("GBFS Pathfinding Visualization")
    grid_frame = tk.Frame(window)
    grid_frame.pack()
    update_gui(grid, start=start, goal_states=goal_states)  # Initial GUI setup with the start state highlighted

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def get_path_directions(path):
    directions = []
    for i in range(len(path) - 1):
        current_node, next_node = path[i], path[i + 1]
        dx, dy = next_node[0] - current_node[0], next_node[1] - current_node[1]
        if dx == 0 and dy == -1:
            directions.append('up')
        elif dx == 0 and dy == 1:
            directions.append('down')
        elif dx == -1 and dy == 0:
            directions.append('left')
        elif dx == 1 and dy == 0:
            directions.append('right')
    return directions

def update_gui(grid, path=[], visited=set(), current=None, start=None, goal_states=None, sleep_time=0.5):
    global grid_frame, window
    cell_size = 50

    if goal_states is None:
        goal_states = []

    for widget in grid_frame.winfo_children():
        widget.destroy()

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if (x, y) == start:  # Check if the current cell is the start position
                color = 'blue'  # Color for the start position
            elif grid[y][x] == 'X':
                color = 'black'
            elif (x, y) in goal_states:
                color = 'green'
            elif (x, y) in path:
                color = 'orange'
            elif (x, y) in visited and (x, y) != current:
                color = '#f0e68c'
            if (x, y) == current:
                color = '#ff4500'

            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)

    window.update()  # Force the window to update
    time.sleep(sleep_time)  # Slow down the update speed

def main(file_path, use_gui=True):
    content = read_input_file(file_path)
    if content is None:
        sys.exit(1)

    num_rows, num_cols = extract_grid_dimensions(content[0])
    if num_rows is None or num_cols is None:
        sys.exit(1)

    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    if use_gui:
        init_gui(grid, initial_state, set(goal_states))
        found, path, goal_node, visited_nodes, path_directions = greedy_best_first_search(grid, initial_state, set(goal_states), use_gui=use_gui, visualization_speed=0.5)
        if found:
            path = [initial_state] + path
            update_gui(grid, path=path, visited=set(), current=None, start=initial_state, goal_states=set(goal_states))
            time.sleep(2)  # Give time to visualize the final path
        window.mainloop()
    else:
        found, path, goal_node, visited_nodes, path_directions = greedy_best_first_search(grid, initial_state, set(goal_states), use_gui=use_gui, visualization_speed=0.5)
        if found:
            print(f"Path found from {initial_state} to goal node {goal_node} with {visited_nodes} nodes visited.")
            print(f"Path directions: {path_directions}")
        else:
            print(f"No path found after visiting {visited_nodes} nodes.")

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv  # GUI mode is optional and activated with --gui
    args = [arg for arg in sys.argv[1:] if arg not in ['--console', '--gui']]

    if len(args) != 1:
        print("Usage Error: python script.py <file_path> [--gui]")
        sys.exit(1)

    main(args[0], use_gui)
