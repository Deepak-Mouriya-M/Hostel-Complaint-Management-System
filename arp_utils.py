arp_table = {
    "192.168.1.1": "AA:BB:CC:DD:EE:01",
    "192.168.1.2": "AA:BB:CC:DD:EE:02"
}

# ARP: IP → MAC
def arp(ip):
    return arp_table.get(ip, "Not Found")

# RARP: MAC → IP
def rarp(mac):
    for ip, m in arp_table.items():
        if m == mac:
            return ip
    return "Not Found"

print("ARP Lookup:", arp("192.168.1.1"))
print("RARP Lookup:", rarp("AA:BB:CC:DD:EE:02"))