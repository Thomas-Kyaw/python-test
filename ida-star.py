import sys
import re
import tkinter as tk
import time

# Global variables for GUI
window = None
grid_frame = None
cell_frames = []  # Store references to cell frames
visited_nodes = set()

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

def manhattan_distance(pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

def ida_star(grid, start, goals, use_gui=False):
    path = []
    threshold = min(manhattan_distance(start, goal) for goal in goals)
    
    while True:
        temp, path = search(start, 0, threshold, grid, goals, [start], {start}, use_gui)
        if temp == "FOUND":
            return path
        if temp == float('inf'):
            return []
        threshold = temp

def search(node, g, threshold, grid, goals, path, visited, use_gui):
    global visited_nodes
    visited_nodes.add(node)  # Track visited nodes globally
    f = g + min(manhattan_distance(node, goal) for goal in goals)
    if f > threshold:
        return f, path
    if node in goals:
        if use_gui:
            update_gui(grid, path=path + [node], current=node, use_gui=use_gui)
        return "FOUND", path
    min_threshold = float('inf')

    if use_gui:
        update_gui(grid, path=path, current=node, use_gui=use_gui)
        time.sleep(0.05)

    for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        x, y = node[0] + dx, node[1] + dy
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] != 'X' and (x, y) not in visited:
            visited.add((x, y))
            temp, new_path = search((x, y), g + 1, threshold, grid, goals, path + [(x, y)], visited, use_gui)
            if temp == "FOUND":
                return "FOUND", new_path
            if temp < min_threshold:
                min_threshold = temp
            visited.remove((x, y))  # Backtrack: remove from visited if not leading to a solution

    return min_threshold, path

def init_gui(grid):
    global window, grid_frame, cell_frames
    window = tk.Tk()
    window.title("IDA* Pathfinding")
    grid_frame = tk.Frame(window)
    grid_frame.pack()

    cell_frames = [[None for _ in range(len(grid[0]))] for _ in range(len(grid))]  # Initialize cell frame references
    cell_size = 50
    for y in range(len(grid)):
        row = []
        for x in range(len(grid[0])):
            color = 'white'
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)
            row.append(cell)
        cell_frames[y] = row
    update_gui(grid, use_gui=True)  # Initial grid setup

def update_gui(grid, path=[], current=None, use_gui=False):
    if not use_gui or grid_frame is None:
        return  # Skip GUI update if not in GUI mode
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif (x, y) in path:
                color = 'orange'
            elif grid[y][x] == 'G':
                color = 'green'
            elif grid[y][x] == 'R':
                color = 'blue'
            cell_frames[y][x].config(bg=color)
    window.update_idletasks()
    window.update()
    time.sleep(0.3)  # Adjust the sleep time as needed for visualization

def print_grid_with_path(grid, path):
    grid_copy = [row[:] for row in grid]  # Make a copy of the grid
    for x, y in path:
        grid_copy[y][x] = 'P'  # Mark the path on the grid
    for row in grid_copy:
        print(' '.join(row))  # Print each row of the grid

def format_directions(path):
    directions = []
    direction_symbols = {(-1, 0): 'up', (1, 0): 'down', (0, -1): 'left', (0, 1): 'right'}
    for i in range(1, len(path)):
        dx = path[i][0] - path[i-1][0]
        dy = path[i][1] - path[i-1][1]
        directions.append(direction_symbols.get((dx, dy), 'unknown'))
    return '; '.join(directions)

def main(file_path, use_gui=False):
    content = read_input_file(file_path)
    if content is None:
        sys.exit(1)

    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    if use_gui:
        init_gui(grid)
    path = ida_star(grid, initial_state, set(goal_states), use_gui)

    if path:
        directions = format_directions(path)
        print("Path found:", path)
        print(f"Goal node: {goal_states[0]}")
        print(f"Nodes visited: {len(visited_nodes)}")
        print(f"Direction path: {directions}")
        if use_gui:
            update_gui(grid, path=path, use_gui=use_gui)
            window.mainloop()
    else:
        print("No path found.")

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--gui']

    if len(args) != 1:
        print("Usage: python3 ida_star.py <file_path> [--gui]")
        sys.exit(1)

    main(args[0], use_gui)
