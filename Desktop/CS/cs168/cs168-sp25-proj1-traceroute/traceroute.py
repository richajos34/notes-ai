import util

# Your program should send TTLs in the range [1, TRACEROUTE_MAX_TTL] inclusive.
# Technically IPv4 supports TTLs up to 255, but in practice this is excessive.
# Most traceroute implementations cap at approximately 30.  The unit tests
# assume you don't change this number.
TRACEROUTE_MAX_TTL = 30

# Cisco seems to have standardized on UDP ports [33434, 33464] for traceroute.
# While not a formal standard, it appears that some routers on the internet
# will only respond with time exceeeded ICMP messages to UDP packets send to
# those ports.  Ultimately, you can choose whatever port you like, but that
# range seems to give more interesting results.
TRACEROUTE_PORT_NUMBER = 33434  # Cisco traceroute port number.

# Sometimes packets on the internet get dropped.  PROBE_ATTEMPT_COUNT is the
# maximum number of times your traceroute function should attempt to probe a
# single router before giving up and moving on.
PROBE_ATTEMPT_COUNT = 3

class IPv4:
    # Each member below is a field from the IPv4 packet header.  They are
    # listed below in the order they appear in the packet.  All fields should
    # be stored in host byte order.
    #
    # You should only modify the __init__() method of this class.
    version: int
    header_len: int  # Note length in bytes, not the value in the packet.
    tos: int         # Also called DSCP and ECN bits (i.e. on wikipedia).
    length: int      # Total length of the packet.
    id: int
    flags: int
    frag_offset: int
    ttl: int
    proto: int
    cksum: int
    src: str
    dst: str

    def __init__(self, buffer: bytes):
        self.version, self.header_len = self.get_version_header_length(buffer[0])
        self.tos = buffer[1]
        
        #read
        self.length = self.read_16_big_endian(buffer, 2)
        self.id = self.read_16_big_endian(buffer, 4)
        self.flags, self.frag_offset = self.get_flags_and_offset(buffer[6:8])
        
        #time to live
        self.ttl = buffer[8]
        self.proto = buffer[9]
        
        #convert
        self.cksum = self.read_16_big_endian(buffer, 10)
        self.src = self.bytes_to_ip(buffer[12:16])
        self.dst = self.bytes_to_ip(buffer[16:20])

    def __str__(self) -> str:
        return f"IPv{self.version} (tos 0x{self.tos:x}, ttl {self.ttl}, " + \
            f"id {self.id}, flags 0x{self.flags:x}, " + \
            f"ofsset {self.frag_offset}, " + \
            f"proto {self.proto}, header_len {self.header_len}, " + \
            f"len {self.length}, cksum 0x{self.cksum:x}) " + \
            f"{self.src} > {self.dst}"
    
    #byte -> ipv4
    def get_version_header_length(self, byte: int):
        version = byte >> 4
        header_len = (byte & 0x0F) * 4
        return version, header_len
    
    def read_16_big_endian(self, buffer: bytes, start: int):
        return int.from_bytes(buffer[start:start+2], "big")
    
    #read 32 bits in big endian + fragment offset 
    def get_flags_and_offset(self, flag_bytes: bytes):
        #cite: stage 2 hints
        b = ''.join(format(byte, '08b') for byte in flag_bytes)
        flags = int(b[:3], 2)
        offset = int(b[3:], 2)
        return flags, offset

    #byte -> ip
    def bytes_to_ip(self, ip_bytes: bytes):
        return ".".join(str(byte) for byte in ip_bytes)


class ICMP:
    # Each member below is a field from the ICMP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    type: int
    code: int
    cksum: int

    def __init__(self, buffer: bytes):
        self.type, self.code = buffer[0], buffer[1]
        
        #read
        self.cksum = self.read_16_big_endian(buffer, 2)

    def __str__(self) -> str:
        return f"ICMP (type {self.type}, code {self.code}, " + \
            f"cksum 0x{self.cksum:x})"
    
    def read_16_big_endian(self, buffer: bytes, start: int):
        return int.from_bytes(buffer[start:start+2], "big")


