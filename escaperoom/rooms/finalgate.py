
import hashlib
import hmac
from .base import Room, GameState, REQUIRED_TOKENS


class FinalGateRoom(Room):

    def __init__(self, data_dir="data"):
        super().__init__(
            "final",
            "Final token verification",
            #the final gate has no token of its own, "FINAL" is used to store and write its transcript lines
            token_name="FINAL",
            item="final_gate.txt",
            hint="Collect all four tokens (KEYPAD, DNS, SAFE, PID) first, then type \"use gate\".",
            data_dir=data_dir,
            display_name="Final Gate"
        )

    def solve(self, state: GameState):

        # Read the configuration file
        config = {}

        with open(self.data_path(self.item), "r", encoding="utf-8") as file:
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
            "final_gate": "OPEN",
            "msg": message,
            "hmac": digest
            }
