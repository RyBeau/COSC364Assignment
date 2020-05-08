from CustomExceptions import *

CONFIG_FORMAT = "format should match:\n{Router_id}\ninput ports {input port}, {input port},...\noutput ports {output port}-{metric}-{id},..."

# convert id from string to int
def convert_id(param_id):
    try:
        converted_id = int(param_id)
        if 1 <= converted_id <= 64000:
            return converted_id
        else:
            raise RouterException("Router id is out of range must be between 1 and 64000 inclusive")
    except RouterException:
        raise
    except Exception:
        raise RouterException("Error converting router id\n" + CONFIG_FORMAT)


# Return a list of input ports as integers
def convert_input(param_input_ports):
    port_list = []
    try:
        for port in param_input_ports:
            converted_port = int(port)

            if not (1024 <= converted_port <= 64000):
                raise RouterException("Input port out of range must be between 1024 and 64000 inclusive")

            if converted_port in port_list:
                raise RouterException("Input ports can only be used once")

            port_list.append(converted_port)

        return port_list

    except RouterException:
        raise
    except Exception:
        raise RouterException("Unable to convert input ports\n" + CONFIG_FORMAT)


# Return a list of output ports as integers
def convert_output(param_output_ports, input_ports):
    port_list = []
    try:
        for port in param_output_ports:

            port = port.split('-')
            router_port = int(port[0])
            router_metric = int(port[1])
            router_id = int(port[2])

            if not (1024 <= router_port <= 64000):
                raise RouterException("Output port out of range must be between 1024 and 64000 inclusive")

            if router_metric < 0 or router_metric > 16:
                raise RouterException("Route metric out of range must be between 1 and 16 inclusive")

            if not (1 <= router_id <= 64000):
                raise RouterException("Neighbour router ID out of range must be between 1 and 64000 inclusive")

            if router_port in input_ports:
                raise RouterException("Output port is also an input port")

            if router_port in [p[0] for p in port_list]:
                raise RouterException("Output ports can only be used once")

            port_tuple = tuple([router_port, router_metric, router_id])
            port_list.append(port_tuple)

        if len(port_list) != len(input_ports):
            raise RouterException("There are not the same number of input ports and output ports")

        return port_list
    except RouterException:
        raise
    except Exception:
        raise RouterException("Could not convert output ports\n" + CONFIG_FORMAT)


# Main
def router_config(filename):
    try:
        file = open(filename, 'r')

        print("\'%s\' file exists" % filename)

    except Exception:
        raise RouterException("File not found")

    else:
        lines = file.readlines()

        i = 0
        while i < len(lines):  # filters out comments and new lines
            line = lines[i]

            if line == '\n':
                lines.pop(i)

            elif line[0] == "#":
                lines.pop(i)

            else:
                i += 1

        filtered_lines = [line[:-1] if line[-1] == "\n" else line for line in lines]

        try:
            router_id = convert_id(filtered_lines[0])
            input_ports = convert_input(filtered_lines[1][12:].split(", "))
            output_ports = convert_output(filtered_lines[2][13:].split(", "), input_ports)

        except RouterException:
            raise
        except Exception:
            raise RouterException("Error with config file " + CONFIG_FORMAT)
        else:
            return router_id, input_ports, output_ports

# router_config("router1.txt")
