from dataclasses import dataclass, field

#the tokens the player needs to open the final gate, used by the commands and the final gate room
REQUIRED_TOKENS = ["KEYPAD", "DNS", "SAFE", "PID"]

@dataclass
class GameState:
    #the current room of the game
    current_room: str = "intro"

    #the items collected by the user
    inventory: set[str] = field(default_factory=set)

    #the tokens obtained from the rooms
    tokens: dict[str, str] = field(default_factory=dict)

    #returns the names of the required tokens we don't have yet, an empty list if we have all of them
    def missing_tokens(self):
        missing = []
        for token in REQUIRED_TOKENS:
            if token not in self.tokens:
                missing.append(token)
        return missing

class Room:
    #Base class for all the rooms
    def __init__(self, name: str, description: str, items: list[str] | None = None, hint: str = "No hint for this room."):
        self.name= name
        self.description = description
        #the items the player can inspect in this room (e.g. auth.log)
        #optional, so rooms that don't pass any items yet still work
        self.items = items if items is not None else []
        #the hint shown with the "hint" command, optional like the items
        self.hint = hint
         
    #each room implements its own solution
    def solve(self, state: GameState):
        raise NotImplementedError