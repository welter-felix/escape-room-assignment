

#central engine of the game

#Here I think its best to keep track of all our global variables

    
#List of commands we need to implement : look, move <room>, inspect <item>, use <item>, inventory, hint, save, load, quit.


def start_game(start_room,data,transcript_filename):

    
    print ("[Game] Cyber Escape Room started. Type 'help' for commands.")
    while True:
        command = input("> ") #gets the user's command

        if (command == "help"):
            print("The supported commands are look, move <room>, " \
            "inspect <item>, use <item>, inventory, hint, save, load, quit")
        elif (command=="move"):
            pass
        elif (command == "quit"):
            print(f"[Game] Goodbye. Transcript written to {transcript_filename} ")  
            break
