from datetime import datetime
import ipaddress

auth_log = open("data/auth.log") #importing the auth.log file 

malformed = 0

#Making all the checks and creating a list of only the valid records
failed_records=[]
for line in auth_log:
    parts=line.split()
    
    #checking that each line has 13 parts
    if len(parts) != 13:
        malformed += 1
        continue

    #checking each part one by one. Do we need to perform this check? 
    if (parts[3] not in ("Failed", "Accepted") or parts[4] != "password" or 
        parts[5] != "for" or parts[7] != "from" or 
        parts[9] != "port" or parts[11] != "protocol" or parts[12] != "2" or 
        not (parts[2].startswith("sshd[") and parts[2].endswith("]:"))):
        malformed += 1
        continue

    #checking that TIMESTAMP is a valid ISO-8601 timestamp
    timestamp = parts[0]
    try:
        datetime.fromisoformat(timestamp)
    except ValueError:
        malformed += 1
        continue

    #checking that the PORT is an integer 
    port = parts[10]
    try:
        port = int(port) #not using type(value), as 
    except ValueError:
        malformed +=1
        continue

    #checking that the PID is an integer 
    sshd = parts[2]
    pid = sshd[5: -2]
    try:
        pid = int(pid)
    except ValueError:
        malformed += 1
        continue

    #checking that the source is a valid IPv4 address
    ipv4 = parts[8]
    try:
        ipaddress.IPv4Address(ipv4)
    except ValueError:
        malformed += 1
        continue

    if parts[3] == "Failed":
        failed_records.append(parts)

#grouping failures by /24, storing its total failures and its each IPs failure count
grouped_valid_records = {}
for record in failed_records:

    ipv4 = record[8]
    ipv4_group24 = ipv4.rsplit('.', 1)[0] #removes the last octet of the ipv4, giving the /24 

    #grouping the /24-s and their counts
    if ipv4_group24 not in grouped_valid_records:
        grouped_valid_records[ipv4_group24] = {"count": 1, "ips": {ipv4:1}}
    else:
        grouped_valid_records[ipv4_group24]["count"] += 1

        #within the /24, grouping the IPs and their failure counts
        if ipv4 not in grouped_valid_records[ipv4_group24]["ips"]:
            grouped_valid_records[ipv4_group24]["ips"][ipv4] = 1
        else:
            grouped_valid_records[ipv4_group24]["ips"][ipv4] += 1

#finding the /24 group with the largest failure count
largest_count = 0
largest_24_group = ""

for ipv4_group24, record in grouped_valid_records.items():
    if record["count"] > largest_count:
        largest_count = record["count"]
        largest_24_group = ipv4_group24

#finding the most frequent source IP inside the /24 with the largest failure count
most_frequent_ip = "" 
most_frequency = 0

for ip, frequency in grouped_valid_records[largest_24_group]["ips"].items():
    if frequency > most_frequency:
        most_frequency = frequency
        most_frequent_ip = ip

#printing the expected output 
last_octet = most_frequent_ip.rsplit('.', 1)[1] # taking the last octet

sample=""
for record in failed_records:
    ipv4 = record[8]
    ipv4_group24 = ipv4.rsplit('.', 1)[0]

    if (record[3] == "Failed" and ipv4_group24 == largest_24_group):
        sample = " ".join(record) #to make the list record a string
        break

print("TOKEN[KEYPAD]=" + last_octet + str(largest_count))
print("EVIDENCE[KEYPAD].TOP24=" + largest_24_group + ".0/24")
print("EVIDENCE[KEYPAD].COUNT=" + str(largest_count))
print("EVIDENCE[KEYPAD].SAMPLE=" + sample)
print("EVIDENCE[KEYPAD].MALFORMED_SKIPPED=" + str(malformed))