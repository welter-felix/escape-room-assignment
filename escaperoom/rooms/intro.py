from .base import Room, GameState

class IntroRoom(Room):
    """Welcome the player and explain the escape-room mission."""

    def __init__(self):
        super().__init__(
            "intro",
            "A terminal blinks in the corner. Doors lead to: soc, dns, vault, malware, final.",
            hint="Type \"move <room>\" to go to a room. Start with soc, dns, vault or malware.",
            display_name="Intro Lobby"
        )

    def solve(self, state: GameState):
        """Return no result because the intro contains no puzzle or token."""
        return None
