import base64           
import codecs          

from .base import Room, GameState

class DnsRoom(Room):
    def __init__(self):
        super().__init__("dns", "Config analysis and decoding", ["dns.cfg"])

    def solve(self, state: GameState):

        records = {} #for storing the key, the encoding and the payload

        with open("data/dns.cfg") as dns_cfg: #importing the dns.cfg file 

            for line in dns_cfg:   #for each line in the file

                if line.startswith("#"):  #ignoring the comment lines
                    continue                

                # parsing the key=value
                key_value = line.split("=", 1)    
                key = key_value[0].strip() 
                value = key_value[1].strip()   

                # spliting the value into encoding and payload
                encoding_payload=value.split(":", 1)
                if(len(encoding_payload) > 1):
                    encoding = encoding_payload[0]
                    payload = encoding_payload[1]
                    records[key] = {"encoding": encoding, "payload": payload}

            #decoding the token_tag
            hint = base64.b64decode(records["token_tag"]["payload"])
            hint = hint.decode("utf-8")    
            auth_hint = "hint" + hint

            #decoding the authoritative hint
            record = records[auth_hint]
            payload = record["payload"]
            encoding = record["encoding"]
                
            # choosing the correct decoding
            if(record["encoding"]=="rot13+b64"):
                payload = codecs.decode(record["payload"], "rot13")

            decoded_base64 = base64.b64decode(payload)
            decoded_utf8 = decoded_base64.decode("utf-8")

            #taking the last word ot the hint and removing the period
            final_word=decoded_utf8.split()[-1]
            dns_token = final_word.rstrip('.')

            #storing the token in GameState
            state.tokens["DNS"] = dns_token

            #returning the evidence/expected output to the engine 
            return{
                "token": dns_token,
                "key": auth_hint,
                "encoding": encoding, 
                "decoded_line": decoded_utf8
            }

#TEST - Run with "python -m escaperoom.rooms.dns" - RO BE REMOVED
#state = GameState()
#room = DnsRoom()
#result = room.solve(state)

#print("TOKEN[DNS]=" + result["token"])
#print("EVIDENCE[DNS].KEY=" + result["key"])
#print("EVIDENCE[DNS].ENCODING=" + result["encoding"])
#print("EVIDENCE[DNS].DECODED_LINE=" + result["decoded_line"])