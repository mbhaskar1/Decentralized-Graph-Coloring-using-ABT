import random

import pygame
import drawing_utils
import ctypes

from Agent import Agent


NUM_COLORS = 3
WINDOW_OUTLINE = 25


def main():
    ctypes.windll.user32.SetProcessDPIAware()

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Multi Agent Systems Simulation")
    clock = pygame.time.Clock()

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

    for i in range(len(positions)):
        positions[i] = (positions[i][0], -positions[i][1])

    agents = []
    for i in range(len(graph_matrix)):
        agents.append(Agent(i, list(range(NUM_COLORS)), verbose=True, initial_assignment=0))
    for i in range(len(graph_matrix)):
        neighbors = []
        for j in range(len(graph_matrix)):
            if i != j and graph_matrix[i][j] == 1:
                neighbors.append(agents[j])
        agents[i].set_neighbors(neighbors)

    frame = 0
    while True:
        frame += 1
        # Lock the framerate at 50 FPS
        clock.tick(5)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.QUIT:
                return

        screen.fill((255, 255, 255))
        agents[frame % len(agents)].process_messages()
        drawing_utils.draw_csp_graph('Graph1', screen, graph_matrix, node_colors=[
            [-1] if agent.no_sol else [agent.number] if agent.number is not None else list(range(NUM_COLORS))
            for agent in agents],
                                     center=(screen_width / 2, screen_height / 2),
                                     width=screen_width - WINDOW_OUTLINE * 2, height=screen_height - WINDOW_OUTLINE * 2,
                                     rel_positions=positions)
        pygame.display.flip()


if __name__ == "__main__":
    main()
