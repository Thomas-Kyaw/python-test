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
    time.sleep(0.1)  # Slow down the update speed for better visualization

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

def main(file_path, depth_limit):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]
    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 dls_gui.py <file_path> <depth_limit>")
        sys.exit(1)
    file_path = sys.argv[1]
    depth_limit = int(sys.argv[2])
    main(file_path, depth_limit)
