# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 8), (2, 7), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self):
        """
        Returns only local sensor readings instead of global coordinates.
        Percept: {'wall_ahead': bool, 'food_here': bool}
        """
        x, y = self.agent_pos
        dx, dy = self.agent_direction

        next_x, next_y = x + dx, y + dy

        # Check boundaries or obstacle grid
        wall_ahead = (
            next_x < 0 or next_x >= self.grid_width or
            next_y < 0 or next_y >= self.grid_height or
            self.grid[next_y][next_x] == 'WALL'
        )

        food_here = (self.grid[y][x] == 'FOOD')

        return {
            'wall_ahead': wall_ahead,
            'food_here': food_here
        }

    def execute_action(self, action: str):
        self.steps += 1
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 300 or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()

class SimpleReflexAgent:
    """
        Simple Reflex Agent acting solely on immediate percepts via Condition-Action rules.
        No internal state or percept history is maintained.
        """
    def sense_and_act(self, percept):
     # Condition-Action Rule 1: Clean/Consume if food is present
        if percept['food_here']:
            return 'suck'
        
        # Condition-Action Rule 2: Turn left if facing an obstacle
        elif percept['wall_ahead']:
            return 'turn_left'
        
        # Condition-Action Rule 3: Default action - move forward
        else:
            return 'move_forward'

class ModelBasedAgent:
    """
    Model-Based Agent that tracks an internal state (visited positions and heading)
    to overcome partial observability.
    """
    def __init__(self):
        # Internal State / Memory
        self.current_pos = (0, 0)
        self.headings = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # UP, RIGHT, DOWN, LEFT
        self.heading_idx = 0  # Starts facing UP
        self.visited_cells = {self.current_pos}
        self.last_action = None

    def _update_internal_state(self, percept):
        """
        Transition Model: Updates internal position based on last action taken.
        Sensor Model: Updates knowledge of current cell based on percept.
        """
        if self.last_action == 'move_forward' and not percept.get('hit_wall', False):
            dx, dy = self.headings[self.heading_idx]
            self.current_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
            self.visited_cells.add(self.current_pos)
            
        elif self.last_action == 'turn_left':
            self.heading_idx = (self.heading_idx - 1) % 4
            
        elif self.last_action == 'turn_right':
            self.heading_idx = (self.heading_idx + 1) % 4

    def sense_and_act(self, percept):
        # 1. Update internal state before acting
        self._update_internal_state(percept)

        # 2. Predict relative cell coordinates
        curr_dir = self.headings[self.heading_idx]
        left_dir = self.headings[(self.heading_idx - 1) % 4]
        right_dir = self.headings[(self.heading_idx + 1) % 4]

        left_cell = (self.current_pos[0] + left_dir[0], self.current_pos[1] + left_dir[1])
        right_cell = (self.current_pos[0] + right_dir[0], self.current_pos[1] + right_dir[1])

        # 3. Condition-Action Rules conditioned on Internal State
        if percept['food_here']:
            action = 'suck'
        elif percept['wall_ahead']:
            # If left has already been explored, turn right instead to avoid loops
            if left_cell in self.visited_cells and right_cell not in self.visited_cells:
                action = 'turn_right'
            else:
                action = 'turn_left'
        else:
            action = 'move_forward'

        self.last_action = action
        return action


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()