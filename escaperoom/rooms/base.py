from dataclasses import dataclass, field

@dataclass
class GameState:
    #the current room of the game
    current_room: str = "intro"

    #the items collected by the user
    inventory: set[str] = field(default_factory=set)

    #the tokens obtained from the rooms
    tokens: dict[str, str] = field(default_factory=dict)

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