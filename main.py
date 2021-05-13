import random

import pygame
import drawing_utils
import ctypes

from Agent import Agent
from drawing_utils import GraphMessageAnimation

NUM_COLORS = 2
WINDOW_OUTLINE = 25
EXAMPLE = 2


def main():
    ctypes.windll.user32.SetProcessDPIAware()

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Multi Agent Systems Simulation")
    clock = pygame.time.Clock()

    initial_assignments = None
    if EXAMPLE == 1:
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
        node_radius = 50
    elif EXAMPLE == 2:
        connections = [
            [4, 2],
            [1, 7, 3],
            [2, 10],
            [1, 5],
            [4, 12, 6],
            [5, 11, 7],
            [2, 6, 8],
            [7, 11, 9],
            [8, 16, 10],
            [3, 9],
            [6, 8, 14],
            [5, 24, 22, 13],
            [12, 21, 14],
            [13, 11, 15],
            [14, 17, 16],
            [15, 18, 20, 9],
            [15, 18],
            [17, 16, 19],
            [18, 20],
            [16, 19],
            [22, 13],
            [23, 12, 21],
            [22, 24],
            [23, 12]
        ]
        positions = [
            (280, 420),
            (397, 420),
            (515, 420),
            (260, 340),
            (300, 291),
            (367, 362),
            (397, 389),
            (428, 362),
            (494, 291),
            (534, 340),
            (397, 335),
            (324, 224),
            (364, 187),
            (397, 187),
            (432, 187),
            (470, 224),
            (488, 115),
            (606, 62),
            (614, 106),
            (569, 180),
            (306, 115),
            (188, 62),
            (180, 106),
            (225, 180)
        ]
        graph_matrix = []
        for i in range(len(connections)):
            graph_matrix.append([])
            for j in range(len(connections)):
                if j + 1 in connections[i]:
                    graph_matrix[i].append(1)
                else:
                    graph_matrix[i].append(0)
        node_radius = 25
    if EXAMPLE == 3:
        graph_matrix = [
            [0, 0, 1],
            [0, 0, 1],
            [1, 1, 0]
        ]
        positions = [
            (-1, -1),
            (1, -1),
            (0, 0)
        ]
        node_radius = 50
        initial_assignments = [0, 1, 1]

    agents = []
    for i in range(len(graph_matrix)):
        if initial_assignments is not None:
            agents.append(Agent(i, list(range(NUM_COLORS)), verbose=True, initial_assignment=initial_assignments[i]))
        else:
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

        clock.tick(60)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.QUIT:
                return

        screen.fill((255, 255, 255))
        messages = agents[frame % len(agents)].process_messages()
        times = {}
        for msg in messages:
            message_type = msg['message'][0]
            if message_type == 'indirect':
                message_type = msg['message'][1][1][0]
            source_index = msg['source'].index
            target_index = msg['agent'].index
            if source_index * len(agents) + target_index not in times:
                times[source_index * len(agents) + target_index] = 0
            delay = times[source_index * len(agents) + target_index] * 20
            drawing_utils.add_animation(
                GraphMessageAnimation('Graph1', source_index, target_index, message_type,
                                      callback=lambda agent, message: agent.message(message),
                                      callback_params=[msg['agent'], msg['message']], delay=delay))
            times[source_index * len(agents) + target_index] += 1

        drawing_utils.draw_csp_graph('Graph1', screen, graph_matrix, node_colors=[
            [-1] if agent.no_sol else [agent.number] if agent.number is not None else list(range(NUM_COLORS))
            for agent in agents],
                                     center=(screen_width / 2, screen_height / 2),
                                     width=screen_width - WINDOW_OUTLINE * 2, height=screen_height - WINDOW_OUTLINE * 2,
                                     rel_positions=positions, node_radius=node_radius)
        pygame.display.flip()
        drawing_utils.step()


if __name__ == "__main__":
    main()
