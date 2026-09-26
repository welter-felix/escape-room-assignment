#First we parse the starting argument. Here I check if they are taken correctly, later on we add logic to it.
import argparse

from escaperoom.engine import start_game

#Command to run 
#python escape.py --start intro --data data --transcript run.txt

parser = argparse.ArgumentParser()
parser.add_argument("--start",required=True)
parser.add_argument("--data",required=True)
parser.add_argument("--transcript",required=True)

args = parser.parse_args()


#this will be used later to determine the starting room
print(args.start)

#file location of the data
print(args.data)

#file to which we write the transcript
print(args.transcript)

start_game(args.start,args.data,args.transcript)