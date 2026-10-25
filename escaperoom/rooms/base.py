import os
from dataclasses import dataclass, field

# Tokens every puzzle room must provide before the final gate can be opened.
REQUIRED_TOKENS = ["KEYPAD", "DNS", "SAFE", "PID"]


@dataclass
class GameState:
    """Track the player's current room, collected tokens, and room transcripts."""

    current_room: str = "intro"
    tokens: dict[str, str] = field(default_factory=dict)
    transcript: dict[str, list[str]] = field(default_factory=dict)

    def missing_tokens(self):
        """Return the required token names that have not yet been collected."""
        missing = []
        for token in REQUIRED_TOKENS:
            if token not in self.tokens:
                missing.append(token)
        return missing

class Room:
    """Shared configuration and interface for each game room."""

    def __init__(self, name: str, description: str, token_name: str | None = None, item: str | None = None, hint: str = "No hint for this room.", data_dir: str = "data"):
        self.name= name
        self.description = description
        self.token_name = token_name
        # Optional filename for the evidence item associated with this room.
        self.item = item
        # Text shown when the player requests a hint.
        self.hint = hint
        # Directory containing this room's evidence files.
        self.data_dir = data_dir

    def data_path(self, filename):
        """Build the path to a room's evidence file."""
        return os.path.join(self.data_dir, filename)

    def solve(self, state: GameState):
        """Solve the room's puzzle; subclasses must provide the implementation."""
        raise NotImplementedError