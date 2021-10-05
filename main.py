import neat
import os
from controller import Game


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Set up population
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(Game(1800, 1000).main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)