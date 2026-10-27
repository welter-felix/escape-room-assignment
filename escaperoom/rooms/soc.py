from datetime import datetime
import ipaddress

from .base import Room, GameState

#Analyse failed SSH login records from auth.log, validate log fields,
#group failed attempts by /24 subnet, identify the busiest subnet and its
#most frequent source IP, and generate a keypad token from the IP's last
#octet and the total number of failed attempts in that subnet."

class SocRoom(Room):
    """Derive a keypad token from failed SSH logins in auth.log."""

    def __init__(self, data_dir="data"):
        super().__init__("SOC", "A cluttered screen shows failed SSH login attempts.","KEYPAD", "auth.log",
                         "Inspect auth.log. Look for the /24 subnet with the most failed logins; its busiest IP gives the keypad code.",
                         data_dir=data_dir, display_name="SOC Triage Desk")

        
    """Validate log entries and build the keypad token from the busiest subnet."""
    def solve(self, state: GameState):
        # Count malformed lines.
        malformed = 0

        # Retain validated failed-login records for the subnet analysis.
        failed_records=[]
        with open(self.data_path(self.item)) as auth_log:
            for line in auth_log:
                fields=line.split()
            
                # The expected sshd record has 13 whitespace-separated fields.
                if len(fields) != 13:
                    malformed += 1
                    continue

                # Check fixed field positions before reading their values below.
                if (fields[3] not in ("Failed", "Accepted") or
                    fields[4] != "password" or
                    fields[5] != "for" or 
                    fields[7] != "from" or 
                    fields[9] != "port" or 
                    fields[11] != "protocol" or 
                    fields[12] != "2" or 
                    not (fields[2].startswith("sshd[") 
                         and fields[2].endswith("]:"))):
                
                    malformed += 1
                    continue

                # Reject timestamps that cannot be parsed as ISO-8601. 
                timestamp = fields[0]

                try:
                    datetime.fromisoformat(timestamp)
                except ValueError:
                    malformed += 1
                    continue

                # Convert the port and process ID to integers to verify that both fields
                # contain valid numeric values; skip the log entry if either is invalid.
                port = fields[10]

                try:
                    port = int(port)
                except ValueError:
                    malformed +=1
                    continue

                sshd = fields[2]
                pid = sshd[5: -2]

                try:
                    pid = int(pid)
                except ValueError:
                    malformed += 1
                    continue

                # Require a valid IPv4 source address before grouping records.
                ipv4 = fields[8]

                try:
                    ipaddress.IPv4Address(ipv4)
                except ValueError:
                    malformed += 1
                    continue

                if fields[3] == "Failed":
                    failed_records.append(fields)

        # Remove the final octet from the IPv4 address to obtain its /24 subnet prefix.
        def get_subnet_prefix(ipv4):
            return ipv4.rsplit('.', 1)[0]
        
        # Map each /24 prefix to its total failed-login count and a nested
        # mapping of source IPs to their individual failed-login counts.
        failures_by_subnet = {}

        for record in failed_records:

            ipv4 = record[8]
            subnet_prefix = get_subnet_prefix(ipv4)

            # Track both subnet-wide failures and per-IP failures within each subnet.
            if subnet_prefix not in failures_by_subnet:
                failures_by_subnet[subnet_prefix] = {"count": 1, "ips": {ipv4:1}}
            else:
                failures_by_subnet[subnet_prefix]["count"] += 1

                if ipv4 not in failures_by_subnet[subnet_prefix]["ips"]:
                    failures_by_subnet[subnet_prefix]["ips"][ipv4] = 1
                else:
                    failures_by_subnet[subnet_prefix]["ips"][ipv4] += 1

        # Select the subnet with the most failures.
        max_subnet_failures = 0
        busiest_subnet_prefix = ""

        for subnet_prefix, record in failures_by_subnet.items():
            if record["count"] > max_subnet_failures:
                max_subnet_failures = record["count"]
                busiest_subnet_prefix = subnet_prefix

        # Within the winning subnet, select the IP with the highest individual count.
        most_frequent_ip = "" 
        max_ip_failures = 0

        for ip, frequency in failures_by_subnet[busiest_subnet_prefix]["ips"].items():
            if frequency > max_ip_failures:
                max_ip_failures = frequency
                most_frequent_ip = ip
 
        last_octet = most_frequent_ip.rsplit('.', 1)[1]
        
        # Return the first original failed-login record from the winning
        # subnet as evidence for the result.
        sample_record=""

        for record in failed_records:

            ipv4 = record[8]
            subnet_prefix = get_subnet_prefix(ipv4)

            if subnet_prefix == busiest_subnet_prefix:
                sample_record = " ".join(record)
                break

        # The keypad code combines the busiest IP's last octet with the total
        # number of failures in its /24 subnet.
        keypad = last_octet + str(max_subnet_failures)

        # Store the solved room token for use by the game state.
        state.tokens["KEYPAD"] = keypad
        
        # Return the token and supporting details for the game interface.
        return{
            "summary": [
                "[Room SOC] Parsing logs...",
                f"{max_subnet_failures} failed attempts found in {busiest_subnet_prefix}.0/24",
                f"Top IP is {most_frequent_ip} (last octet={last_octet})",
                f"Token formed: {keypad}",
            ],

            "token": keypad,
            "top24": busiest_subnet_prefix + ".0/24",
            "count": max_subnet_failures,
            "sample_record": sample_record,
            "malformed": malformed
        }
