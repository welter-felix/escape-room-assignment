#First we parse the starting argument. Here I check if they are taken correctly, later on we add logic to it.
import argparse

from escaperoom.engine import start_game

#Command to run 
#python escape.py --start intro --data data --transcript run.txt

parser = argparse.ArgumentParser()
parser.add_argument("--start",default="intro")
parser.add_argument("--data",default="data")
parser.add_argument("--transcript",default="run.txt")

args = parser.parse_args()

start_game(args.start,args.data,args.transcript)
