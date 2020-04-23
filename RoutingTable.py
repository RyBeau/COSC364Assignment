"""
This is the RoutingTable class for the COSC364 Assignment.
"""
class RoutingTable:
    def __init__(self):
        """Initialise starting properties"""
        self.table = {}


    def __str__(self):
        table_string = ""
        for key in self.table.keys():
            #table_string += "{}: {}\n".format(key, self.table[key])
            table_string += "{}: {}\n".format(key, self.table[key][0])
        return table_string



    def update(self, rip_entries):
        for entry in rip_entries:
            if not str(entry[1]) in self.table.keys():
                #self.table[str(entry[1])] = entry[0]
                
                # 'c' for change in RoutingTable
                # 'u' for updated, when a triggered update is sent
                self.table[str(entry[1])] = (entry[0], "c")
