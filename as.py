import sys
import re
import tkinter as tk
from queue import PriorityQueue
from time import sleep

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

def manhattan_distance(start, goal):
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

window = None
grid_frame = None

def update_gui(grid, current, open_set):
    global grid_frame
    if grid_frame is None:  # Added safety check
        return

    for widget in grid_frame.winfo_children():
        widget.destroy()

    cell_size = 70
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'R' or (x, y) == current:
                color = 'blue'
            elif grid[y][x] == 'G':
                color = 'green'
            elif (x, y) in [item[1] for item in open_set.queue]:
                color = 'orange'

            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)

    window.update()

def a_star_search(grid, start, goal_states):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal_states[0])}

    while not open_set.empty():
        _, current = open_set.get()

        if current in goal_states:
            return True, reconstruct_path(came_from, current)

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] != 'X':
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal_states[0])
                    if neighbor not in [item[1] for item in open_set.queue]:
                        open_set.put((f_score[neighbor], neighbor))

        update_gui(grid, current, open_set)
        sleep(0.5)

    return False, []

def print_grid_gui(grid, path=[]):
    global window, grid_frame
    window = tk.Tk()
    window.title("A* Pathfinding")
    grid_frame = tk.Frame(window)
    grid_frame.pack()

    update_gui(grid, None, PriorityQueue())

    window.mainloop()

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def print_grid(grid, path=[]):
    for y    in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            if (x, y) in path:
                row += 'P '  # Mark path
            else:
                row += f'{grid[y][x]} '
        print(row)

def main(file_path, use_gui=False):
    global window, grid_frame
    if use_gui:
        window = tk.Tk()
        window.title("A* Pathfinding")
        grid_frame = tk.Frame(window)
        grid_frame.pack()

        # Function to handle window close event
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
        update_gui(grid, None, PriorityQueue())
        found, path = a_star_search(grid, initial_state, goal_states)
        if found:
            update_gui(grid, None, PriorityQueue())
            for position in path:
                update_gui(grid, position, PriorityQueue())
                sleep(0.4)
        window.mainloop()
    else:
        found, path = a_star_search(grid, initial_state, goal_states)
        if found:
            print_grid(grid, path)
        else:
            print("Path not found.")

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python as.py <file_path> [--gui]")
        sys.exit(1)

    use_gui = '--gui' in sys.argv
    file_path = sys.argv[1] if sys.argv[1] != '--gui' else sys.argv[2]
    main(file_path, use_gui)
