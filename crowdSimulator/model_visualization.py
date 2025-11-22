import os

import pygame
import random
from param_choice import ParamsChoice
from crowd_model import CrowdModel
from statistics import Statistics
from statistics import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import cv2

class SimulationVisualization:

    def __init__(self):
        self.model = None
        self.grid_size = 30
        self.cell_size = 500 // self.grid_size
        self.agent_colors = {}
        self.plots = []
        self.current_plot_index = 0

        pygame.init()
        # start with a larger default window so plots and figures can be bigger
        self.screen = pygame.display.set_mode((1200, 700))
        pygame.display.set_caption("Crowd Simulation")
        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def draw_agents(self):
        for agent in self.model.schedule.agents:
            color = (208, 168, 52)
            pygame.draw.circle(self.screen, color, (agent.pos[0] * self.cell_size + self.cell_size // 2,
                                                    agent.pos[1] * self.cell_size + self.cell_size // 2),
                               self.cell_size // 3)

            for pos in agent.visited_positions:
                trail_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                trail_color = (*color, 30)
                pygame.draw.circle(trail_surface, trail_color,
                                   (self.cell_size // 2, self.cell_size // 2), self.cell_size // 3)
                self.screen.blit(trail_surface, (pos[0] * self.cell_size, pos[1] * self.cell_size))

    def draw_objectives(self):
        for obj in self.model.destinations:
            color = obj.color
            pygame.draw.rect(self.screen, color, (obj.pos[0] * self.cell_size, obj.pos[1] * self.cell_size,
                                                  self.cell_size, self.cell_size))

    def draw_obstacles(self):
        color = (128, 128, 128)
        s = self.cell_size
        n = self.grid_size

        for x in range(n):
            for y in range(n):
                if x < y and x < n - y - 1:
                    pygame.draw.rect(self.screen, color, (x * s, y * s, s, s))
                elif x > y and x > n - y - 1:
                    pygame.draw.rect(self.screen, color, (x * s, y * s, s, s))

    def draw_button(self, text, rect, color):
        pygame.draw.rect(self.screen, color, rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def menu(self):
        running = True

        logo_rect = pygame.Rect(10, 30, 480, 380)
        logo_path = 'crowdSimulator/assets/HourglassTitle.png'
        logo_image = pygame.image.load(logo_path)
        logo_image = pygame.transform.scale(logo_image, (logo_rect.width, logo_rect.height))

        while running:
            self.screen.fill((230, 230, 230))
            self.screen.blit(logo_image, (logo_rect.x, logo_rect.y))

            start_rect = pygame.Rect(120, logo_rect.bottom + 20, 270, 50)

            self.draw_button("Start visualization", start_rect, (208, 168, 52))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos):
                        return "Start"

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        scenario = self.menu()
        self.run_scenario(scenario)

    def run_scenario(self, scenario):
        running = True

        params = ParamsChoice()
        directory = f"crowdSimulator/presets/{params.menu()}"
        self.model = CrowdModel(directory, scenario)

        window_width = 1200
        window_height = 700
        self.screen = pygame.display.set_mode((window_width, window_height))
        sim_width = window_width // 2
        sim_height = window_height
        self.cell_size = sim_width // self.grid_size
        pygame.display.flip()

        video_path = "crowdSimulator/assets/CrowdSimulation.mp4"
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 1))

        for agent in self.model.schedule.agents:
            self.agent_colors[agent.unique_id] = (0,150,255)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            sim_surface = pygame.Surface((sim_width, sim_height))
            sim_surface.fill((255, 255, 255))
            self.screen.blit(sim_surface, (0, 0))

            self.draw_grid()
            self.draw_objectives()
            self.draw_agents()
            self.draw_obstacles()

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                ret, frame = cap.read()

            frame = cv2.flip(frame, 0)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # resize video frame to match the simulation area
            frame = cv2.resize(frame, (sim_width, sim_height))
            frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            # blit the video/frame to the right half of the window
            self.screen.blit(frame_surface, (sim_width, 0))

            pygame.display.flip()
            self.clock.tick(900)

            self.model.step()
            self.model.count_intruders()

            if random.randint(1, 20) >= 17:
                self.model.spawn_agent()

            if all(not agent.has_moved for agent in self.model.schedule.agents):
                running = False

        cap.release()
        self.show_statistics_in_pygame()
        pygame.quit()

    def show_statistics_in_pygame(self):
        stats = Statistics()

        fig1 = stats.plot_space_frequency(self.model.visited_counts, self.model.grid.width,
                                                     self.model.grid.height)
        fig2 = stats.plot_collision_history(self.model.collision_history)
        fig3 = stats.plot_intruders_by_zone(self.model.intruders_history)
        self.add_plot(fig1)
        self.add_plot(fig2)
        self.add_plot(fig3)

        self.show_plots()

    def figure_to_surface(self, fig):

        canvas = FigureCanvas(fig)
        canvas.draw()
        width, height = canvas.get_width_height()
        buf = canvas.buffer_rgba()
        surface = pygame.image.frombuffer(buf, (width, height), "RGBA")

        return surface

    def add_plot(self, fig):
        surface = self.figure_to_surface(fig)
        # scale plot surface down if it's larger than the window
        win_w, win_h = self.screen.get_size()
        surf_w, surf_h = surface.get_size()
        max_w = win_w - 40
        max_h = win_h - 40
        scale = min(1.0, float(max_w) / surf_w, float(max_h) / surf_h)
        if scale < 1.0:
            new_size = (int(surf_w * scale), int(surf_h * scale))
            surface = pygame.transform.smoothscale(surface, new_size)

        self.plots.append(surface)

    def show_plots(self):
        running = True

        while running:
            self.screen.fill((255, 255, 255))

            if self.plots:
                plot_surface = self.plots[self.current_plot_index]
                win_w, win_h = self.screen.get_size()
                plot_rect = plot_surface.get_rect(center=(win_w // 2, win_h // 2))
                self.screen.blit(plot_surface, plot_rect.topleft)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.current_plot_index = (self.current_plot_index + 1) % len(self.plots)
                    if event.key == pygame.K_LEFT:
                        self.current_plot_index = (self.current_plot_index - 1) % len(self.plots)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
