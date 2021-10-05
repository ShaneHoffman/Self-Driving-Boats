import pygame
import neat
import os
import sys
from boat import Boat
from profiler import Profiler

pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Game():
    FPS = 60
    START_X, START_Y = 850, 850
    BOAT_WIDTH, BOAT_HEIGHT = 30, 72
    FINISH_X, FINISH_Y = 850, 800
    FINISH_WIDTH, FINISH_HEIGHT = 16, 102
    CHECK1_X, CHECK1_Y = 854, 668
    CHECK2_X, CHECK2_Y = 984, 168
    CHECK_WIDTH = 2
    CHECK1_HEIGHT, CHECK2_HEIGHT = 106, 114
    # RAY_ANGLES = [80, 40, 0, -40, -80]
    RAY_ANGLES = [60, 30, 0, -30, -60]
    # Boat 1 scale is 40 x 80
    # Boat 2 is 5 x 12

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.WIN = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Boat Physics")

        # Load background
        OCEAN_IMAGE = pygame.image.load(os.path.join("Assets", "Ocean-1.png")).convert_alpha()
        self.ocean = pygame.transform.scale(OCEAN_IMAGE, (self.width, self.height))
        COURSE_1_IMAGE = pygame.image.load(os.path.join("Assets", "Course-1-2.png")).convert_alpha()
        self.course_1 = pygame.transform.scale(COURSE_1_IMAGE, (self.width, self.height))
        self.course_1_mask = pygame.mask.from_surface(self.course_1)

        # Load finish line and check points
        FINISH_IMAGE = pygame.image.load(os.path.join("Assets", "Finish-Line.png")).convert_alpha()
        self.finish = pygame.transform.scale(FINISH_IMAGE, (self.FINISH_WIDTH, self.FINISH_HEIGHT))
        self.finish_rect = pygame.Rect(self.FINISH_X, self.FINISH_Y, self.FINISH_WIDTH, self.FINISH_HEIGHT)
        self.checkpoint1 = pygame.Rect(self.CHECK1_X, self.CHECK1_Y, self.CHECK_WIDTH, self.CHECK1_HEIGHT)
        self.checkpoint2 = pygame.Rect(self.CHECK2_X, self.CHECK2_Y, self.CHECK_WIDTH, self.CHECK2_HEIGHT)

        # Score
        self.laps = 0

    # Draws the window: background, course, updated boat, etc...
    def draw_window(self, boats):
        self.WIN.blit(self.ocean, (0, 0))
        self.WIN.blit(self.course_1, (0, 0))
        self.WIN.blit(self.finish, (self.FINISH_X, self.FINISH_Y))

        # Shows check points
        # pygame.draw.rect(self.WIN, WHITE, self.checkpoint1)
        # pygame.draw.rect(self.WIN, WHITE, self.checkpoint2)

        # Used for checking course mask
        # course_mask = pygame.mask.from_surface(self.course_1)
        # self.WIN.blit(course_mask.to_surface(), (0, 0))

        for boat in boats:
            boat_rect = boat.rotated_image.get_rect()
            self.WIN.blit(boat.rotated_image, boat.position - (boat_rect.width / 2, boat_rect.height / 2))
            for ray_coord in boat.ray_coords:
                pygame.draw.line(self.WIN, WHITE, boat.position, ray_coord, 1)

        # Used for checking boat mask
        # mask = boat.get_mask()
        # self.WIN.blit(mask.to_surface(), boat.position - (boat_rect.width / 2, boat_rect.height / 2))

        font = pygame.font.SysFont('comicsans', 32)
        text = font.render('Laps: ' + str(self.laps), 1, (255, 255, 0))
        self.WIN.blit(text, (10, 10))


        pygame.display.update()

    # Handles input from user to control the boats speed and direction
    def boat_movement(self, boat, dt, direction):
        if 1 in direction: # UP
            if boat.velocity.x < 0:
                boat.acceleration = boat.DECELERATION
            elif boat.acceleration < 0:
                boat.acceleration = 0
            else:
                boat.acceleration += 1 * dt
        elif 2 in direction: # DOWN
            if boat.velocity.x > 0:
                boat.acceleration = -boat.DECELERATION
            elif boat.acceleration > 0:
                boat.acceleration = 0
            else:
                boat.acceleration -= 1 * dt
        else:
            # Slow the boat when no acceleration forwards or backwards
            if boat.velocity.x > dt * boat.SLOWDOWN:
                boat.acceleration = -boat.SLOWDOWN
            elif boat.velocity.x < -dt * boat.SLOWDOWN:
                boat.acceleration = boat.SLOWDOWN
            else:
                boat.acceleration = -boat.velocity.x / dt

        if 3 in direction and 4 in direction:
            boat.steering = 0
        elif 3 in direction: # LEFT
            boat.steering += 30 * dt
        elif 4 in direction: # RIGHT
            boat.steering -= 30 * dt
        else:
            boat.steering = 0

        # Acceleration and steering limits
        # boat.acceleration = max(-boat.ACCELERATION_LIMIT, min(boat.acceleration, boat.ACCELERATION_LIMIT))
        boat.steering = max(-boat.ROTATION_ANGLE, min(boat.steering, boat.ROTATION_ANGLE))

    # Checks for collisions with our boat and the course
    def course_collisions(self, boat):
        boat_mask = boat.get_mask()
        boat_rect = boat.rotated_image.get_rect()
        offset = (round(boat.position.x - boat_rect.width / 2), round(boat.position.y - boat_rect.height / 2))
        collide_point = self.course_1_mask.overlap(boat_mask, offset)
        if collide_point:
            return True
        return False

    # Checks for finish line and check point collisions
    def finish_collisions(self, boat, ge):
        boat_rect = boat.get_rect()
        if boat_rect.colliderect(self.finish_rect):
            if len(boat.checks) == 2 and boat.checks[0] == 1 and boat.checks[1] == 2:
                for g in ge:
                    g.fitness += 1000
                self.laps += 1
            boat.checks.clear()

        if boat_rect.colliderect(self.checkpoint1):
            if 1 not in boat.checks:
                for g in ge:
                    g.fitness += 200
                boat.checks.append(1)

        if boat_rect.colliderect(self.checkpoint2):
            if 2 not in boat.checks:
                for g in ge:
                    g.fitness += 200
                boat.checks.append(2)

    def construct_rays(self, boat):
        boat.rays.clear()
        boat.ray_coords.clear()
        for angle in self.RAY_ANGLES:
            boat.ray_casting(self.course_1_mask, angle)
    
    # Initilizes clock and starts the main game loop
    def main(self, genomes, config):
        nets = []
        ge = []
        boats = []

        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            boats.append(Boat(os.path.join("Assets", "Boat-2.png"), 
                self.START_X, self.START_Y, self.BOAT_HEIGHT, self.BOAT_WIDTH))
            g.fitness = 0
            ge.append(g)

        clock = pygame.time.Clock()
        profiler = Profiler()
        run = True
        while run:
            dt = self.width / 50000 # acceleration constant (default: clock.get_time() / 1000)
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LCTRL:
                        profiler.toggle()

            if len(boats) == 0:
                run = False
                break
            
            for boat in boats:
                self.construct_rays(boat)

            # Draw course and boats
            self.draw_window(boats)

            for x, boat in enumerate(boats):
                output = nets[x].activate(boat.get_distances())

                if output[0] > 0.55:
                    self.boat_movement(boat, dt, (3, 1))
                if output[1] > 0.55:
                    self.boat_movement(boat, dt, (4, 1))
                if output[0] <= 0.55 and output[1] <= 0.55:
                    self.boat_movement(boat, dt, (1, 0))

                boat.update(dt)

                # On collision with a boundary
                if self.course_collisions(boat):
                    boats.pop(x)
                    nets.pop(x)
                    ge.pop(x)   
                else:
                    ge[x].fitness += 1

                self.finish_collisions(boat, ge)