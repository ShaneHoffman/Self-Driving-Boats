![boat](https://user-images.githubusercontent.com/90718732/136070106-d3728f3f-570c-4491-b069-7d83bd6e54d3.JPG)
# Boat-AI

This project was my adventure into AI. I started off by creating a simple boat driving game using only a graphics library (Pygame).
The physics were written by me with the help of this resource: https://github.com/maximryzhov/pygame-car-tutorial/blob/master/game.py.

After I built the game, I wanted to add AI, and have the boats teach themselves how to navigate the course. I decided to use NEAT, more information can
be found here: https://neat-python.readthedocs.io/en/latest/. The premise is survival of the fittest. Each boat is given a score and the higher scoring boats
survive. I also created invisble checkpoints that rewarded a boat for reaching there.

Each boat in the generation has a set of rays that tells the boat a set of distances. This is the only information the boats recieve. Based off this they decide wether
to go straight, turn left or right. 

If you want to test it out for yourself, download the repo, install the necessary packages (NEAT and pygame), and then run main.py to start.

# TO-DO
  - Add new courses or let a user create their own course
  - Display the best score/laps not the overall amount
