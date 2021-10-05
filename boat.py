import pygame
from pygame.math import Vector2
import math

class Boat(pygame.sprite.Sprite):
    ROTATION_ANGLE = 25
    ACCELERATION_LIMIT = 8
    VELOCITY_LIMIT = 25
    DECELERATION = 8
    SLOWDOWN = 4
    RATIO = 4
    RAY_MAX = 150

    def __init__(self, image_path, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load(image_path).convert_alpha()
        rotated_image = pygame.transform.rotate(image, 90)
        self.image = pygame.transform.scale(rotated_image, (width, height))
        self.rect = self.image.get_rect()
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.length = height
        self.steering = 0
        self.angle = 0
        self.acceleration = 0
        self.last_acceleration = 0
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.checks = []
        self.rays = []
        self.ray_coords = []
        self.distance = 0

    # Apply acceleration to the velocity and override update method
    def update(self, dt):
        begin = (self.position.x, self.position.y)
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.VELOCITY_LIMIT, min(self.velocity.x, self.VELOCITY_LIMIT))

        if self.steering:
            turning_radius = self.length / math.sin(math.radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0
        # Added multiplier by 1.5 to increase turning speed
        self.angle += math.degrees(angular_velocity) * dt * self.RATIO * 1.5
        self.position += self.velocity.rotate(-self.angle) * dt * self.RATIO

        # Update the rotated image
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        end = (self.position.x, self.position.y)
        change_x = end[0] - begin[0]
        change_y = end[1] - begin[1]
        self.distance = change_x + change_y

    # Cast rays in a certain direction from the boat
    def ray_casting(self, course_mask, ray_angle):
        
        x = self.position.x
        y = self.position.y
        ray_len = 0
        while course_mask.get_at((round(x), round(y))) != 1 and ray_len <= self.RAY_MAX:
            ray_len += 4
            x = int(self.position.x + ray_len * math.cos(math.radians(360 - self.angle + ray_angle)))
            y = int(self.position.y + ray_len * math.sin(math.radians(360 - self.angle + ray_angle)))
            if x < 0 or x >= course_mask.get_size()[0]:
                break
            if y < 0 or y >= course_mask.get_size()[1]:
                break

        # Distance formula for a line
        self.rays.append(math.sqrt((self.position.x - x) ** 2 + (self.position.y - y) ** 2))

        self.ray_coords.append((x, y))
    
    def get_distances(self):
        distances = [0] * 5
        for i, ray in enumerate(self.rays):
            distances[i] = ray
        return distances

    def get_rect(self):
        return pygame.Rect(self.position.x - self.rotated_image.get_width() / 2, self.position.y - self.rotated_image.get_height() / 2, 
            self.rotated_image.get_width(), self.rotated_image.get_height())

    def get_mask(self):
        return pygame.mask.from_surface(self.rotated_image)
        