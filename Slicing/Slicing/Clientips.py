import operator
from os import name
import random
from scapy.all import*
from .ids import ids
from .utils import distance, KDTree


class Clientips:
    def __init__(self, pk, env, x, y, mobility_pattern,
                 usage_freq,
                 subscribed_slice_index,packet, stat_collector,
                 base_station=None):
        self.pk = pk
        self.env = env
        self.x = x
        self.y = y
        self.mobility_pattern = mobility_pattern
        self.usage_freq = usage_freq
        self.base_station = base_station
        self.stat_collector = stat_collector
        self.subscribed_slice_index = subscribed_slice_index
        self.usage_remaining = 0
        self.last_usage = 0
        self.closest_base_stations = []
        self.connected = False
        self.bs=[]
        self.handover=0
        self.is_intruder=False
        

        
        # Stats
        self.total_connected_time = 0
        self.total_unconnected_time = 0
        self.total_request_count = 0
        self.total_consume_time = 0
        self.total_usage = 0
        self.packets=packet
        self.action = env.process(self.iter())
        # print(self.usage_freq)

    def iter(self):
        '''
        There are four steps in a cycle:
            1- .00: Lock
            2- .25: Stats
            3- .50: Release
            4- .75: Move
        '''

        # .00: Lock
        if self.base_station is not None:
            if self.usage_remaining > 0:
                if self.connected:
                    self.start_consume()
                
                else:
                    self.connect()
            else:
                if self.connected:
                    self.disconnect()
                else:
                    self.generate_usage_and_connect()
        
        yield self.env.timeout(0.25)

        # .25: Stats
        
        yield self.env.timeout(0.25)
        
        # .50: Release
        # Base station check skipped as it's already implied by self.connected
        if self.connected and self.last_usage > 0:
            self.release_consume()
            if self.usage_remaining <= 0:
                self.disconnect()

        yield self.env.timeout(0.25)
        
        # .75: Move
        # Move the client
        x, y = self.mobility_pattern.generate_movement()

        self.x += x
        self.y += y
        

        if self.base_station is not None:
            if not self.base_station.coverage.is_in_coverage(self.x, self.y):
                self.disconnect()
                print("changed")
                self.assign_closest_base_station(exclude=[self.base_station.pk])
                self.incr_handover_count()

        else:
            self.assign_closest_base_station()
        
        yield self.env.timeout(0.25)
        
        yield self.env.process(self.iter())

    def get_slice(self):
        if self.base_station is None:
            return None
        return self.base_station.slices[self.subscribed_slice_index]
    
    def generate_usage_and_connect(self):
        if self.usage_freq < random.random() and self.get_slice() is not None:
            # Generate a new usage
            self.usage_remaining = self.get_slice().usage_pattern.generate()
            self.total_request_count += 1
            if self.connect():
                print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] requests {self.usage_remaining} usage.')

    def connect(self):
        s = self.get_slice()
        b=self.base_station.pk
        if self.connected:
            return
        # increment connect attempt
        self.stat_collector.incr_connect_attempt(self)
        if s.intrusion_packet(self.packets)==False:
            if s.is_avaliable():
            
                s.connected_users += 1
                s.total_user+=1
                s.client.append(self)

                self.connected = True
                print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] connected to slice={self.get_slice().name} @ {self.base_station}')
                intrusion = ids("2.3.4.5",self.base_station.ip,s,self.packets)
                if intrusion.not_detect():
                    return True
                else:
                    print(f'\t--Intrusion detected at client {self.pk} as size of packet sent is huge---------------------------------')
                    print(f' \t----------------------Client_{self.pk} is disconnected as intrusion detected')
                    self.usage_remaining=0
                    self.is_intruder=True
                    self.disconnect()
                    print(f' \t--Intrusion detected at slice {s} ------------------')
                    print(f' \t--Slice {s} is diabled------------------')

                    s.is_intruder=True
                    s.disable=True
                    self.moveToOtherSlice()
                    return False
                    

        
            else:
                self.assign_closest_base_station(exclude=[self.base_station.pk])
                if self.base_station is not None and self.get_slice().is_avaliable():
                    # handover
                    self.stat_collector.incr_handover_count(self)
                    self.incr_handover_count()

                elif self.base_station is not None:
                    # block
                    self.stat_collector.incr_block_count(self)
                else:
                    pass # uncovered
                print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] connection refused to slice={s} @ Base Station-{b}')
                return False
        else:
            print("Intrusion detected as packets are more")
            print(f' ----------------------Client_{self.pk} is disconnected as intrusion detected')
            self.is_intruder=True

            
            self.connected = False
            return False
            

    def disconnect(self):
        if self.connected == False:
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] is already disconnected from slice={self.get_slice()} @ {self.base_station}')
       

        else:
            slice = self.get_slice()
            slice.connected_users -= 1
            slice.client.remove(self)

            self.connected = False
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] disconnected from slice={self.get_slice()} @ {self.base_station}')
        return not self.connected

    def start_consume(self):
        s = self.get_slice()
        if s.is_usage_min(self.usage_remaining)==False:
            print("-----Intrusion detected-----REQUESTED FOR MORE RESOURCE ")
            self.is_intruder=True

            self.disconnect()
        else:
            amount = min(s.get_consumable_share(), self.usage_remaining)
            # Allocate resource and consume ongoing usage with given bandwidth
            s.capacity.get(amount)
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] gets {amount} usage.')
            self.last_usage = amount

    def release_consume(self):
        s = self.get_slice()
        # Put the resource back
        if self.last_usage > 0: # note: s.capacity.put cannot take 0
            s.capacity.put(self.last_usage)
            print(f'[{int(self.env.now)}] Client_{self.pk} [{self.x}, {self.y}] puts back {self.last_usage} usage.')
            self.total_consume_time += 1
            self.total_usage += self.last_usage
            self.usage_remaining -= self.last_usage
            self.last_usage = 0

    # Check closest base_stations of a client and assign the closest non-excluded avaliable base_station to the client.
    def assign_closest_base_station(self, exclude=None):
        updated_list = []
        for d,b in self.closest_base_stations:
            if exclude is not None and b.pk in exclude:
                continue
            d = distance((self.x, self.y), (b.coverage.center[0], b.coverage.center[1]))
            updated_list.append((d,b))
        updated_list.sort(key=operator.itemgetter(0))
        for d,b in updated_list:
            if d <= b.coverage.radius:
                self.base_station = b
                self.bs.append(b)
                print(f'[{int(self.env.now)}] Client_{self.pk} freshly assigned to {self.base_station} at x={self.x},y={self.y}')
                return
        if KDTree.last_run_time is not int(self.env.now):
            KDTree.run(self.stat_collector.clients, self.stat_collector.base_stations, int(self.env.now), assign=False)
        self.base_station = None

    def incr_handover_count(self):
        self.handover+=1

    def __str__(self):
        if self.base_station==None:
            return f'Client_{self.pk}  at [{self.x:<5}, {self.y:>5}] connected to: slice={self.get_slice()} @ {self.base_station}  with mobility pattern of {self.mobility_pattern.name}'
        return f'Client_{self.pk}  at [{self.x:<5}, {self.y:>5}] connected to: slice={self.base_station.slices[self.subscribed_slice_index].name} @ BS_{self.base_station.pk:<2}  with mobility pattern of {self.mobility_pattern.name}'


    def moveToOtherSlice(self):
        s = self.get_slice()
        b=self.base_station
        for bn in self.base_station.slices:
            if bn.name==self.base_station.slices[self.subscribed_slice_index].name:
                for c in bn.client:
                    c.disconnect()
                    c.subscribed_slice_index=3
                    print(f'Client-{c.pk} disconnected from slice {c.get_slice()} and moved to other slice')



        # b.move(s,self.subscribed_slice_index)