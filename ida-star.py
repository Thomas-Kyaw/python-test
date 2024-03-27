import sys
import re
import tkinter as tk
import time

# Global variables for GUI
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

def manhattan_distance(pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

def ida_star(grid, start, goals):
    path = []
    threshold = min(manhattan_distance(start, goal) for goal in goals)
    
    while True:
        temp, path = search(start, 0, threshold, grid, goals, [start], {start})
        if temp == "FOUND":
            return path
        if temp == float('inf'):
            return []
        threshold = temp

def search(node, g, threshold, grid, goals, path, visited):
    f = g + min(manhattan_distance(node, goal) for goal in goals)
    if f > threshold:
        return f, path
    if node in goals:
        update_gui(grid, path=path + [node], current=node)  # Update to show current path + node
        return "FOUND", path
    min_threshold = float('inf')

    update_gui(grid, path=path, current=node)  # Update GUI on each recursive call to show current exploration
    time.sleep(0.05)  # Slow down to visualize the search

    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        x, y = node[0] + dx, node[1] + dy
        if 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] != 'X' and (x, y) not in visited:
            visited.add((x, y))
            temp, new_path = search((x, y), g + 1, threshold, grid, goals, path + [(x, y)], visited)
            if temp == "FOUND":
                return "FOUND", new_path  # Found a path, no need to remove from visited as the path is correct
            if temp < min_threshold:
                min_threshold = temp
            else:
                visited.remove((x, y))  # Backtrack: remove from visited if not leading to a solution

    return min_threshold, path

def init_gui(grid):
    global window, grid_frame
    window = tk.Tk()
    window.title("IDA* Pathfinding")
    grid_frame = tk.Frame(window)
    grid_frame.pack()
    update_gui(grid)

def update_gui(grid, path=[], current=None):
    global grid_frame
    if grid_frame is None:
        return  # Guard against calling before initialization
    for widget in grid_frame.winfo_children():
        widget.destroy()
    cell_size = 50
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
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)
    window.update_idletasks()
    window.update()
    time.sleep(0.05) # Adjust the sleep time as needed for visualization

def main(file_path):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    init_gui(grid)  # Initialize GUI with the grid

    path = ida_star(grid, initial_state, goal_states)  # Run IDA* to find a path

    if path:
        print("Path found:", path)
        update_gui(grid, path=path, current=None)  # Visualize the final path
    else:
        print("No path found.")
        update_gui(grid, path=[], current=None)  # Show the grid without a path

    window.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    main(sys.argv[1])
