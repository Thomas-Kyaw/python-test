import sys
import re
import tkinter as tk
import time  # Import the time module

# GUI global variables
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

def dfs(grid, x, y, goal_states, visited, path=[]):
    if (x, y) in goal_states:
        return True, path + [(x, y)]
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    visited.add((x, y))
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] not in ['X', 'V'] and (nx, ny) not in visited:
            grid[ny][nx] = 'V'
            update_gui(grid, path=path + [(x, y)], current=(nx, ny), visited=visited, start=(x, y))
            found, new_path = dfs(grid, nx, ny, goal_states, visited, path + [(x, y)])
            if found:
                return True, new_path
            grid[ny][nx] = '-'
    return False, path

def dfs_console(grid, x, y, goal_states, visited, path=[]):
    if (x, y) in goal_states:
        return True, path + [(x, y)]
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    visited.add((x, y))
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] not in ['X', 'V'] and (nx, ny) not in visited:
            result, new_path = dfs_console(grid, nx, ny, goal_states, visited, path + [(x, y)])
            if result:
                return True, new_path
    return False, path

def update_gui(grid, path=[], current=None, visited=set(), start=None):
    global grid_frame
    for widget in grid_frame.winfo_children():
        widget.destroy()

    cell_size = 50
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'G':
                color = 'green'
            if (x, y) in path:
                color = 'orange'
            elif (x, y) in visited and (x, y) != start:
                color = '#f0e68c'
            if (x, y) == current:
                color = '#ff4500'
            if (x, y) == start:
                color = '#1e90ff'

            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)

    window.update_idletasks()
    window.update()
    time.sleep(0.5) 

def init_gui(grid):
    global window, grid_frame
    window = tk.Tk()
    window.title("DFS Pathfinding")
    
    grid_frame = tk.Frame(window)
    grid_frame.pack()

    update_gui(grid)

    def on_window_close():
        global window
        if window:
            window.quit()
            window = None
            
    window.protocol("WM_DELETE_WINDOW", on_window_close)

def print_grid(grid, path=[]):
    for y in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            if (x, y) in path:
                row += 'P '  # Path
            elif grid[y][x] == 'X':
                row += 'X '  # Obstacle
            elif grid[y][x] == 'G':
                row += 'G '  # Goal
            elif grid[y][x] == 'R':
                row += 'S '  # Start
            else:
                row += '- '  # Empty
        print(row)

def main(file_path, use_gui=False):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]
    
    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    if use_gui:
        init_gui(grid)
        visited = set()
        found, path = dfs(grid, initial_state[0], initial_state[1], set(goal_states), visited)
        if found:
            print("Path found!")
            update_gui(grid, path=path, current=None, visited=visited, start=initial_state)
        else:
            print("No path found.")
            update_gui(grid, path=[], current=None, visited=visited, start=initial_state)
        window.mainloop()
    else:
        visited = set()
        found, path = dfs_console(grid, initial_state[0], initial_state[1], set(goal_states), visited)
        if found:
            print("Path found:", path)
            print_grid(grid, path)
        else:
            print("No path found.")

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != '--gui']

    if len(args) != 1:
        print("Usage: python script.py <file_path> [--gui]")
        sys.exit(1)
    
    main(args[0], use_gui)
