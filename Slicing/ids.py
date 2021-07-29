from collections import Counter
from scapy.all import sniff,send,IP,TCP,AsyncSniffer,wrpcap,Raw
import ipaddress
import random
import string
import random

## Create a Packet Counter
packet_counts = Counter()
chars = string.ascii_letters + string.punctuation



class ids:
    def __init__(self, src,dest,slicee,packets):
        self.src = src
        self.dest = dest
        self.slice= slicee
        self.length=0
        self.data=" "
        self.packet=packets
        
        
        

    def not_detect(self):
        pkts=AsyncSniffer(filter="host 2.3.4.5", prn=self.custom_action)
        pkts.start()

        a=str(self.dest)
        if a=='1.1.1.11' or a=='1.1.1.8' or a=='1.1.1.13':
            c=random.randint(1000,2000)
        else:
            c=random.randint(10,100)
        
        self.data=self.random_string_generator(c, chars)
        send(IP(src=str(self.src),dst=str(self.dest))/TCP(sport=80,dport=80)/Raw(self.data),count=self.packet)
        
        if self.check_resource_is_min():
            #print(f"{f'{key[0]} <--> {key[1]}'}: {count}" for key, count in packet_counts.items())
            return True
        else:
            return False

        

    def custom_action(self,packet):
        key = tuple(sorted([packet[0][1].src, packet[0][1].dst]))
        packet_counts.update([key])
        wrpcap('s.pcap',packet,append=True)
        #print(len(packet))
        self.length=len(packet)
        #return f"Packet #{sum(packet_counts.values())}: {packet[0][1].src} ==> {packet[0][1].dst}"
 
    
    def random_string_generator(self,str_size, allowed_chars):
        return ''.join(random.choice(allowed_chars) for x in range(str_size))

    def check_resource_is_min(self):
        l=self.length+600
        print(f'length: {l}')
        if l<=1500:
            return True
        else:
            return False
            




