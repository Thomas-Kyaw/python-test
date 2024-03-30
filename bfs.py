import sys
import re
from queue import Queue
import tkinter as tk
from tkinter import messagebox
import time 

# Global variables for the GUI
window = None  # Tkinter window
grid_frame = None  # Frame for the grid

def read_input_file(file_path):
    # Reads an input file, removing comments and blank lines.
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def extract_grid_dimensions(line):
    # Extracts grid dimensions (rows, cols) from a line.
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        sys.exit(1)

def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    # Creates an empty grid and places the robot ('R') and goal ('G') positions.
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'
    return grid

def place_blocks(grid, blocks):
    # Places blocks ('X') on the grid as obstacles.
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'

def bfs_step(queue, goal_states, visited, start, grid):
    if not queue.empty():
        path = queue.get()
        current = path[-1]
        visited.add(current)

        update_gui(grid, path=path, current=current, visited=visited, start=start)  # Show current path

        if current in goal_states:
            # If a goal is found, don't schedule more steps.
            print("Path found!")
            update_gui(grid, path=path, current=None, visited=visited, start=start)
            return

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = current
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 'X' and neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.put(new_path)

        # Schedule the next step with the grid passed as an argument
        window.after(500, bfs_step, queue, goal_states, visited, start, grid)
    else:
        # If the queue is empty, no path was found.
        print("No path found.")
        update_gui(grid, path=[], current=None, visited=visited, start=start)

def bfs(grid, start, goal_states):
    queue = Queue()
    queue.put([start])
    visited = set()

    # Start the BFS steps with a delay of 500ms between each one.
    window.after(500, bfs_step, queue, goal_states, visited, start, grid)

def bfs_console(grid, start, goal_states):
    queue = Queue()
    queue.put([start])  # Queue stores paths rather than nodes
    visited = set([start])
    
    while not queue.empty():
        path = queue.get()
        current = path[-1]
        
        if current in goal_states:
            print("Path found:", path)
            print_grid(grid, path)
            return path
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] != 'X' and neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.put(new_path)
    
    print("No path found.")
    return []

def print_grid(grid, path=[]):
    for y in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            if (x, y) == path[0]:
                row += 'S '  # Start
            elif (x, y) in path[1:-1]:
                row += 'P '  # Path
            elif (x, y) == path[-1] and len(path) > 1:
                row += 'G '  # Goal
            elif grid[y][x] == 'X':
                row += 'X '  # Obstacle
            elif grid[y][x] == 'G':
                row += 'G '  # Goal state (unreached)
            else:
                row += '- '  # Empty space
        print(row.strip())

def update_gui(grid, path=[], current=None, visited=set(), start=None):
    global grid_frame
    cell_size = 50  # Define the cell size

    for widget in grid_frame.winfo_children():
        widget.destroy()

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'  # Default color for empty cells
            if grid[y][x] == 'X':
                color = 'black'  # Obstacles
            elif grid[y][x] == 'G':
                color = 'green'  # Goals
            if (x, y) in path:
                color = 'orange'  # Path
            elif (x, y) in visited and (x, y) != start:
                color = '#f0e68c'  # Khaki for visited nodes
            if (x, y) == current:
                color = '#ff4500'  # OrangeRed for the current node being explored
            if (x, y) == start:
                color = '#1e90ff'  # DodgerBlue for the start node

            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)

    window.update_idletasks()  # For smoother updates

def init_gui(grid):
    global window, grid_frame
    window = tk.Tk()
    window.title("BFS Pathfinding")
    
    grid_frame = tk.Frame(window)
    grid_frame.pack()

    update_gui(grid)  # Initial grid display

    def on_window_close():
        global window
        if window:
            window.quit()
            window = None

    window.protocol("WM_DELETE_WINDOW", on_window_close)


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
        bfs(grid, initial_state, set(goal_states))
        window.mainloop()
    else:
        print("Starting BFS search without GUI...")
        bfs_console(grid, initial_state, goal_states)

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 bfs.py <file_path> [--gui]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path, use_gui)
