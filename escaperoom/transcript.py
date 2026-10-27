#everything to do with the transcript file (run.txt)
from escaperoom.rooms.base import REQUIRED_TOKENS

#some keys returned by the rooms have a different name in the transcript
KEY_NAMES = {"malformed": "MALFORMED_SKIPPED"}

#turns the result of a room into the tagged transcript lines, e.g.
#("SAFE", {"token": "6-19-25", "check": "6+19=25"}) -> ["TOKEN[SAFE]=6-19-25", "EVIDENCE[SAFE].CHECK=6+19=25"]
def format_result(token_name, result, state=None):
    lines = []
    #displays the human-readable summary
    summary = result.get("summary", [])
    lines.extend(summary)

    if token_name == "FINAL":
            tokens = ", ".join(
                f"{key}={value}" for key, value in state.tokens.items()
            )
            lines.append(f"Collected tokens: {tokens}")

    for key, value in result.items():
        
        if key == "summary":
            lines.append("")
            continue

        #the final gate has no token of its own, its lines are written without TOKEN[...] or EVIDENCE[...]
        if token_name == "FINAL":
            lines.append(f"{key.upper()}={value}")
            continue
        if key == "token":
            lines.append(f"TOKEN[{token_name}]={value}")
        else:
            #use the transcript name of the key if it has one, otherwise the key itself
            tag = KEY_NAMES.get(key, key).upper()
            lines.append(f"EVIDENCE[{token_name}].{tag}={value}")

    return lines


#writes the transcript file, always in the required order (KEYPAD, DNS, SAFE, PID, FINAL)
#no matter in which order the player solved the rooms. Rooms that are not solved yet are skipped
def write_transcript(state, path):
    with open(path, "w", encoding="utf-8") as file:
        for token_name in REQUIRED_TOKENS + ["FINAL"]:
            if token_name in state.transcript:
                for line in state.transcript[token_name]:
                    file.write(line + "\n")
