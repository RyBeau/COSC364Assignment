
# convert id from string to int
def convert_id(param_id):
    try:
        converted_id = int(param_id)
        if 1 <= converted_id <= 64000:
            return converted_id
    
    except:
        return False
    
    
# Return a list of input ports as integers
def convert_input(param_input_ports):
    port_list = []
    try:
        for port in param_input_ports:
            converted_port = int(port)
            
            if 1024 <= converted_port <= 64000:
                port_list.append(converted_port)
                
            else:
                return False
            
        return port_list
    
    except:
        return False    
    
    
# Return a list of output ports as integers
def convert_output(param_output_ports):
    port_list = []
    try:
        for port in param_output_ports:
            
            port = port.split('-')
            router_port = int(port[0])
            router_metric = int(port[1])
            router_id = int(port[2])
            
            if not(1024 <= router_port <= 64000):
                return False
            
            if router_metric < 0:
                return False
            
            if not(1 <= router_id <= 64000):
                return False
            
            
            port_tuple = tuple([router_port, router_metric, router_id])
            port_list.append(port_tuple)
            
            
        return port_list
    
    except:
        return False
    


# Main
def router_config(filename):
    try:
        file = open(filename, 'r')
        
        print("\'%s\' file exists" % filename)
        
    except:
        print("Config file cannot be found.")
        return

    
    
    router_id = None;
    input_ports = []
    output_ports = []
    
    lines = file.readlines()
    
    i = 0
    while i < len(lines): # filters out comments and new lines
        line = lines[i]
        
        if line == '\n':
            lines.pop(i)
        
        elif line[0] == "#":
            lines.pop(i)
            
        else:
            i += 1
            
    
    filtered_lines = [line[:-1] if line[-1] == "\n" else line for line in lines]
    
    
    for line in filtered_lines:
        if len(line) == 1: # get id
            router_id = line

        elif line[:11] == "input-ports": # get input ports
            input_ports = line[12:].split(', ')
            
        elif line[:12] == "output-ports": # get output ports
            output_ports = line[13:].split(', ')
            
    
    
    router_id = convert_id(router_id)
    if router_id == False:
        print("Problem converting router id.")
        return
    
    input_ports = convert_input(input_ports)
    if input_ports == False:
        print("Problem converting input ports")
        return
    
    output_ports = convert_output(output_ports)
    if output_ports == False:
        print("Problem converting output ports")
        return
    
    
    
    return router_id, input_ports, output_ports



#router_config("router1.txt")