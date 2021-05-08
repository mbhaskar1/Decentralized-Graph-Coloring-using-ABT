import pygame
import pygame.gfxdraw
import math
from math import cos, sin

WINDOW_OUTLINE = 25

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


def draw_arrow(screen, pos1, pos2, color=BLACK, width=10):
    draw_line(screen, pos1, pos2, color, width)
    magnitude = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
    direction = ((pos2[0] - pos1[0]) / magnitude, (pos2[1] - pos1[1]) / magnitude)
    perpendicular = (direction[1], -direction[0])
    base = (pos2[0] - 3 * direction[0] * width, pos2[1] - 3 * direction[1] * width)
    point1 = (base[0] + 1.2 * perpendicular[0] * width, base[1] + 1.2 * perpendicular[1] * width)
    point2 = (base[0] - 1.2 * perpendicular[0] * width, base[1] - 1.2 * perpendicular[1] * width)

    pygame.gfxdraw.aapolygon(screen, [pos2, point1, point2], color)
    pygame.gfxdraw.filled_polygon(screen, [pos2, point1, point2], color)


def draw_node(screen, center, radius=50, width=5, outline_color=BLACK, interior_color=WHITE, interior_func=None,
              args=None):
    draw_filled_circle(screen, center, radius, interior_color, outline_color=outline_color, width=width)

    if interior_func:
        if args is None:
            args = []
        interior_func(screen, center, radius, outline_color, args)


def draw_graph(identifier, screen, graph_matrix, center, width, height, rel_positions=None,
               outline_color=BLACK, outline_thickness=5,
               node_func=draw_node, node_func_args=None, node_fun_args_per_agent=None):
    num_objects = len(graph_matrix)
    if node_func_args and 'radius' in node_func_args:
        node_radii = node_func_args['radius']
    else:
        node_radii = 50
    width -= node_radii * 2 + WINDOW_OUTLINE * 2
    height -= node_radii * 2 + WINDOW_OUTLINE * 2
    if rel_positions:
        rel_max = (max(pos[0] for pos in rel_positions), max(pos[1] for pos in rel_positions))
        rel_min = (min(pos[0] for pos in rel_positions), min(pos[1] for pos in rel_positions))
        rel_center = ((rel_max[0] + rel_min[0]) / 2, (rel_max[1] + rel_min[1]) / 2)
        rel_width = rel_max[0] - rel_min[0]
        rel_height = rel_max[1] - rel_min[1]
        if (width / rel_width) * rel_height <= height:
            scale = width / rel_width
        else:
            scale = height / rel_height
        positions = rel_positions
        for i in range(len(positions)):
            pos = positions[i]
            positions[i] = (
                (pos[0] - rel_center[0]) * scale + center[0],
                (pos[1] - rel_center[1]) * scale + center[1]
            )
    else:
        positions = get_polygon_points(num_objects, center, min(width, height) / 2 - node_radii)
    for i in range(num_objects):
        for j in range(i + 1, num_objects):
            if graph_matrix[i][j]:
                draw_line(screen, positions[i], positions[j], outline_color, outline_thickness)
    for i in range(num_objects):
        if node_func_args:
            if node_fun_args_per_agent:
                node_func(screen, positions[i], **node_func_args, **(node_fun_args_per_agent[i]))
            else:
                node_func(screen, positions[i], **node_func_args)
        else:
            if node_fun_args_per_agent:
                node_func(screen, positions[i], **(node_fun_args_per_agent[i]))
            else:
                node_func(screen, positions[i])


def draw_csp_graph(identifier, screen, graph_matrix, node_colors, center, width, height, rel_positions=None,
                   node_background_color=WHITE, outline_color=BLACK, outline_thickness=5, ID=None):
    draw_graph(identifier, screen, graph_matrix, center, width, height, rel_positions=rel_positions,
               outline_color=outline_color, outline_thickness=outline_thickness, node_func=draw_csp_node,
               node_func_args={'interior_color': node_background_color},
               node_fun_args_per_agent=[{'colors': node_colors[i]} for i in range(len(node_colors))])


def draw_csp_node(screen, center, colors=None, radius=50, width=5, outline_color=BLACK, interior_color=WHITE):
    if colors is None:
        colors = [0]
    if len(colors) == 1:
        if colors[0] == -1:
            draw_node(screen, center, radius=radius, width=width,
                      outline_color=outline_color, interior_color=BLACK)
        else:
            draw_node(screen, center, radius=radius, width=width,
                      outline_color=outline_color, interior_color=COLORS[colors[0]])
    else:
        draw_node(screen, center, radius=radius, width=width,
                  outline_color=outline_color, interior_color=interior_color,
                  interior_func=csp_node_interior, args=colors)


# args is color indices
def csp_node_interior(screen, center, radius, color, args):
    num_sides = len(args)
    polygon = get_polygon_points(num_sides, center, radius / 2)
    for i in range(num_sides):
        draw_filled_circle(screen, polygon[i], radius / 5, COLORS[args[i]])


def draw_filled_polygon(screen, points, color):
    for i in range(len(points)):
        points[i][0] = round(points[i][0])
        points[i][1] = round(points[i][1])
    pygame.gfxdraw.aapolygon(screen, points, color)
    pygame.gfxdraw.filled_polygon(screen, points, color)


def draw_filled_circle(screen, center, radius, interior_color, outline_color=BLACK, width=0):
    radius = round(radius)
    x = round(center[0])
    y = round(center[1])
    pygame.gfxdraw.aacircle(screen, x, y, radius, outline_color)
    pygame.gfxdraw.filled_circle(screen, x, y, radius, outline_color)
    pygame.gfxdraw.aacircle(screen, x, y, radius - width, interior_color)
    pygame.gfxdraw.filled_circle(screen, x, y, radius - width, interior_color)


def draw_line(screen, pos1, pos2, color, width):
    # https://stackoverflow.com/a/30599392
    center = ((pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2)

    magnitude = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
    angle = math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])
    line_length = magnitude - 3 * width

    ul = (center[0] + (line_length / 2.) * cos(angle) - (width / 2.) * sin(angle),
          center[1] + (width / 2.) * cos(angle) + (line_length / 2.) * sin(angle))
    ur = (center[0] - (line_length / 2.) * cos(angle) - (width / 2.) * sin(angle),
          center[1] + (width / 2.) * cos(angle) - (line_length / 2.) * sin(angle))
    bl = (center[0] + (line_length / 2.) * cos(angle) + (width / 2.) * sin(angle),
          center[1] - (width / 2.) * cos(angle) + (line_length / 2.) * sin(angle))
    br = (center[0] - (line_length / 2.) * cos(angle) + (width / 2.) * sin(angle),
          center[1] - (width / 2.) * cos(angle) - (line_length / 2.) * sin(angle))

    pygame.gfxdraw.aapolygon(screen, (ul, ur, br, bl), color)
    pygame.gfxdraw.filled_polygon(screen, (ul, ur, br, bl), color)


def get_polygon_points(num_sides, center, radius, rotation=0):
    theta = 2 * math.pi / num_sides

    points = [
        (radius * math.sin(theta * i + rotation) + center[0],
         -radius * math.cos(theta * i + rotation) + center[1])
        for i in range(num_sides)
    ]

    return points
