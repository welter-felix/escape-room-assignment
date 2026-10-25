# Cyber Escape Room

A command-line escape-room game where you investigate sample security evidence,
solve four puzzles, and use the resulting tokens to open the final gate.

## Requirements

- Python 3.10 or later
- No third-party Python packages are required

## Run the game

From the project directory, run:

```bash
python escape.py
```

If your system uses `python3` to run Python 3, use:

```bash
python3 escape.py
```

The game starts in the `intro` room, reads evidence files from `data/`, and
writes the game transcript to `run.txt` when the game ends.

You can customize these paths and the starting room with command-line options:

```bash
python escape.py --start soc --data data --transcript run.txt
```

| Option | Default | Description |
| --- | --- | --- |
| `--start` | `intro` | Room to start in: `intro`, `soc`, `dns`, `vault`, `malware`, or `final`. |
| `--data` | `data` | Directory containing the room evidence files. |
| `--transcript` | `run.txt` | File where the game writes its transcript when it ends. |

If `--start` names a room that does not exist, the game displays a message and
starts in `intro` instead. Use `python escape.py --help` to see the command-line
options.

## How to play

Type commands at the `>` prompt. Commands are not case-sensitive. Start with
`help` to see the available commands, then use `look` to see the current room
and its item. Use `inspect <item>` to analyze that item and collect its token.

The puzzle rooms are:

| Room | Evidence file | Investigation |
| --- | --- | --- |
| `soc` | `auth.log` | Find the most active `/24` subnet of failed logins and its busiest IP. |
| `dns` | `dns.cfg` | Follow the token tag and decode the selected hint. |
| `vault` | `vault_dump.txt` | Find the `SAFE{...}` entry with a valid checksum. |
| `malware` | `proc_tree.jsonl` | Trace the process tree to the process that transfers the archive. |
| `final` | `final_gate.txt` | Use the collected puzzle tokens to complete the final verification. |

Collect the `KEYPAD`, `DNS`, `SAFE`, and `PID` tokens, then go to the `final`
room and enter `use gate`.

## Commands

| Command | What it does |
| --- | --- |
| `help` | Lists available commands. |
| `look` | Describes the current room and shows its item, if any. |
| `move <room>` | Moves to a room, for example `move soc`. |
| `inspect <item>` | Solves the current room's puzzle item. |
| `use <item>` | Uses an item in the final room; enter `use gate` to attempt the final verification. |
| `inventory` | Shows collected tokens and which required tokens are missing. |
| `hint` | Shows the current room's hint. |
| `save <filename>.json` | Saves the current room, tokens, and transcripts to a JSON file in the current directory. |
| `load <filename>.json` | Loads a JSON save file from the current directory. |
| `quit` | Ends the game and writes the transcript. |

The transcript is also written when the game ends with Ctrl+C or Ctrl+D.

## Project layout

```text
.
├── data/                    # Evidence and final-gate configuration files
├── escaperoom/
│   ├── commands.py          # Command parsing and handlers
│   ├── engine.py            # Game setup and main input loop
│   ├── transcript.py        # Transcript formatting and writing
│   └── rooms/               # Shared room classes and puzzle implementations
└── escape.py                # Command-line entry point
```
