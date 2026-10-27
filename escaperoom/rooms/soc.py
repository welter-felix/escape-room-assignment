from datetime import datetime
import ipaddress

from .base import Room, GameState

class SocRoom(Room):
    """Derive a keypad token from failed SSH logins in auth.log."""

    def __init__(self, data_dir="data"):
        super().__init__("SOC", "A cluttered screen shows failed SSH login attempts.","KEYPAD", "auth.log",
                         "Inspect auth.log. Look for the /24 subnet with the most failed logins; its busiest IP gives the keypad code.",
                         data_dir=data_dir, display_name="SOC Triage Desk")

    def solve(self, state: GameState):
        """Validate log entries and build the keypad token from the busiest subnet."""
        malformed = 0

        # Keep only structurally valid failed-login entries for the subnet analysis.
        failed_records=[]
        with open(self.data_path(self.item)) as auth_log:
            for line in auth_log:
                parts=line.split()
            
                # The expected sshd record has 13 whitespace-separated fields.
                if len(parts) != 13:
                    malformed += 1
                    continue

                # Check fixed field positions before reading their values below.
                if (parts[3] not in ("Failed", "Accepted") or
                    parts[4] != "password" or
                    parts[5] != "for" or 
                    parts[7] != "from" or 
                    parts[9] != "port" or 
                    parts[11] != "protocol" or 
                    parts[12] != "2" or 
                    not (parts[2].startswith("sshd[") 
                         and parts[2].endswith("]:"))):
                
                    malformed += 1
                    continue

                # Reject timestamps that cannot be parsed as ISO-8601.
                timestamp = parts[0]

                try:
                    datetime.fromisoformat(timestamp)
                except ValueError:
                    malformed += 1
                    continue

                # Ports and process IDs should be numeric.
                port = parts[10]

                try:
                    port = int(port)
                except ValueError:
                    malformed +=1
                    continue

                sshd = parts[2]
                pid = sshd[5: -2]

                try:
                    pid = int(pid)
                except ValueError:
                    malformed += 1
                    continue

                # Require a valid IPv4 source address before grouping records.
                ipv4 = parts[8]

                try:
                    ipaddress.IPv4Address(ipv4)
                except ValueError:
                    malformed += 1
                    continue

                if parts[3] == "Failed":
                    failed_records.append(parts)

        # An IPv4 /24 is identified by its first three octets.
        def get_24_prefix(ipv4):
            return ipv4.rsplit('.', 1)[0]
        
        grouped_valid_records = {}

        for record in failed_records:

            ipv4 = record[8]
            ipv4_group24 = get_24_prefix(ipv4)

            # Track both subnet-wide failures and per-IP failures within each subnet.
            if ipv4_group24 not in grouped_valid_records:
                grouped_valid_records[ipv4_group24] = {"count": 1, "ips": {ipv4:1}}
            else:
                grouped_valid_records[ipv4_group24]["count"] += 1

                if ipv4 not in grouped_valid_records[ipv4_group24]["ips"]:
                    grouped_valid_records[ipv4_group24]["ips"][ipv4] = 1
                else:
                    grouped_valid_records[ipv4_group24]["ips"][ipv4] += 1

        # Select the subnet with the most failures; ties keep the first encountered.
        largest_count = 0
        largest_24_group = ""

        for ipv4_group24, record in grouped_valid_records.items():
            if record["count"] > largest_count:
                largest_count = record["count"]
                largest_24_group = ipv4_group24

        # Within that subnet, find the IP responsible for the most failures.
        most_frequent_ip = "" 
        most_frequency = 0

        for ip, frequency in grouped_valid_records[largest_24_group]["ips"].items():
            if frequency > most_frequency:
                most_frequency = frequency
                most_frequent_ip = ip
 
        last_octet = most_frequent_ip.rsplit('.', 1)[1]
        
        # Return one original failed-login record as evidence for the result.
        sample=""

        for record in failed_records:

            ipv4 = record[8]
            ipv4_group24 = get_24_prefix(ipv4)

            if ipv4_group24 == largest_24_group:
                sample = " ".join(record)
                break

        # The keypad code combines the IP's with the most failed login attempts' last octet and subnet failure count.
        keypad = last_octet + str(largest_count)

        # Store the solved room token for use by the game state.
        state.tokens["KEYPAD"] = keypad
        
        # Return the token and supporting details for the game interface.
        return{
            "summary": [
                "[Room SOC] Parsing logs...",
                f"{largest_count} failed attempts found in {largest_24_group}.0/24",
                f"Top IP is {most_frequent_ip} (last octet={last_octet})",
                f"Token formed: {keypad}",
            ],

            "token": keypad,
            "top24": largest_24_group + ".0/24",
            "count": largest_count,
            "sample": sample,
            "malformed": malformed
        }
