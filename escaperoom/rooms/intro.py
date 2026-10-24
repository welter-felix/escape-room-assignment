from .base import Room, GameState


class IntroRoom(Room):
    #the room the player starts in, it only explains the mission and has no puzzle or token

    def __init__(self):
        super().__init__(
            "intro",
            "You wake up in a dark server room. The doors are locked and a terminal blinks in front of you:\n"
            "  \"Intruders breached this network. Four rooms hide the evidence of the attack.\n"
            "   Analyse the logs in the soc, decode the dns config, crack the vault and\n"
            "   trace the malware. Each room gives you a token. Bring all four tokens to\n"
            "   the final gate to escape.\"",
            hint="Type \"move <room>\" to go to a room. Start with soc, dns, vault or malware.",
        )

    #the intro has no items, so the engine never asks it to solve anything
    def solve(self, state: GameState):
        return None
