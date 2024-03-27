import sys
import re
import tkinter as tk
from queue import Queue
import time

def read_input_file(file_path):
    # Reads an input file, filtering out comments and blank lines.
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def extract_grid_dimensions(line):
    # Extracts the number of rows and columns for the grid from the first line of the input.
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        sys.exit(1)

def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    # Creates an empty grid and marks the initial and goal positions.
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'
    return grid

def place_blocks(grid, blocks):
    # Places obstacles ('X') on the grid as specified in the input.
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'

def print_grid(grid, path=[]):
    # Prints the grid, marking the path if one was found.
    for y in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            if (x, y) in path:
                row += 'P '
            else:
                row += f'{grid[y][x]} '
        print(row.strip())

def bidirectional_search(grid, start, goal_states):
    # Initializes queues for the start and goal, and tracks visited nodes.
    queue_start = Queue()
    queue_goal = Queue()

    queue_start.put((start, [start]))
    queue_goal.put((goal_states[0], [goal_states[0]]))

    visited_start = {start: [start]}
    visited_goal = {goal_states[0]: [goal_states[0]]}

    while not queue_start.empty() and not queue_goal.empty():
        # Expand nodes from start towards goal.
        if not queue_start.empty():
            current_start, path_start = queue_start.get()
            if current_start in visited_goal:  # Check for intersection.
                return True, path_start[:-1] + visited_goal[current_start][::-1]
            for neighbor in get_neighbors(current_start, grid):
                if neighbor not in visited_start:
                    visited_start[neighbor] = path_start + [neighbor]
                    queue_start.put((neighbor, path_start + [neighbor]))

        # Expand nodes from goal towards start.
        if not queue_goal.empty():
            current_goal, path_goal = queue_goal.get()
            if current_goal in visited_start:  # Check for intersection.
                return True, visited_start[current_goal][:-1] + path_goal[::-1]
            for neighbor in get_neighbors(current_goal, grid):
                if neighbor not in visited_goal:
                    visited_goal[neighbor] = path_goal + [neighbor]
                    queue_goal.put((neighbor, path_goal + [neighbor]))

    return False, []

def get_neighbors(position, grid):
    # Returns valid, non-obstacle neighbors of a given position.
    x, y = position
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-way connectivity.
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 'X':
            neighbors.append((nx, ny))
    return neighbors


# GUI setup
def setup_gui(grid):
    global window, canvas
    window = tk.Tk()
    window.title("Bidirectional Search Visualization")
    
    canvas_size = 500
    cell_size = canvas_size // max(len(grid), len(grid[0]))
    canvas = tk.Canvas(window, width=len(grid[0])*cell_size, height=len(grid)*cell_size)
    canvas.pack()

    draw_grid(grid, cell_size)
    window.update()
    return cell_size

def draw_grid(grid, cell_size):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'R':
                color = 'blue'
            elif grid[y][x] == 'G':
                color = 'green'
            canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill=color, outline='gray')

def update_gui(path_from_start, path_from_goal, cell_size):
    for position in path_from_start:
        x, y = position
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill='light blue', outline='gray')

    for position in path_from_goal:
        x, y = position
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill='pink', outline='gray')
    
    window.update()

def bidirectional_search_with_final_path_highlight(grid, start, goal, update_func, cell_size):
    queue_start = Queue()
    queue_goal = Queue()

    queue_start.put((start, [start]))
    queue_goal.put((goal, [goal]))

    visited_start = {start: start}
    visited_goal = {goal: goal}

    while not queue_start.empty() and not queue_goal.empty():
        # Search from start
        current_start, path_start = queue_start.get()
        for neighbor in get_neighbors(current_start, grid):
            if neighbor in visited_goal:
                final_path = path_start + [neighbor] + visited_goal[neighbor][::-1][1:]
                draw_final_path(final_path, cell_size)
                return final_path
            if neighbor not in visited_start:
                visited_start[neighbor] = path_start + [neighbor]
                queue_start.put((neighbor, path_start + [neighbor]))
        
        # Update visualization for search from start
        update_func(path_start, [], cell_size)

        # Search from goal
        current_goal, path_goal = queue_goal.get()
        for neighbor in get_neighbors(current_goal, grid):
            if neighbor in visited_start:
                final_path = visited_start[neighbor] + [neighbor] + path_goal[::-1][1:]
                draw_final_path(final_path, cell_size)
                return final_path
            if neighbor not in visited_goal:
                visited_goal[neighbor] = path_goal + [neighbor]
                queue_goal.put((neighbor, path_goal + [neighbor]))

        # Update visualization for search from goal
        update_func([], path_goal, cell_size)

        # Slow down the loop for visualization purposes
        time.sleep(0.5)

    return None

def draw_final_path(path, cell_size):
    for position in path:
        x, y = position
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill='yellow', outline='gray')
    window.update_idletasks()
    window.update()

def parse_tuple(s):
    # Extracts numbers from a string and returns them as a tuple of integers
    return tuple(map(int, re.findall(r'\d+', s)))

def main_with_gui(file_path):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = parse_tuple(content[1])
    goal_states = [parse_tuple(goal_state) for goal_state in content[2].split('|')]
    blocks = [parse_tuple(block) for block in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    cell_size = setup_gui(grid)
    goal_state = goal_states[0] if goal_states else None

    if goal_state:
        path = bidirectional_search_with_final_path_highlight(grid, initial_state, goal_state, update_gui, cell_size)
        if path:
            print("Path found!")
        else:
            print("No path found.")
    else:
        print("Error: No goal state provided.")

    window.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 bs.py <file_path>")
    else:
        main_with_gui(sys.argv[1])