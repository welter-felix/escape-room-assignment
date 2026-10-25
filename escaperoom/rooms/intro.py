from .base import Room, GameState


class IntroRoom(Room):
    """Welcome the player and explain the escape-room mission."""

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

    def solve(self, state: GameState):
        """Return no result because the intro contains no puzzle or token."""
        return None
