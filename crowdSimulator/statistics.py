import matplotlib.pyplot as plt
import numpy as np


class Statistics:

    @staticmethod
    def plot_space_frequency(visited_counts, grid_width, grid_height):
        visit_density = np.zeros((grid_width, grid_height))

        for (x, y), count in visited_counts.items():
            visit_density[x, y] = count
        # increase default figure size so plots are more readable in the pygame window
        fig, ax = plt.subplots(figsize=(6, 4))
        cax = ax.imshow(visit_density.T, interpolation='nearest', cmap='viridis')
        fig.colorbar(cax, label='Częstość odwiedzin')
        ax.set_title('Mapa gęstości odwiedzin danego pola przez agentów')
        ax.set_xlabel('Oś X siatki')
        ax.set_ylabel('Oś Y siatki')

        return fig

    @staticmethod
    def plot_collision_history(collision_history):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(collision_history, label="Kolizje w czasie", color="red")
        ax.set_xlabel("Krok symulacji")
        ax.set_ylabel("Liczba prób kolizji")
        ax.set_title("Historia kolizji w czasie")
        ax.legend()
        ax.grid(True)

        return fig

    @staticmethod
    def plot_intruders_by_zone(intruders_history):
        fig, ax = plt.subplots(figsize=(6, 4))

        for zone, history in intruders_history.items():
            ax.plot(history, label=f"Strefa {zone.capitalize()}", linewidth=2)

        ax.set_title("Liczba intruzów w różnych strefach społecznych w czasie")
        ax.set_xlabel("Kroki symulacji")
        ax.set_ylabel("Liczba intruzów")
        ax.legend()
        ax.grid(True)

        return fig
