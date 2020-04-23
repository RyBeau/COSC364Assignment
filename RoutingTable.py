"""
This is the RoutingTable class for the COSC364 Assignment.
"""


class RoutingTable:
    def __init__(self):
        """Initialise starting properties
        Table entry format (destination_id, next_hop_routerID, metric, flag)
        flag
        'c' for change in RoutingTable
        'u' for updated, when a triggered update is sent
        """
        self.table = {}

    def __str__(self):
        table_string = ""
        for key in self.table.keys():
            table_string += "{}: Next Hop ID {}, Metric: {}\n".format(key, self.table[key][1], self.table[key][2])
        return "Routing Table\n" + table_string

    def update(self, rip_entries):
        """
        Expected RIP entry format
        (destination_id, next_hop_id, metric)
        """
        for entry in rip_entries:
            if not str(entry[0]) in self.table.keys():
                self.table[str(entry[0])] = (entry[0], entry[1], entry[2], "c")
            elif self.table[str(entry[0])][2] > entry[2]:
                self.table[str(entry[0])] = (entry[0], entry[1], entry[2], "c")
            elif self.table[str(entry[0])][1] == entry[1] and entry[2] == 16:
                self.table[str(entry[0])] = (entry[0], entry[1], entry[2], "c")

    def get_entries(self):
        return self.table.values()

if __name__ == "__main__":
    routing_table = RoutingTable()
    print("Intial Table:")
    print(routing_table)
    print("First Fill Test")
    test_entries1 = [(1, 2, 5), (3, 2, 10), (4, 2, 15), (5, 2, 1)]
    routing_table.update(test_entries1)
    print(routing_table)
    print("Updating table Test")
    test_entries2 = [(1, 3, 1), (4, 3, 10), (5, 3, 5)]
    routing_table.update(test_entries2)
    print(routing_table)
    print("Set Unreachable Test")
    test_entries3 = [(1, 3, 16), (4, 3, 16), (5, 3, 16)]
    routing_table.update(test_entries3)
    print(routing_table)
    print("Get entries test")
    print(routing_table.get_entries())
"""
RoutingTable Planning

Print routing table

Update routing table
    for entry in entries
        if router id not in table keys && entry metric < 16
            table key = entry
        else if table key metric > entry metric
            table key = entry
        else if entry metric = 16 && entry next hop = table next hop
            table key metric = 16
        
"""