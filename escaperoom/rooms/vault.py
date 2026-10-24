#importing regex
import re

from .base import Room, GameState



#  explanation:
#
#We want to accept all Strings resembling this pattern "SAFE{A-B-C}" with the condition that the white spaces may vary
#
#In this regex, I mostly used "\s*" which just means there can be zero or more whitespaces in the expression
#
#The "^" marks the beginning of the expressing and after the "\s*" we check for the word SAFE, meaning if it would not be there, that line would not match
#
#then we check for the curly braces (which is a special character that is why I put a "\" in front of it just to make sure that it is seen as such)
#
#on the next stage I do 2 things, I use "()" which creates a group (so we can access the contents of it later) and with "\d" I specify that the string has to contain digits and with the "+" afterwards I make sure that it can be one or more digits
#
# Then I repeat this process and I mark the end with "$"


#here i use re.compile so that the expression does no have to be compiled for each line
safe_pattern = re.compile(r'^\s*SAFE\s*\{\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*\}\s*$')


class VaultRoom(Room):

    def __init__(self):
        super().__init__("vault", "Regex & checksum validation", ["vault_dump.txt"])

    def solve(self, state: GameState):

        #import the file
        with open("data/vault_dump.txt") as f:

            # we iterate through each line in our file
            for line in f:
                #here we look for patterns matching our regex
                match = safe_pattern.search(line)
                if match:
                    #In case the regex matches we take the groups that we specified and see if a + b == c and if it matches we found our line
                    if int(match.group(1)) + int(match.group(2))==int(match.group(3)):

                        safe_token = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

                        #storing the token in GameState
                        state.tokens["SAFE"] = safe_token

                        #returning the evidence/expected output to the engine
                        return {
                            "token": safe_token,
                            "match": line.rstrip("\n"),
                            "check": f"{match.group(1)}+{match.group(2)}={match.group(3)}"
                        }

        #In case no valid SAFE line was found
        return None

