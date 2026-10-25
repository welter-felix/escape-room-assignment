import base64           
import codecs          

from .base import Room, GameState

class DnsRoom(Room):
    """Decode the authoritative hint in dns.cfg to obtain the DNS token."""

    def __init__(self, data_dir="data"):
        super().__init__("dns", "Config analysis and decoding","DNS","dns.cfg",
                         "Inspect dns.cfg. The token_tag tells you which hint record is the real one, and some hints are double encoded.",
                         data_dir=data_dir)

    def solve(self, state: GameState):
        """Follow the token tag, decode its hint, and save the resulting token."""
        # Store each configured record's encoding and payload by key.
        records = {}

        with open(self.data_path(self.item)) as dns_cfg:

            for line in dns_cfg:

                # Configuration comment lines are not records.
                if line.startswith("#"):
                    continue                

                # Separate the record name from its encoded value.
                key_value = line.split("=", 1)    
                key = key_value[0].strip() 
                value = key_value[1].strip()   

                # The value format is "encoding:payload".
                encoding_payload=value.split(":", 1)
                if(len(encoding_payload) > 1):
                    encoding = encoding_payload[0]
                    payload = encoding_payload[1]
                    records[key] = {"encoding": encoding, "payload": payload}

            # Decode token_tag to learn which hint record is authoritative.
            hint = base64.b64decode(records["token_tag"]["payload"])
            hint = hint.decode("utf-8")    
            auth_hint = "hint" + hint

            # Retrieve the selected hint's encoding and payload.
            record = records[auth_hint]
            payload = record["payload"]
            encoding = record["encoding"]
                
            # Some records apply ROT13 before Base64; reverse that layer first.
            if(record["encoding"]=="rot13+b64"):
                payload = codecs.decode(record["payload"], "rot13")

            # Decode the remaining Base64 data into the hint text.
            decoded_base64 = base64.b64decode(payload)
            decoded_utf8 = decoded_base64.decode("utf-8")

            # The final word of the hint is the token; remove sentence punctuation.
            final_word=decoded_utf8.split()[-1]
            dns_token = final_word.rstrip('.')

            # Store the solved room token for use by the game state.
            state.tokens["DNS"] = dns_token

            # Return the token and supporting details for the game interface.
            return{
                "token": dns_token,
                "key": auth_hint,
                "encoding": encoding, 
                "decoded_line": decoded_utf8
            }
