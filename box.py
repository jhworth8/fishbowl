import pygame
import math

# Initialize pygame
pygame.init()

# Screen dimensions
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Yellow Ball in Rotating Tesseract Projection")

# Colors
yellow = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)

# Ball properties
ball_radius = 15  # Slightly smaller ball
ball_pos = [width // 2, height // 2]
ball_velocity = [3, 2]

# Tesseract properties
tesseract_size = 150  # Reduced size
tesseract_center = [width // 2, height // 2]
tesseract_rotation_angle = 0
tesseract_rotation_speed = 0.3  # Slower rotation

clock = pygame.time.Clock()

def rotate_point(point, center, angle_degrees):
    """Rotates a point around a center by a given angle in degrees."""
    angle_radians = math.radians(angle_degrees)
    cos_theta = math.cos(angle_radians)
    sin_theta = math.sin(angle_radians)
    x, y = point[0] - center[0], point[1] - center[1]
    new_x = x * cos_theta - y * sin_theta + center[0]
    new_y = x * sin_theta + y * cos_theta + center[1]
    return [new_x, new_y]

def draw_rotated_tesseract(surface, color, center, size, angle):
    """Draws a rotated 2D projection of a tesseract."""
    half_size = size // 2
    # Define vertices of the 2D tesseract projection (nested squares)
    vertices_2d = [
        [-half_size, -half_size],  # 0 - outer square
        [half_size, -half_size],   # 1
        [half_size, half_size],    # 2
        [-half_size, half_size],   # 3
        [-half_size/2, -half_size/2], # 4 - inner square, scaled down
        [half_size/2, -half_size/2],  # 5
        [half_size/2, half_size/2],   # 6
        [-half_size/2, half_size/2]   # 7
    ]

    rotated_vertices = [rotate_point([v[0] + center[0], v[1] + center[1]], center, angle) for v in vertices_2d]

    # Define edges - connections between vertices to form tesseract projection
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),         # Outer square
        (4, 5), (5, 6), (6, 7), (7, 4),         # Inner square
        (0, 4), (1, 5), (2, 6), (3, 7)          # Connections between squares
    ]

    for start_index, end_index in edges:
        pygame.draw.line(surface, color, rotated_vertices[start_index], rotated_vertices[end_index], 2)


def check_collision_tesseract(ball_pos, ball_radius, tesseract_center, tesseract_size, angle):
    """Checks for collision between the ball and the rotated tesseract projection."""
    half_size = tesseract_size / 2
    vertices_2d_unrotated = [
        [-half_size, -half_size],  # 0 - outer square
        [half_size, -half_size],   # 1
        [half_size, half_size],    # 2
        [-half_size, half_size],   # 3
        [-half_size/2, -half_size/2], # 4 - inner square, scaled down
        [half_size/2, -half_size/2],  # 5
        [half_size/2, half_size/2],   # 6
        [-half_size/2, half_size/2]   # 7
    ]
    rotated_vertices = [rotate_point([v[0] + tesseract_center[0], v[1] + tesseract_center[1]], tesseract_center, angle) for v in vertices_2d_unrotated]

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),         # Outer square
        (4, 5), (5, 6), (6, 7), (7, 4),         # Inner square
        (0, 4), (1, 5), (2, 6), (3, 7)          # Connections between squares
    ]

    for start_index, end_index in edges:
        start_point = rotated_vertices[start_index]
        end_point = rotated_vertices[end_index]

        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]

        segment_length_sq = dx**2 + dy**2
        if segment_length_sq == 0:
            continue # Line segment is just a point

        px = start_point[0] - ball_pos[0]
        py = start_point[1] - ball_pos[1]

        t = - (px * dx + py * dy) / segment_length_sq
        t = max(0, min(1, t)) # Clamp t to be within the segment [0, 1]

        closest_point_x = start_point[0] + t * dx
        closest_point_y = start_point[1] + t * dy

        distance_sq = (ball_pos[0] - closest_point_x)**2 + (ball_pos[1] - closest_point_y)**2

        if distance_sq <= ball_radius**2:
            return True, [dx, dy], [closest_point_x, closest_point_y] # Collision detected, edge vector, closest point

    return False, None, None # No collision


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the ball
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]

    # Rotate the tesseract
    tesseract_rotation_angle += tesseract_rotation_speed
    if tesseract_rotation_angle >= 360:
        tesseract_rotation_angle -= 360

    # Collision detection with screen boundaries (fallback - less restrictive)
    if ball_pos[0] + ball_radius > width or ball_pos[0] - ball_radius < 0:
        ball_velocity[0] = -ball_velocity[0]
    if ball_pos[1] + ball_radius > height or ball_pos[1] - ball_radius < 0:
        ball_velocity[1] = -ball_velocity[1]


    # Collision detection with rotating tesseract projection
    collision, edge_vector, collision_point = check_collision_tesseract(ball_pos, ball_radius, tesseract_center, tesseract_size, tesseract_rotation_angle)
    if collision:
        # Calculate normal vector of the edge
        edge_normal = [-edge_vector[1], edge_vector[0]] # 90 degree rotation to get normal
        norm = math.sqrt(edge_normal[0]**2 + edge_normal[1]**2)
        if norm != 0:
            edge_normal = [edge_normal[0]/norm, edge_normal[1]/norm] # Normalize

        # Reflect velocity vector
        dot_product = ball_velocity[0] * edge_normal[0] + ball_velocity[1] * edge_normal[1]
        ball_velocity[0] -= 2 * dot_product * edge_normal[0]
        ball_velocity[1] -= 2 * dot_product * edge_normal[1]

        # Slightly move ball out of collision to prevent sticking.
        push_out_factor = ball_radius - math.sqrt((ball_pos[0] - collision_point[0])**2 + (ball_pos[1] - collision_point[1])**2)
        ball_pos[0] += edge_normal[0] * push_out_factor * 1.1 # small factor to avoid re-collision in next frame
        ball_pos[1] += edge_normal[1] * push_out_factor * 1.1


    # Drawing
    screen.fill(black)
    draw_rotated_tesseract(screen, gray, tesseract_center, tesseract_size, tesseract_rotation_angle)
    pygame.draw.circle(screen, yellow, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    pygame.display.flip()

    clock.tick(60) # Limit frame rate to 60 FPS

pygame.quit()