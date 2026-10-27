import re

from .base import Room, GameState

# The regex accepts a whole line of the form SAFE{a-b-c}, where the spaces may vary:
#   ^ and $        the whole line must be the SAFE block (no text before or after it)
#   \s*            zero or more spaces, allowed around every part
#   SAFE           the literal word
#   \{ and \}      the literal curly braces ("{}" has a special meaning in regex, so they are escaped)
#   (\d+)          a group of one or more digits; the three groups are read later with match.group(1..3)
#   -              the literal dash between the numbers
# Examples: "SAFE { 6-19 - 25 }" matches, "SAFE{5-6-12} maybe" and "partialSAFE{3-4-}garbage" do not.
# re.compile builds the pattern once, instead of again for every line of the file.
SAFE_PATTERN = re.compile(r'^\s*SAFE\s*\{\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*\}\s*$')


class VaultRoom(Room):
    """Find the one SAFE{a-b-c} line in vault_dump.txt whose checksum a + b = c is correct."""

    def __init__(self, data_dir="data"):
        super().__init__("vault", "A noisy dump scrolls past. Somewhere a SAFE{a-b-c} hides.","SAFE", "vault_dump.txt",
                         "Inspect vault_dump.txt. Only one SAFE{a-b-c} line has a valid checksum where a + b = c.",
                         data_dir=data_dir, display_name="Vault Corridor")

    def solve(self, state: GameState):
        """Check each line for the SAFE format and the checksum, and save the first valid one as the SAFE token."""

        with open(self.data_path(self.item)) as f:
            # Read the file line by line.
            for line in f:
                # Step 1: does the line have the SAFE{a-b-c} format?
                match = SAFE_PATTERN.search(line)
                if match:
                    # Step 2: the checksum. The groups are strings, so they are converted to int first
                    # (otherwise "6" + "19" would be "619").
                    if int(match.group(1)) + int(match.group(2))==int(match.group(3)):

                        # The token is the three numbers joined with "-", e.g. "6-19-25".
                        safe_token = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

                        # Store the token in GameState so the inventory and the final gate can use it.
                        state.tokens["SAFE"] = safe_token

                        # Return the evidence. Only one line is valid, so we can stop at the first one.
                        return {
                            "summary": [
                                "[Room Vault] Scanning dump...",
                                f"Found candidate: {line.rstrip()}",
                                f"Checksum: {match.group(1)}+{match.group(2)}={match.group(3)} (OK)",
                            ],
                            
                            "token": safe_token,
                            # The transcript wants the matched line in quotes, e.g. MATCH="SAFE { 6-19 - 25 }".
                            "match": "\"" + line.rstrip("\n") + "\"",
                            "check": f"{match.group(1)}+{match.group(2)}={match.group(3)}"
                        }

        # No line had both the right format and a correct checksum.
        return None
