# Set up command-line options so the player can choose how to start the game.
import argparse
import os
import os

from escaperoom.engine import start_game

# Create a parser to read options supplied when running this script.
parser = argparse.ArgumentParser()
# Choose the room to start in, and where to find game data and save the transcript.
parser.add_argument("--start",default="intro")
parser.add_argument("--data",default="data")
parser.add_argument("--transcript",default="run.txt")

# Read the options from the command line.
args = parser.parse_args()

# Stop before the game starts if the data folder does not exist.
if not os.path.isdir(args.data):
    parser.error(f"data folder \"{args.data}\" does not exist")
    
# Start the game using the selected room, data folder, and transcript file.
start_game(args.start,args.data,args.transcript)