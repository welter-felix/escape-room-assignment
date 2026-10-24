#all the commands of the game
#every command handler gets the same 3 arguments (state, rooms, arg) and returns a list of lines to print
#the handlers do not print themselves, so the engine can print the lines and also write them to the transcript


#splits the user input into the command and its argument, e.g. "Move VAULT" -> ("move", "vault")
def parse_command(text):
    #make lowercase to make sure there is no errors with capital letters
    parts = text.strip().lower().split(maxsplit=1)

    #empty input
    if not parts:
        return None, None

    #only a command without argument, e.g. "look"
    if len(parts) == 1:
        return parts[0], None

    return parts[0], parts[1]


def cmd_help(_state, _rooms, _arg):
    #the list of commands is built from the COMMANDS dictionary, so it is always up to date
    return ["The supported commands are: " + ", ".join(COMMANDS)]


def cmd_move(state, rooms, arg):
    #sanity checks to see if the argument is correct
    if arg is None:
        return ["Please provide a room to go to",
                "Possible rooms are: " + ", ".join(rooms)]

    #check if it is a valid room in our room dict
    if arg not in rooms:
        return ["Not a valid room.",
                "Possible rooms are: " + ", ".join(rooms)]

    if state.current_room == arg:
        return ["You are already in " + arg]

    state.current_room = arg
    return ["Moving to " + arg]


def cmd_look(state, rooms, arg):
    if arg is not None:
        return ["Too many arguments. Usage: \"look\""]

    #this is for removal, only bc we dont have an introroom yet
    if state.current_room not in rooms:
        return ["Current Room: " + state.current_room,
                "There is nothing here yet. Possible rooms are: " + ", ".join(rooms)]

    room = rooms[state.current_room]
    lines = ["Current Room: " + room.name, room.description]
    if room.items:
        lines.append("Items here: " + ", ".join(room.items))
    else:
        lines.append("There are no items here.")
    return lines


def cmd_inspect(state, rooms, arg):
    if arg is None:
        return ["Please provide an item to inspect. Usage: \"inspect <item>\""]

    #get the room we are in, None if it is not a room object (e.g. "intro")
    room = rooms.get(state.current_room)
    if room is None or arg not in room.items:
        return ["There is no item called " + arg + " here. Type \"look\" to see the items."]

    #the room solves its puzzle, stores the token in the state and returns the evidence
    #the final gate raises a ValueError if tokens are missing, we catch it so the game does not crash
    try:
        result = room.solve(state)
    except ValueError as error:
        return [str(error)]

    if result is None:
        return ["Nothing useful was found in " + arg]

    lines = [f"You inspect {arg}..."]
    #here we add every part of the result from the solve function
    for key, value in result.items():
        lines.append(f"{key.upper()}={value}")
    return lines


def cmd_inventory(state, rooms, arg):
    if not state.tokens:
        return ["Your inventory is empty."]

    lines = ["Tokens collected:"]
    for name, token in state.tokens.items():
        lines.append(f"  {name}: {token}")
    return lines


def cmd_use(state, rooms, arg):
    return ["The use command is not implemented yet."]


def cmd_hint(state, rooms, arg):
    return ["The hint command is not implemented yet."]


def cmd_save(state, rooms, arg):
    return ["The save command is not implemented yet."]


def cmd_load(state, rooms, arg):
    return ["The load command is not implemented yet."]


def cmd_quit(state, rooms, arg):
    #the engine checks for "quit" itself and stops the loop after printing this
    return ["[Game] Goodbye."]


#maps each command word to its handler function
COMMANDS = {
    "help": cmd_help,
    "look": cmd_look,
    "move": cmd_move,
    "inspect": cmd_inspect,
    "use": cmd_use,
    "inventory": cmd_inventory,
    "hint": cmd_hint,
    "save": cmd_save,
    "load": cmd_load,
    "quit": cmd_quit,
}
