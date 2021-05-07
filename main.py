import random
from copy import copy

import pygame
import drawing_utils
from random import randrange
import ctypes


class Agent:
    def __init__(self, index, neighbors, options):
        self.index = index
        self.options = options
        self.neighbors = neighbors
        self.constraints = copy(neighbors)
        self.number = None
        self.agent_view = []
        self.no_goods = []
        self.messages = []

    def message(self, message):
        self.messages.append(message)

    def process_messages(self):
        if self.number is None:
            # Assign self random number
            self.number = random.choice(self.options)
            # Send all neighbors with lower priority current number
            for neighbor in self.neighbors:
                if neighbor.index > self.index:
                    neighbor.message(('ok', (self.index, self.number)))

        # Process received messages
        for message_type, (agent_index, updated_number) in self.messages:
            # Process Ok? Messages
            if message_type == 'ok':
                updated = False
                for i in range(len(self.agent_view)):
                    if self.agent_view[i][0] == agent_index:
                        self.agent_view[i][1] = updated_number
                        updated = True
                        break
                if not updated:
                    self.agent_view.append((agent_index, updated_number))

            if message_type == 'nogood':
                continue
            if message_type == 'no_solution':
                break
            print('error')

    def check_agent_view(self):
        if not self.is_consistent(self.number):
            new_value = None
            for number in self.options:
                if self.is_consistent(number):
                    new_value = number
                    break
            if new_value is None:
                self.backtrack()
            else:
                self.number = new_value
                for neighbor in self.neighbors:
                    if neighbor.index > self.index:
                        neighbor.message(('ok', (self.index, self.number)))

    def backtrack(self):
        # More efficient versions of ABT try to find a minimal no_good here
        no_good = copy(self.agent_view)

        if len(no_good) == 0:
            for agent in self.neighbors:
                agent.message(('no_solution', None))

    def is_consistent(self, number):
        for agent in self.constraints:
            if agent.number == number:
                return False
        for no_good in self.no_goods:
            if set(no_good).issubset({*self.agent_view, self.number}):
                return False
        return True


def main():
    ctypes.windll.user32.SetProcessDPIAware()

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Multi Agent Systems Simulation")
    clock = pygame.time.Clock()

    while True:
        # Lock the framerate at 50 FPS
        clock.tick(2)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.QUIT:
                return

        screen.fill((255, 255, 255))
        graph_matrix = [
            [0, 1, 1, 0, 0, 0],
            [1, 0, 1, 1, 0, 0],
            [1, 1, 0, 1, 1, 0],
            [0, 1, 1, 0, 1, 1],
            [0, 0, 1, 1, 0, 1],
            [0, 0, 0, 1, 1, 0]
        ]
        positions = [
            (0, 0),
            (1, 1),
            (1, -1),
            (3, 1),
            (3, -1),
            (4, 0)
        ]
        drawing_utils.draw_graph(screen, graph_matrix, center=(screen_width/2, screen_height/2),
                                 width=screen_width, height=screen_height,
                                 rel_positions=positions, node_func_args={'radius': 50})
        pygame.display.flip()


if __name__ == "__main__":
    main()