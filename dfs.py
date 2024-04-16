import sys
import re
import tkinter as tk
import time
import itertools

# GUI global variables
window = None
grid_frame = None

# Function to read input file
def read_input_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

# Function to extract grid dimensions from the first line of the file
def extract_grid_dimensions(line):
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        sys.exit(1)

# Function to create an empty grid
def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'
    return grid

# Function to place blocks on the grid
def place_blocks(grid, blocks):
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'

# Function to update the GUI
def update_gui(grid, current, path=[], visited=set()):
    global grid_frame
    for widget in grid_frame.winfo_children():
        widget.destroy()
    cell_size = 70
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'G':
                color = 'green'
            if (x, y) in path:
                color = 'yellow'
            elif (x, y) == current:
                color = 'blue'
            elif (x, y) in visited:
                color = 'lightgrey'
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)
    window.update()
    time.sleep(0.5)

# Function to get direction between two points
def get_direction(from_node, to_node):
    directions = {
        (0, -1): 'UP',
        (0, 1): 'DOWN',
        (-1, 0): 'LEFT',
        (1, 0): 'RIGHT'
    }
    dx = to_node[0] - from_node[0]
    dy = to_node[1] - from_node[1]
    return directions.get((dx, dy), 'UNKNOWN')

# Depth-First Search function with goal node, visited nodes count, and path directions
def dfs(grid, x, y, goal_states, visited, path=[], update_gui_callback=None):
    visited.add((x, y))
    if (x, y) in goal_states:
        return True, path + [(x, y)], (x, y), len(visited)  # Return path, goal node, and visited nodes count
    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] not in ['X', 'V'] and (nx, ny) not in visited:
            current_path = path + [(x, y)]
            if update_gui_callback:
                update_gui_callback(grid, (nx, ny), current_path, visited)
            found, new_path, goal_node, visited_count = dfs(grid, nx, ny, goal_states, visited, current_path, update_gui_callback)
            if found:
                return True, new_path, goal_node, visited_count
    return False, path, None, len(visited)

# Function to calculate directions from path
def calculate_directions(path):
    directions = [get_direction(path[i], path[i + 1]) for i in range(len(path) - 1)]
    return directions

# Function to initialize the GUI
def init_gui(grid):
    global window, grid_frame
    window = tk.Tk()
    window.title("DFS Pathfinding Visualization")
    grid_frame = tk.Frame(window)
    grid_frame.pack()

    # Update the GUI with the initial grid state before any search
    update_gui(grid, None)

    # Define the function to be called when the window is closed
    def on_window_close():
        global window
        if window:
            window.quit()
            window = None

    # Set the function to be called when the window is closed
    window.protocol("WM_DELETE_WINDOW", on_window_close)


# Main function
def main(file_path, use_gui=False):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]
    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)
    visited = set()
    if use_gui:
        init_gui(grid)
        found, path, goal_node, visited_count = dfs(grid, initial_state[0], initial_state[1], set(goal_states), visited, update_gui_callback=update_gui)
        if found:
            print(f"Path found to goal {goal_node} with {visited_count} nodes visited.")
            directions = calculate_directions(path)
            print("Directions:", directions)
            update_gui(grid, None, path, visited)
        else:
            print("No path found.")
        window.mainloop()
    else:
        found, path, goal_node, visited_count = dfs(grid, initial_state[0], initial_state[1], set(goal_states), visited)
        if found:
            print(f"Path found to goal {goal_node} with {visited_count} nodes visited.")
            directions = calculate_directions(path)
            print("Path:", path)
            print("Directions:", directions)
        else:
            print("No path found.")

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--gui']
    if len(args) != 1:
        print("Usage: python script.py <file_path> [--gui]")
        sys.exit(1)
    main(args[0], use_gui)
