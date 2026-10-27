import base64           
import codecs          

from .base import Room, GameState

# Read dns.cfg records, follow the Base64-encoded token_tag to the authoritative
# hint, decode that hint according to its declared encoding, and use its final
# word as the DNS token.

class DnsRoom(Room):
    """Decode the authoritative hint in dns.cfg to obtain the DNS token."""

    def __init__(self, data_dir="data"):
        super().__init__("dns", "The walls are covered with scribbled key=value pairs.","DNS","dns.cfg",
                         "Inspect dns.cfg. The token_tag tells you which hint record is the real one, and some hints are double encoded.",
                         data_dir=data_dir, display_name="DNS Closet")

    def solve(self, state: GameState):
        """Follow the token tag, decode its hint, and save the resulting token."""
        # Map each record key to its declared encoding and encoded payload.
        records = {}

        with open(self.data_path(self.item)) as dns_cfg:

            for line in dns_cfg:

                # Configuration comment lines are not records.
                if line.startswith("#"):
                    continue                

                # Separate the record name from its encoded value.
                key_value_parts = line.split("=", 1)    
                key = key_value_parts[0].strip() 
                value = key_value_parts[1].strip()   

                # The value format is "encoding:payload".
                encoding_payload_parts=value.split(":", 1)
                if(len(encoding_payload_parts) > 1):
                    encoding = encoding_payload_parts[0]
                    payload = encoding_payload_parts[1]
                    records[key] = {"encoding": encoding, "payload": payload}

            # token_tag contains the Base64-encoded suffix of the authoritative
            # hint key; prefix it with "hint" to select the corresponding record.
            hint = base64.b64decode(records["token_tag"]["payload"])
            hint = hint.decode("utf-8")    
            auth_hint = "hint" + hint

            # Retrieve the selected hint's encoding and payload for decoding.
            record = records[auth_hint]
            payload = record["payload"]
            encoding = record["encoding"]
                
            # For rot13+b64 records, reverse the ROT13 layer before decoding
            # the underlying Base64 payload.
            if(record["encoding"]=="rot13+b64"):
                payload = codecs.decode(record["payload"], "rot13")

            # Decode Base64 bytes as UTF-8 to recover the complete hint text.
            decoded_base64 = base64.b64decode(payload)
            decoded_hint = decoded_base64.decode("utf-8")

            # The final whitespace-delimited word is the token.
            final_word=decoded_hint.split()[-1]
            dns_token = final_word.rstrip('.')

            # Store the solved room token for use by the game state.
            state.tokens["DNS"] = dns_token

            # Return the token and supporting details for the game interface. 
            return{
                "summary": [
                    "[Room DNS] Decoding hints...",
                    f"Decoded line : {decoded_hint}",
                    f"Token formed: {dns_token}",
                ],
                  
                "token": dns_token,
                "key": auth_hint,
                "encoding": encoding, 
                "decoded_line": decoded_hint
            }
