import os
from dataclasses import dataclass, field

#the tokens the player needs to open the final gate, used by the commands and the final gate room
REQUIRED_TOKENS = ["KEYPAD", "DNS", "SAFE", "PID"]

@dataclass
class GameState:
    #the current room of the game
    current_room: str = "intro"

    #the tokens obtained from the rooms, we use this also as inventory
    tokens: dict[str, str] = field(default_factory=dict)

    transcript:dict[str, list[str]] = field(default_factory=dict)
    #returns the names of the required tokens we don't have yet, an empty list if we have all of them
    def missing_tokens(self):
        missing = []
        for token in REQUIRED_TOKENS:
            if token not in self.tokens:
                missing.append(token)
        return missing

class Room:
    #Base class for all the rooms
    def __init__(self, name: str, description: str, token_name: str | None = None, item: str | None = None, hint: str = "No hint for this room.", data_dir: str = "data"):
        self.name= name
        self.description = description
        self.token_name = token_name
        #the item the player can inspect in this room (e.g. auth.log)
        #optional, so rooms that don't pass any items yet still work
        self.item = item
        #the hint shown with the "hint" command, optional like the items
        self.hint = hint
        #the folder with the data files, comes from the --data argument
        self.data_dir = data_dir

    #returns the path of a file in the data folder, os.path.join works with or without a "/" at the end of data_dir
    def data_path(self, filename):
        return os.path.join(self.data_dir, filename)

    #each room implements its own solution
    def solve(self, state: GameState):
        raise NotImplementedError