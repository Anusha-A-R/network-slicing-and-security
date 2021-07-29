class BaseStation:
    def __init__(self, pk, coverage, capacity_bandwidth, ip, slices=None):
        self.pk = pk
        self.coverage = coverage
        self.capacity_bandwidth = capacity_bandwidth
        self.slices = slices
        self.ip=ip
        print(self)
        

    def __str__(self):
        return f'BS_{self.pk:<2}\t cov:{self.coverage}\t with cap {self.capacity_bandwidth:<5}\t IP {self.ip} '
    
    def printed(self):
        return f'BS_{self.pk:<2}\t '

    def move(self,slice,index):
        print("1")
        # for s in self.slices:
        #     print(2)
        #     if s[index]==slice:
        #         print(3)
        #         for client in s.client:
        #             print(4)
        #             client.disconnect()
        #             client.subscribed_slice_index=3
        #             print(f'Client-{client.pk} disconnected from slice {client.get_slice()} and moved to other slice')
        #             client.iter()

