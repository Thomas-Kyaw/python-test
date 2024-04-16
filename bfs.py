import sys
import re
import tkinter as tk
from queue import Queue
from time import sleep
import itertools

# Global counter for nodes insertion order
insertion_counter = itertools.count()
open_set_tracker = set()  # Track nodes in the open set globally

def read_input_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def extract_grid_dimensions(line):
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        sys.exit(1)

def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'
    return grid

def place_blocks(grid, blocks):
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'

def get_direction(current, next_node):
    if current is None or next_node is None:
        return 'unknown'
    dx = next_node[0] - current[0]
    dy = next_node[1] - current[1]
    direction_map = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
    return direction_map.get((dx, dy), 'unknown')

def reconstruct_path(came_from, start, goal):
    path = []
    directions = []
    current = goal

    while current != start:  # Traverse back from goal to start
        next_node = came_from.get(current, None)
        if next_node is None:  # If start node is reached or no path is found
            break
        direction = get_direction(next_node, current)
        directions.append(direction)
        current = next_node
        path.append(current)

    path.reverse()
    directions.reverse()

    # Ensure the path starts at the initial state
    if path and path[0] != start:
        path.insert(0, start)

    # Ensure the path includes the last direction towards the goal
    if path[-1] != goal:
        last_direction = get_direction(path[-1], goal)
        directions.append(last_direction)
        path.append(goal)

    return path, directions

window = None
grid_frame = None

def update_gui(grid, current, path=[]):
    global grid_frame
    if grid_frame is None:
        return

    for widget in grid_frame.winfo_children():
        widget.destroy()

    cell_size = 70
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if (x, y) in path:
                color = 'yellow'
            elif grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'R' or (x, y) == current:
                color = 'blue'
            elif grid[y][x] == 'G':
                color = 'green'
            elif (x, y) in open_set_tracker:
                color = 'orange'
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)
    window.update()

def bfs_search(grid, start, goal_states):
    global open_set_tracker
    open_set = Queue()
    open_set.put(start)
    open_set_tracker = {start}
    came_from = {start: None}
    visited_nodes_count = 0  # Initialize the visited nodes count

    while not open_set.empty():
        current = open_set.get()
        open_set_tracker.remove(current)
        visited_nodes_count += 1  # Increment visited nodes count

        if current in goal_states:
            path, directions = reconstruct_path(came_from, start, current)
            return True, path, directions, visited_nodes_count  # Include visited node count in the return statement
        
        for dx, dy in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] != 'X' and neighbor not in came_from:
                open_set.put(neighbor)
                open_set_tracker.add(neighbor)
                came_from[neighbor] = current
        if window and grid_frame:
            update_gui(grid, current, [])
            sleep(0.5)
    
    return False, [], [], visited_nodes_count  # Return visited node count if no path is found

def print_grid(grid, path):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if (x, y) in path:
                print('P', end=' ')
            elif grid[y][x] == 'X':
                print('X', end=' ')
            elif grid[y][x] == 'R':
                print('R', end=' ')
            elif grid[y][x] == 'G':
                print('G', end=' ')
            else:
                print('.', end=' ')
        print()

def main(file_path, use_gui=False):
    global window, grid_frame
    if use_gui:
        window = tk.Tk()
        window.title("BFS Pathfinding")
        grid_frame = tk.Frame(window)
        grid_frame.pack()

        def on_window_close():
            global window
            if window:
                window.quit()
                window = None
        window.protocol("WM_DELETE_WINDOW", on_window_close)

    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    if use_gui:
        found, path, directions, visited_nodes_count = bfs_search(grid, initial_state, goal_states)
        if found:
            update_gui(grid, None, path)  # Final update to draw the entire path in yellow
        else:
            print("Path not found.")
        window.mainloop()
    else:
        found, path, directions, visited_nodes_count = bfs_search(grid, initial_state, goal_states)
        if found:
            print_grid(grid, path)
            print(f"Goal Node: {goal_states[0]}")  # Assume single goal state for this output
            print(f"Number of nodes visited by the path: {visited_nodes_count}")
            print("Path found with directions:")
            print(' -> '.join(directions))  # Print directions with arrows
        else:
            print("Path not found.")
            print(f"Number of nodes visited: {visited_nodes_count}")

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python bfs.py <file_path> [--gui]")
        sys.exit(1)

    use_gui = '--gui' in sys.argv
    file_path = sys.argv[1] if sys.argv[1] != '--gui' else sys.argv[2]
    main(file_path, use_gui)
