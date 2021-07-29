class Slice:
    def __init__(self, name, ratio,
                 connected_users, user_share, delay_tolerance, qos_class,
                 bandwidth_guaranteed, bandwidth_max, init_capacity,
                 usage_pattern,packet):
        self.name = name
        self.connected_users = connected_users
        self.total_user=0
        self.user_share = user_share
        self.delay_tolerance = delay_tolerance
        self.qos_class = qos_class
        self.ratio = ratio
        self.bandwidth_guaranteed = bandwidth_guaranteed
        self.bandwidth_max = bandwidth_max #max bandwidth for each client
        self.init_capacity = init_capacity #available bandwidth of this slice
        self.capacity = 0
        self.available_bandwidth=init_capacity
        self.usage_pattern = usage_pattern
        self.packet=packet
        self.is_intruder=False
        self.intrusion_rate=0
        self.client=[]
        self.disable=False


    def get_consumable_share(self):
        if self.connected_users <= 0:
            return min(self.init_capacity, self.bandwidth_max)
        else:
            return min(self.init_capacity/self.connected_users, self.bandwidth_max)

    def is_avaliable(self):
        if self.disable==True:
            return False
        real_cap = min(self.init_capacity, self.bandwidth_max)
        bandwidth_next = real_cap / (self.connected_users + 1)
        

        if bandwidth_next < self.bandwidth_guaranteed:
            return False
        
        
        return True

    def intrusion_packet(self,pack):
        if pack>self.packet:
            return True
        else:
            return False

    def resource_reduce(self):
        h=self.available_bandwidth
        self.available_bandwidth=self.available_bandwidth-self.packet*8000
        print(f'Resource reduced from {h} to {self.available_bandwidth}')


    def reduce_band(self,num):
        self.connected_users+=1000
        
    def __str__(self):
        return f'{self.name:<10} init={self.init_capacity:<5} cap={self.capacity.level:<5} diff={(self.init_capacity - self.capacity.level):<5}'

    def get_max_band(self):
        return self.bandwidth_max

    def is_usage_min(self,resource):
        self.available_bandwidth=self.available_bandwidth-resource
        if resource<self.bandwidth_max:
            return True
        else:
            return False

    def is_usage_less_than_threshold(self,resource):
        self.available_bandwidth=self.available_bandwidth-resource
        if resource<self.bandwidth_guaranteed:
            return True
        else:
            return False


    def inc_intrusion(self):
        self.intrusion_rate=self.intrusion_rate+1
        self.is_intruder=True
        return True
        #if self.intrusion_rate>=1:
            #self.is_intruder=True
            #return True
        #else:
            #return False