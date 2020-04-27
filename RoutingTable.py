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
        "d" for dead link
        """
        self.table = {}

    def __str__(self):
        table_string = ""
        for key in self.table.keys():
            table_string += "{}: Next Hop ID {}, Metric: {}, Flag {}\n".format(key, self.table[key][1], self.table[key][2], self.table[key][3])
        return "Routing Table\n" + table_string

    def update(self, rip_entries, link_metric):
        """
        Expected RIP entry format
        (destination_id, next_hop_id, metric)
        """
        for entry in rip_entries:
            if not str(entry[0]) in self.table.keys() and entry[2] + link_metric < 16:
                self.table[str(entry[0])] = (entry[0], entry[1], entry[2] + link_metric, "c")
            elif self.table[str(entry[0])][2] > entry[2] + link_metric:
                self.table[str(entry[0])] = (entry[0], entry[1], entry[2] + link_metric, "c")
            elif self.table[str(entry[0])][1] == entry[1] and entry[2] == 16:
                self.table[str(entry[0])] = (entry[0], entry[1], entry[2], "d")

    def get_entries(self, receiving_neighbour):
        """
        receiving_neighbour, ID of router to apply split horizon poisoned reverse for.
        return entry format (destination_id, metric)
        return entry type list
        """
        rip_entries = []
        for entry in self.table.values():
            if entry[0] != receiving_neighbour:
                if entry[1] == receiving_neighbour:
                    rip_entries.append((entry[0], 16))
                else:
                    rip_entries.append((entry[0], entry[2]))
        return rip_entries

    def update_dead_link(self, neighbour_id):
        """
        Updates router entries on death of a neighbour
        """
        for entry in self.table.values():
            if entry[1] == neighbour_id:
                self.table[str(entry[0])] = (entry[0], entry[1], 16, "d")

    def garbage_collection(self):
        keys = list(self.table.keys())
        for key in keys:
            if self.table[key][3] == "d":
                del self.table[key]


if __name__ == "__main__":
    routing_table = RoutingTable()
    print("Intial Table:")
    print(routing_table)
    print("First Fill Test")
    test_entries1 = [(1, 2, 5), (3, 2, 10), (4, 2, 15), (5, 2, 1)]
    routing_table.update(test_entries1, 0)
    print(routing_table)
    print("Updating table Test")
    test_entries2 = [(1, 3, 1), (4, 3, 10), (5, 3, 5)]
    routing_table.update(test_entries2, 0)
    print(routing_table)
    print("Set Unreachable Test")
    test_entries3 = [(1, 3, 16), (4, 3, 16), (5, 3, 16)]
    routing_table.update(test_entries3, 0)
    print(routing_table)
    test_entries4 = [(1, 3, 1), (4, 3, 3)]
    routing_table.update(test_entries4, 0)
    print(routing_table)
    print("Get entries test no SH needed")
    print(routing_table.get_entries(5))
    print("Get entries test SH needed")
    print(routing_table.get_entries(3))
    print(routing_table)
    print("Testing Marking dead links")
    routing_table.update_dead_link(3)
    print(routing_table)
    print("Testing Removing dead links")
    routing_table.garbage_collection()
    print(routing_table)


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