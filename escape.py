print ("[Game] Cyber Escape Room started. Type 'help' for commands.")

while True:
    command = input("> ") #gets the user's command

    if (command == "help"):
        print("The supported commands are look, move <room>, " \
        "inspect <item>, use <item>, inventory, hint, save, load, quit")

    if (command == "quit"):
        print("[Game] Goodbye. Transcript written to run.txt ")  
        break