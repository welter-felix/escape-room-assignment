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
    def __init__(self, name: str, description: str):
        self.name= name
        self.description = description
         
    #each room implements its own solution
    def solve(self, state: GameState):
        raise NotImplementedError