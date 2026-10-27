# Format room results as tagged transcript lines and write solved rooms to the
# transcript file in the required order, regardless of solve order.
from escaperoom.rooms.base import REQUIRED_TOKENS

# Map room-result keys to their required transcript labels when the names differ.
KEY_NAMES = {"malformed": "MALFORMED_SKIPPED"}

# Convert a room result into its human-readable and tagged transcript lines.
def format_result(token_name, result, state=None):
    lines = []
    # Add the room's readable summary before its tagged result fields.
    summary = result.get("summary", [])
    lines.extend(summary)

    if token_name == "FINAL":
            # Include collected puzzle tokens with the final gate result.
            tokens = ", ".join(
                f"{key}={value}" for key, value in state.tokens.items()
            )
            lines.append(f"Collected tokens: {tokens}")

    for key, value in result.items():
        
        if key == "summary":
            lines.append("")
            continue

        # The final gate has no token of its own, so emit its fields without
        # the TOKEN[...] or EVIDENCE[...] prefixes.
        if token_name == "FINAL":
            lines.append(f"{key.upper()}={value}")
            continue
        if key == "token":
            lines.append(f"TOKEN[{token_name}]={value}")
        else:
            # Use the transcript label override when defined; otherwise use
            # the result key itself.
            tag = KEY_NAMES.get(key, key).upper()
            lines.append(f"EVIDENCE[{token_name}].{tag}={value}")

    return lines

# Write solved room transcripts in required order, skipping unsolved rooms.
def write_transcript(state, path):
    with open(path, "w", encoding="utf-8") as file:
        for token_name in REQUIRED_TOKENS + ["FINAL"]:
            if token_name in state.transcript:
                for line in state.transcript[token_name]:
                    file.write(line + "\n")
