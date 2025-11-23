import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from crowd_model import CrowdAgent

class Statistics:

    @staticmethod
    def plot_space_frequency(visited_counts, grid_width, grid_height):
        visit_density = np.zeros((grid_width, grid_height))

        for (x, y), count in visited_counts.items():
            visit_density[x, y] = count

        fig, ax = plt.subplots(figsize=(5, 4))
        cax = ax.imshow(visit_density.T, interpolation='nearest', cmap='viridis')
        fig.colorbar(cax, label='Częstość odwiedzin')
        ax.set_title('Mapa gęstości odwiedzin danego pola przez agentów')
        ax.set_xlabel('Oś X siatki')
        ax.set_ylabel('Oś Y siatki')

        return fig

    @staticmethod
    def plot_collision_history(collision_history):
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(collision_history, label="Kolizje w czasie", color="red")
        ax.set_xlabel("Krok symulacji")
        ax.set_ylabel("Liczba prób kolizji")
        ax.set_title("Historia kolizji w czasie")
        ax.legend()
        ax.grid(True)

        return fig

    @staticmethod
    def plot_intruders_by_zone(intruders_history):
        fig, ax = plt.subplots(figsize=(5, 4))

        for zone, history in intruders_history.items():
            ax.plot(history, label=f"Strefa {zone.capitalize()}", linewidth=2)

        ax.set_title("Liczba intruzów w różnych strefach społecznych w czasie")
        ax.set_xlabel("Kroki symulacji")
        ax.set_ylabel("Liczba intruzów")
        ax.legend()
        ax.grid(True)

        return fig
    
    @staticmethod
    def plot_path_visiting_frequency(visited_counts, grid_width, grid_height, threshold = 5):
        density = np.zeros((grid_width, grid_height))
        for (x, y), count in visited_counts.items():
            density[x, y] = count

        fig, ax = plt.subplots(figsize=(5, 4))
        heat = ax.imshow(density.T, cmap='viridis', interpolation='nearest')

        for x in range(grid_width):
            for y in range(grid_height):
                if density[x, y] >= threshold:
                    if x + 1 < grid_width and density[x+1, y] >= threshold:
                        ax.plot([x, x+1], [y, y], color="white", linewidth=0.5)

                    if y + 1 < grid_height and density[x, y+1] >= threshold:
                        ax.plot([x, x], [y, y+1], color="white", linewidth=0.5)

                    if x + 1 < grid_width and y + 1 < grid_height and density[x+1, y+1] >= threshold:
                        ax.plot([x, x+1], [y, y+1], color="white", linewidth=0.5)

                    if x + 1 < grid_width and y - 1 >= 0 and density[x+1, y-1] >= threshold:
                        ax.plot([x, x+1], [y, y-1], color="white", linewidth=0.5)

        fig.colorbar(heat, label="Częstość odwiedzin")
        ax.set_title("Najczęściej odwiedzane ścieżki")
        ax.set_xlabel("Oś X siatki")
        ax.set_ylabel("Oś Y siatki")

        return fig
    
    @staticmethod
    def plot_most_used_paths(path_counts, grid_width, grid_height):
        path_density = np.zeros((grid_width, grid_height))

        for (start, end), count in path_counts.items():
            x1, y1 = start
            x2, y2 = end
            path_density[x1, y1] += count
            path_density[x2, y2] += count

        fig, ax = plt.subplots(figsize=(5, 4))
        cax = ax.imshow(path_density.T, origin='lower', cmap='inferno', interpolation='nearest')
        fig.colorbar(cax, label='Częstość użycia ścieżki')
        ax.set_title("Najczęściej odwiedzane ścieżki agentów")
        ax.set_xlabel("Oś X siatki")
        ax.set_ylabel("Oś Y siatki")
        ax.grid(False)

        return fig

    @staticmethod
    def plot_wall_clusters(agents, grid_width, grid_height):
        agent_positions = [agent.visited_positions for agent in agents]
        n_agents = len(agents)
        avg_distances = []

        def x_bounds(y):
            mid = grid_height // 2
            if y <= mid:
                offset = y
            else:
                offset = grid_height - 1 - y
            return offset, grid_width - 1 - offset

        active_agents = []
        for t in range(n_agents):
            active_agents.append(agent_positions[t])
            distances = []
            for path in active_agents:
                for x, y in path:
                    x_min, x_max = x_bounds(y)
                    dist_to_wall = min(x - x_min, x_max - x)
                    distances.append(dist_to_wall)
            avg_distance = np.mean(distances) if distances else 0
            avg_distances.append(np.abs(avg_distance))

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(range(n_agents), avg_distances, marker='o', color='blue')
        ax.set_title("Średnia odległość agentów od ściany klepsydry w czasie")
        ax.set_xlabel("Czas [s]")
        ax.set_ylabel("Średnia odległość od ściany")
        ax.grid(True)

        return fig

