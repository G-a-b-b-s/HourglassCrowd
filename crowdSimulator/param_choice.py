import pygame
import os
import json
import random


class ParamsChoice:
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Select Simulation Parameters")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20)

        self.presets_folder = 'presets'
        self.files = self.load_presets()

    def load_presets(self):
        files = []
        for filename in os.listdir(self.presets_folder):
            if filename.endswith(".json"):
                files.append(filename)
        return files

    def draw_button(self, text, rect, color):
        pygame.draw.rect(self.screen, color, rect)
        label = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(label, (rect.x + 10, rect.y + 10))

    def draw_text(self, text, position):
        label = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(label, position)

    def create_random_params(self):
        params = {
            "num_agents": random.randint(5, 20),
            "num_objectives": len(range(0, 30)),
            "num_obstacles": random.randint(30, 50),
            "randomize_objectives": False,
            "objectives": [
                {"position": [i, 29], "preset": "exit", "color": [0, 0, 128]} for i in range(0, 30)                
            ],
            "randomize_obstacles": True,
            "grid_width": 30,
            "grid_height": 30,
        }

        return params

    def menu(self):
        running = True
        while running:
            self.screen.fill((230, 230, 230))
            self.draw_text("Select Parameters File or Generate New", (50, 50))

            button_rect = pygame.Rect(50, 100, 500, 50)
            self.draw_button("Choose Existing Preset", button_rect, (128, 238, 128))

            random_button_rect = pygame.Rect(50, 200, 500, 50)
            self.draw_button("Generate Random Params", random_button_rect, (240, 128, 128))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        self.screen.fill((230, 230, 230))
                        selected_file = None
                        while selected_file is None:
                            for idx, file in enumerate(self.files):
                                file_rect = pygame.Rect(50, 50 + idx * 50, 500, 40)
                                self.draw_button(file, file_rect, (200, 200, 200))

                            pygame.display.flip()

                            for sub_event in pygame.event.get():
                                if sub_event.type == pygame.QUIT:
                                    pygame.quit()
                                    return None
                                elif sub_event.type == pygame.MOUSEBUTTONDOWN:
                                    for idx, file in enumerate(self.files):
                                        file_rect = pygame.Rect(50, 50 + idx * 50, 500, 40)
                                        if file_rect.collidepoint(sub_event.pos):
                                            return str(file)

                    if random_button_rect.collidepoint(event.pos):
                        random_params = self.create_random_params()
                        random_params_file = "crowdSimulator/presets/random_params.json"
                        with open(random_params_file, "w") as f:
                            json.dump(random_params, f)
                        return "random_params.json"

            pygame.display.flip()
            self.clock.tick(60)