class UDP:
    # Each member below is a field from the UDP header.  They are listed below
    # in the order they appear in the packet.  All fields should be stored in
    # host byte order.
    #
    # You should only modify the __init__() function of this class.
    src_port: int
    dst_port: int
    len: int
    cksum: int

    def __init__(self, buffer: bytes):
        self.src_port = self.read_16_big_endian(buffer, 0)
        self.dst_port = self.read_16_big_endian(buffer, 2)
        
        self.len = self.read_16_big_endian(buffer, 4)
        self.cksum = self.read_16_big_endian(buffer, 6)

    def __str__(self) -> str:
        return f"UDP (src_port {self.src_port}, dst_port {self.dst_port}, " + \
            f"len {self.len}, cksum 0x{self.cksum:x})"
    
    def read_16_big_endian(self, buffer: bytes, start: int):
        return int.from_bytes(buffer[start:start+2], "big")

# TODO feel free to add helper functions if you'd like
    #read 16 bits in big endian
    def read_16_big_endian(self, buffer: bytes, start: int):
        return int.from_bytes(buffer[start:start+2], "big")

def traceroute(sendsock: util.Socket, recvsock: util.Socket, ip: str) \
        -> list[list[str]]:
    """ Run traceroute and returns the discovered path.

    Calls util.print_result() on the result of each TTL's probes to show
    progress.

    Arguments:
    sendsock -- This is a UDP socket you will use to send traceroute probes.
    recvsock -- This is the socket on which you will receive ICMP responses.
    ip -- This is the IP address of the end host you will be tracerouting.

    Returns:
    A list of lists representing the routers discovered for each ttl that was
    probed.  The ith list contains all of the routers found with TTL probe of
    i+1.   The routers discovered in the ith list can be in any order.  If no
    routers were found, the ith list can be empty.  If `ip` is discovered, it
    should be included as the final element in the list.
    """

    #task 1
    """
    #setup
    ttl = 1
    sendsock.set_ttl(ttl)
    
    #send
    sendsock.sendto("dataPacket".encode(), (ip, TRACEROUTE_PORT_NUMBER))
    
    #check if response available
    #cite project spec - section receiving packets
    if recvsock.recv_select():  # Check if there's a packet to process.
        buf, address = recvsock.recvfrom()  # Receive the packet.

        # Print out the packet for debugging.
        print(f"Packet bytes: {buf.hex()}")
        print(f"Packet is from IP: {address[0]}")
        print(f"Packet is from port: {address[1]}")
        
    return []
"""
    routers_per_ttl = []
    for ttl in range(1, TRACEROUTE_MAX_TTL + 1):
        sendsock.set_ttl(ttl)
        routers_at_this_hop = []
        responses_count = 0
        for _ in range(PROBE_ATTEMPT_COUNT):
            sendsock.sendto("dataPacket".encode(), (ip, TRACEROUTE_PORT_NUMBER))
            
        while(responses_count < PROBE_ATTEMPT_COUNT):
            if recvsock.recv_select():
                buf, address = recvsock.recvfrom()
                responses_count += 1
            else:
                break
            
            try:
                ipv4_header = IPv4(buf)
            except:
                break
            
            #duplicates
            if ipv4_header.src not in routers_at_this_hop:
                    routers_at_this_hop.append(ipv4_header.src)

        #missing
        if not routers_at_this_hop:
            print(f"{ttl}: * * *") #kept at print bc print_result resolved ip addresses
            routers_per_ttl.append([])
        else:
            util.print_result(routers_at_this_hop, ttl)
            routers_per_ttl.append(routers_at_this_hop)

        if ip in routers_at_this_hop:
            return routers_per_ttl

    return routers_per_ttl
        


if __name__ == '__main__':
    args = util.parse_args()
    ip_addr = util.gethostbyname(args.host)
    print(f"traceroute to {args.host} ({ip_addr})")
    traceroute(util.Socket.make_udp(), util.Socket.make_icmp(), ip_addr)
