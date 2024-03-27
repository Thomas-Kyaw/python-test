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

def manhattan_distance(point, goals):
    return min(abs(point[0] - goal[0]) + abs(point[1] - goal[1]) for goal in goals)

def greedy_best_first_search(grid, start, goal_states):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    visited = set()

    while not open_set.empty():
        _, current = open_set.get()
        if current in goal_states:
            path = reconstruct_path(came_from, current)
            update_gui(grid, path=path, visited=visited, current=current, goal_states=goal_states)
            print("Result: Path found.")
            return True, path
        visited.add(current)
        update_gui(grid, path=[], visited=visited, current=current, goal_states=goal_states)

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] != 'X' and neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                open_set.put((manhattan_distance(neighbor, goal_states), neighbor))

    print("Result: No path found.")
    return False, []

def init_gui(grid, goal_states):
    global window, grid_frame
    window = tk.Tk()
    window.title("GBFS Pathfinding Visualization")
    grid_frame = tk.Frame(window)
    grid_frame.pack()
    update_gui(grid, goal_states=goal_states)

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def update_gui(grid, path=[], visited=set(), current=None, goal_states=None):
    global grid_frame
    cell_size = 50
    
    if goal_states is None:
        goal_states = []

    for widget in grid_frame.winfo_children():
        widget.destroy()

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif (x,y) in goal_states:
                color = 'green'
            if (x, y) in path:
                color = 'orange'
            elif (x, y) in visited and (x, y) != current:
                color = '#f0e68c'
            if (x, y) == current:
                color = '#ff4500'
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)
    window.update()
    time.sleep(0.5)

def main(file_path):
    global window
    content = read_input_file(file_path)
    if content is None: # Check if file reading was successful
        sys.exit(1)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    if num_rows is None or num_cols is None:  # Check if grid dimensions extraction was successful
        sys.exit(1)

    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    init_gui(grid, set(goal_states))
    found, path = greedy_best_first_search(grid, initial_state, set(goal_states))

    # After search, ensure the final state is visualized before closing
    if found:
        update_gui(grid, path=path, visited=set(), current=None, goal_states=set(goal_states))
        time.sleep(2)  # Give time to visualize the final path
    else:
        print("No path found.")
        time.sleep(2)  # Give time to show the grid without a path
    window.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage Error: Usage: python3 gbfs.py <file_path>") # Notify usage error in terminal
        sys.exit(1)
    main(sys.argv[1])