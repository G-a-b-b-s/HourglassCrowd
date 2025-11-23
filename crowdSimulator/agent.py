import time

from mesa import Agent
import random
import math


class CrowdAgent(Agent):
    def __init__(self, unique_id, model, scenario, obstacles):
        super().__init__(unique_id, model)
        self.steps = 0
        self.obstacles = obstacles
        self.collision_attempts = 0
        self.velocity = 0.02
        self.destination = Destination((0, 0), 'no', (0, 0, 0))
        self.personal_space_radius = 2
        self.visited_positions = []
        self.memory_limit = 4
        self.has_moved = False
        self.reached_destination = False
        self.scenario = scenario

    def is_finished(self, x, y):
        if abs(x - self.destination.pos[0]) + abs(y - self.destination.pos[1]) < 1:
            self.reached_destination = True
            if self.destination.preset == 'exit':
                self.model.schedule.remove(self)
                self.model.grid.remove_agent(self)
            return True
        return False

    def step(self):
        if not self.is_finished(self.pos[0], self.pos[1]):
            if not self.move_towards_goal_or_avoid_intruder(self.destination.pos):
                # Try escaping if movement towards the goal was blocked
                self.escape_wall()
            self.has_moved = True
        else:
            self.has_moved = False

        self.steps += 1

        time.sleep(0.05) if self.scenario == "Walking" else time.sleep(0.015)

    @staticmethod
    def calculate_distance(pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def normalize_distance(self, distance):
        return max(0, min(1, (self.personal_space_radius - distance) / self.personal_space_radius))

    def move_towards_goal_or_avoid_intruder(self, goal_pos):
        intruders = [agent for agent in self.model.schedule.agents
                     if agent.unique_id != self.unique_id and
                     self.calculate_distance(self.pos, agent.pos) <= self.personal_space_radius]

        if not intruders:
            return self.move_towards_goal(goal_pos)

        return self.avoid_intruders(intruders, goal_pos)

    def move_towards_goal(self, goal_pos):
        new_pos = self.get_next_position(self.pos[0], self.pos[1])

        # if not self.is_position_valid(new_pos):
        #     self.collision_attempts += 1
        #     if new_pos in self.model.collision_count:
        #         self.model.collision_count[new_pos] += 1
        #     else:
        #         self.model.collision_count[new_pos] = 1
        #     return False

        self.model.grid.move_agent(self, new_pos)
        # self.update_visited_positions(new_pos)
        return True

    def avoid_intruders(self, intruders, goal_pos):
        directions = {
            "up": (self.pos[0], self.pos[1] + 1),
            "down": (self.pos[0], self.pos[1] - 1),
            "left": (self.pos[0] - 1, self.pos[1]),
            "right": (self.pos[0] + 1, self.pos[1])
        }

        forces = {}

        for direction, pos in directions.items():
            if self.is_position_valid(pos):
                # Calculate total force for this position
                total_force = 0
                for intruder in intruders:
                    distance = self.calculate_distance(pos, intruder.pos)
                    if distance > 0:  #non-zero distances to avoid division by zero
                        normalized_distance = self.normalize_distance(distance)
                        if normalized_distance > 0:
                            total_force += 1 / normalized_distance

                # Extra force if this position was recently visited
                if pos in self.visited_positions:
                    total_force += 100

                forces[direction] = total_force

        # Choose direction with the least force
        if forces:
            best_direction = min(forces, key=forces.get)
            best_pos = directions[best_direction]
            if self.is_position_valid(best_pos):
                self.model.grid.move_agent(self, best_pos)
                self.update_visited_positions(best_pos)
                return True
        return False

    def calculate_wall_distance(self, pos):
        walls = [(x, y) for x in range(self.model.grid.width) for y in range(self.model.grid.height)
                 if not self.model.grid.is_cell_empty((x, y))]

        return min([self.calculate_distance(pos, wall) for wall in walls])

    def escape_wall(self):
        escape_directions = [
            (self.pos[0] + 1, self.pos[1]),  # right
            (self.pos[0] - 1, self.pos[1]),  # left
            (self.pos[0], self.pos[1] + 1),  # up
            (self.pos[0], self.pos[1] - 1)  # down
        ]

        # Rank directions by distance from walls
        valid_positions = [(pos, self.calculate_wall_distance(pos)) for pos in escape_directions if
                           self.is_position_valid(pos)]
        valid_positions.sort(key=lambda x: x[1], reverse=True)  # Prioritize positions further from walls

        for new_pos, _ in valid_positions:
            if new_pos not in self.visited_positions:
                self.model.grid.move_agent(self, new_pos)
                self.update_visited_positions(new_pos)
                return

    def get_next_position(self, dx, dy):
        if dy == 29:
            if dx < 15:
                return dx+1, dy
            return dx-1, dy
        if self.is_position_valid((dx, dy + 1)):
            return dx, dy+1
        elif self.is_position_valid((dx + 1, dy)):
            return dx + 1, dy
        elif self.is_position_valid((dx - 1, dy)):
            return dx - 1, dy
        return dx, dy
        # if abs(dx) > abs(dy):
        #     return (self.pos[0] + (1 if dx > 0 else -1), self.pos[1])
        # return (self.pos[0], self.pos[1] + (1 if dy > 0 else -1))

    def is_position_valid(self, pos):
        return (0 <= pos[0] < self.model.grid.width and
                0 <= pos[1] < self.model.grid.height and
                self.model.grid.is_cell_empty(pos) and
                pos not in [o.pos for o in self.obstacles])

    def update_visited_positions(self, new_pos):
        self.visited_positions.append(new_pos)
        if len(self.visited_positions) > self.memory_limit:
            self.visited_positions.pop(0)

        if new_pos in self.model.visited_counts:
            self.model.visited_counts[new_pos] += 1
        else:
            self.model.visited_counts[new_pos] = 1


class Obstacle(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        pass


class Destination:
    def __init__(self, pos, preset, color):
        self.color = color
        self.preset = preset
        self.pos = pos
