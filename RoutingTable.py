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

    def update(self, rip_entries, next_hop_id, link_metric):
        """
        Expected RIP entry format
        (destination_id, metric)
        """
        for entry in rip_entries:
            if not str(entry[1]) in self.table.keys() and entry[2] + link_metric < 16:
                self.table[str(entry[1])] = (entry[1], next_hop_id, entry[2] + link_metric, "c")
            elif self.table[str(entry[1])][2] > entry[2] + link_metric:
                self.table[str(entry[1])] = (entry[1], next_hop_id, entry[2] + link_metric, "c")
            elif self.table[str(entry[1])][1] == next_hop_id and entry[2] == 16:
                self.table[str(entry[1])] = (entry[1], next_hop_id, entry[2], "d")

    def get_entries(self, sending_router_id, receiving_neighbour=None):
        """
        receiving_neighbour, ID of router to apply split horizon poisoned reverse for.
        return entry format (destination_id, metric)
        return entry type list
        Default parameter for initial message sending for unknown links
        """
        rip_entries = [(sending_router_id, 0)]
        if receiving_neighbour is not None:
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
        """
        Removes any links marked for garbage collection
        """
        keys = list(self.table.keys())
        for key in keys:
            if self.table[key][3] == "d":
                del self.table[key]


if __name__ == "__main__":
    routing_table = RoutingTable()
    print("Intial Table:")
    print(routing_table)
    print("First Fill Test")
    test_entries1 = [(None, 1, 5), (None, 3, 10), (None, 4, 15), (None, 5, 1)]
    routing_table.update(test_entries1, 2, 0)
    print(routing_table)
    print("Updating table Test")
    test_entries2 = [(None, 1, 1), (None, 4, 10), (None,5, 5)]
    routing_table.update(test_entries2, 3, 0)
    print(routing_table)
    print("Set Unreachable Test")
    test_entries3 = [(None, 1, 16), (None, 4, 16), (None, 5, 16)]
    routing_table.update(test_entries3, 3, 0)
    print(routing_table)
    test_entries4 = [(None, 1, 1), (None, 4, 3)]
    routing_table.update(test_entries4, 3, 0)
    print(routing_table)
    print("Get entries test no SH needed")
    print(routing_table.get_entries(1, 5))
    print("Get entries test SH needed")
    print(routing_table.get_entries(1, 3))
    print(routing_table)
    print("Testing Marking dead links")
    routing_table.update_dead_link(1, 3)
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