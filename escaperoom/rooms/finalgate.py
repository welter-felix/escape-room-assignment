
import hashlib
import hmac
from .base import Room, GameState, REQUIRED_TOKENS


class FinalGateRoom(Room):

    def __init__(self):
        super().__init__(
            "final",
            "Final token verification",
            ["final_gate.txt"],
            "Collect all four tokens (KEYPAD, DNS, SAFE, PID) first, then type \"use gate\"."
        )

    def solve(self, state: GameState, data_dir="data"):

        # Read the configuration file
        file_path = data_dir + "/final_gate.txt"
        config = {}

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip()

        #configuration values
        group_id = config["group_id"]
        token_order = config["token_order"].replace(",", " ").split()
        secret_key = config["hmac_key"]

        # Checks that all tokens are available
        for token in REQUIRED_TOKENS:
            if token not in state.tokens:
                raise ValueError("Missing token: " + token)

        # Arranging token values in order
        token_values = []

        for token in token_order:
            token_values.append(state.tokens[token])

        # Create the message
        message = group_id + "|" + "-".join(token_values)

        # Calculate HMAC-SHA256
        digest = hmac.new(
            secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        # Return the required transcript lines
        return {
            "transcript_lines": [
                "FINAL_GATE=PENDING",
                "MSG=" + message,
                "HMAC=" + digest
            ]
        }


#to run the room independently, you can use the following code snippet:
###python -m escaperoom.rooms.finalgate
#remove the values in the final_gate.txt file and run the code it will generate the values and put it into the file
