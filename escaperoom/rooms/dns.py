import base64           #Is it okay to import this library for decoding?
import codecs           #Is it okay to import this library for decoding?

dns_cfg = open("data/dns.cfg") #importing the dns.cfg file 

records = {} #for storing the key, the encoding and the payload

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

#printing the expected output 
print("TOKEN[DNS]=" + dns_token)
print("EVIDENCE[DNS].KEY=" + auth_hint)
print("EVIDENCE[DNS].ENCODING=" + encoding)
print("EVIDENCE[DNS].DECODED_LINE=" + decoded_utf8)


    


