import tkinter as tk
import sys
import re
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

import tkinter as tk
import sys
import re
import time

# Initialize the GUI window and grid frame
window = None
grid_frame = None

def init_gui(grid):
    global window, grid_frame
    window = tk.Tk()
    window.title("DLS Pathfinding Visualization")
    grid_frame = tk.Frame(window)
    grid_frame.pack()
    update_gui(grid, [], None)

def update_gui(grid, current_path=[], current=None):
    global grid_frame
    cell_size = 50

    for widget in grid_frame.winfo_children():
        widget.destroy()

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'G':
                color = 'green'
            elif grid[y][x] == 'R':
                color = 'blue'
            if (x, y) in current_path:
                color = 'light blue'  # Color for the current path
            if (x, y) == current:
                color = 'red'  # Color for the current position
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)
    window.update_idletasks()
    window.update()
    time.sleep(0.5)  # Slow down the update speed for better visualization

def dls(grid, start, goal, limit, update_func, visited, path=[]):
    if start == goal:
        return [start]
    
    if limit == 0:
        return None
    
    visited.add(start)
    new_path = path + [start]
    update_func(grid, new_path, start)
    
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        next_pos = (start[0] + dx, start[1] + dy)
        if 0 <= next_pos[0] < len(grid[0]) and 0 <= next_pos[1] < len(grid) and grid[next_pos[1]][next_pos[0]] != 'X' and next_pos not in visited:
            result_path = dls(grid, next_pos, goal, limit - 1, update_func, visited, new_path)
            if result_path:
                return result_path
    
    return None

def dls_console(grid, start, goal, limit, visited=set(), path=[]):
    if start == goal:
        return path + [start]
    
    if limit <= 0 or start in visited:
        return None
    
    visited.add(start)
    new_path = path + [start]
    
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        next_pos = (start[0] + dx, start[1] + dy)
        if 0 <= next_pos[0] < len(grid[0]) and 0 <= next_pos[1] < len(grid) and grid[next_pos[1]][next_pos[0]] != 'X':
            result_path = dls_console(grid, next_pos, goal, limit - 1, visited, new_path)
            if result_path is not None:
                return result_path
    
    return None

def print_grid(grid, path=[]):
    # Prints the grid and marks the path from start to goal
    for y in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            if (x, y) == path[0]:
                cell = 'S '  # Start
            elif (x, y) in path[1:-1]:
                cell = '. '  # Path
            elif (x, y) == path[-1]:
                cell = 'G '  # Goal
            elif grid[y][x] == 'X':
                cell = 'X '  # Obstacle
            elif grid[y][x] == 'G':
                cell = 'G '  # Unreached goal
            elif grid[y][x] == 'R':
                cell = 'R '  # Unreached start
            else:
                cell = '- '  # Empty space
            row += cell
        print(row)

def main(file_path, depth_limit, use_gui=False):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]
    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    if use_gui:
        init_gui(grid)
        for goal in goal_states:
            visited = set()
            path = dls(grid, initial_state, goal, depth_limit, update_gui, visited, [])
            if path:
                print("Path found from", initial_state, "to goal state:", goal)
                print("Path:", path)
                update_gui(grid, path, None)  # Update GUI to show the final path
                break
        if not path:
            print("No path found from", initial_state, "to any goal state.")
            update_gui(grid, [], None)  # Clear path visualization
        window.mainloop()
    else:
        for goal in goal_states:
            visited = set()
            path = dls_console(grid, initial_state, goal, depth_limit, visited, [])
            if path:
                print("Path found from", initial_state, "to goal state:", goal)
                print("Path:", path)
                print_grid(grid, path)  # Print the grid with the path marked
                break
        if not path:
            print("No path found from", initial_state, "to any goal state with depth limit", depth_limit)

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--gui']

    if len(args) != 2:
        print("Usage: python dls_gui.py <file_path> <depth_limit> [--gui]")
        sys.exit(1)

    file_path = args[0]
    depth_limit = int(args[1])
    main(file_path, depth_limit, use_gui)
