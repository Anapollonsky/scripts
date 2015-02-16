#!/usr/bin/env python
""" aisg_tester.py, aisg_config.py, atl.py
Runs regression tests on AISG using commands from a given file.
Formatting:
* # as first character in line is a comment, and the line will be ignored.
* No space between parameter name and assignment. "PERIOD=0", not "PERIOD = 0", etc.
* No space between command and :. "ALDSCAN: ", not "ALDSCAN : "
* Spaces between parameter declarations. "PERIOD=0 INDEX=1", not "PERIOD=0INDEX=1"
* Empty lines don't matter.
* If multiple devices are detected during ALDSCAN, subsequent commands may be sent once
per every device. Enclose the to-repeat section with {{{ before and }}} after. Every
command between the triple-braces will be duplicated the number of devices that are found,
and every instance of INDEX=X will be replaced with the index returned during the ALDSCAN.
This feature is only reliable with a single {{{ }}} block. 
"""


import pexpect
import time
import sys
import re
import pdb
import types
import serial
from collections import deque


### Initialization
re.DOTALL

# Command to connect with the board
board_connect_command = "telnet 135.112.98.26 1307"

# Commands to send once, to setup the board.
once_commands = "aisg_command_file_single_run"

# Commands to send repeatedly for testing.
repeat_commands = "aisg_command_file_repeat"

# Mapping of sent-stype to first-response-expected-stype.
required_typemap = {'SET':['SETRESPONSE'], 'GET':['GETRESPONSE'], 'ACTION':['ACTIONACK', 'ACTIONCOMP']} # Script will hang until it receives all responses here
allowed_typemap = {'GET':['EVENT'], 'SET':['EVENT'], 'ACTION':['EVENT']} # Script will incorporate, but not hang.

# Timeout for ALDSCAN ACTIONs
expect_timeout = 600 # seconds

# Timeout for device connection/disconnection EVENT captures
capture_event_timeout = 60

# Command to connect with the relay.
relay_connect = "telnet 135.112.98.62 5011"

# Mapping of device serial numbers to relay ports. Note that due to the daisy-chain configuration,
# Turning off the "1" relay port turns off both devices; thus, ensure that when you call to turn off
# port "1", port "2" is already disabled to ensure that that the correct disconnect packet is captured
# in the right order.
relay_device_map = {"00000020120701580": "2", "0000DESA092370436": "1"}

def file_read_blocks(f):
    """Reads an AISG command file, capturing every block and returning a list of blocks and
    a list containing data whether to duplicate every block returned as 1s or 0s. 
    """
    temp_str = ""
    in_block = 0
    in_duplicate = 0
    command_list = []
    duplicate_list = []
    for line in f:
        if line[:3] == "{{{":
            if in_duplicate == 1:
                raise Exception("file_read_blocks: Nested {{{, exiting.")
            else:
                in_duplicate = 1
        elif line[:3] == "}}}":
            if in_duplicate == 0:
                raise Exception("file_read_blocks: nested }}}, exiting.")
            else:
                in_duplicate = 0
        elif line[0] == "[": # Beginning of line
            if in_block == 1:
                raise Exception("file_read_blocks: Nested [, exiting.")
            else:
                temp_str = line
                in_block = 1
        elif line[0] =="]":
            if in_block == 0:
                raise Exception("file_read_blocks: Nested ], exiting.")
            else:
                temp_str += line
                command_list.append(temp_str.rstrip())
                if in_duplicate == 1:
                    duplicate_list.append(1)
                else:
                    duplicate_list.append(0)
                in_block = 0
        elif in_block == 1 and line[0] != "#":
            temp_str += line
    return command_list, duplicate_list

def genqueue(command_list):
    """ Generates initial messagequeue by inserting all commands in commandlist up
    to and including the first ALDSCAN command. Accepts command_list, returns tuple
    containing deque and 0-indexed command_list index of ALDSCAN command.
    """
    output_deque = deque()
    aldind = -1
    for message in command_list:
        aldind += 1
        aldscan_match = re.search(r"ALDSCAN", message)
        if not aldscan_match:
            output_deque.appendleft(message)
            continue
        else:
            output_deque.appendleft(message)
            return aldind, output_deque
    return aldind, output_deque

def iorelay_command_serial(name, commands):
    """ Passes specified character-code list to serial device. Built-in mappings for "1on",
    "1off", "2on" and "2off". Requires sudo.
    """
    command_map = {"1on":[254, 1] , "1off": [254, 0] , "2on": [254, 3] , "2off": [254, 2]}
    if isinstance(commands, types.StringType):
        iorelay_command_serial(name, command_map[commands])
    else:
        ser = serial.Serial(name, 9600, timeout=1)
        for cmd in commands:
            ser.write(chr(cmd))
        ser.close()
    time.sleep(3)
    

def iorelay_command_network(name, commands):
    """ Passes specified character-code list to network device. Built-in mappings for "1on",
    "1off", "2on" and "2off".
    """
    command_map = {"1on":[254, 1] , "1off": [254, 0] , "2on": [254, 3] , "2off": [254, 2]}
    if isinstance(commands, types.StringType):
        iorelay_command_network(name, command_map[commands])
        print "Executing " + commands + "..."
    else:
        board_connect = pexpect.spawn(name)
        sendstr = ""
        for cmd in commands:
            sendstr += chr(cmd)
        time.sleep(2)
        board_connect.send(sendstr)
        time.sleep(2)
        board_connect.close()

def update_queue(queue, command_list, duplicate_list):
    """ After the ALDSCAN, processes commands to finish the queue.
    Accepts deque, command_list and duplicate_list, returns updated deque.
    """
    global GLOBAL_aldscan_ids
    for lid, line in enumerate(command_list):
        if duplicate_list[lid] == 1 and "INDEX" in line:
            for aldindex in GLOBAL_aldscan_ids:
                queue.appendleft(re.sub(r"INDEX=\d+", "INDEX=" + aldindex, line))
        else:
            queue.appendleft(line)
    return queue

def frame_extract_data(messagein):
    """Given a string representing an AISG block, will output a list containing TYPE, ID, and
    ARGLIST lines in the command.
    """
    splitmessage = messagein.strip("\r").split("\n")[1:-1]
    #print splitmessage
    typeresult = re.search("TYPE=(\w+)", splitmessage[0])
    idresult = re.search("ID=(-{0,1}\d+)", splitmessage[1])
    if len(splitmessage) > 2:
        returnlist = [x.strip('\r') for x in splitmessage[2:]]
    else:
        returnlist = []
    if typeresult and idresult:
        return (typeresult.group(1), idresult.group(1), returnlist)
    else:
        return (None, None, [])

def convert_numbers(datain):
    """ Accepts a list or a string input, and converts all decimal and octal numbers to consistent
    representations.
    """
    def convert_numbers_int(matchobj):
        return str(int(matchobj.group(0), 10))
    def convert_numbers_hex(matchobj):
        thematch = re.match('0[xX](\d+)', matchobj.group(0))
        return str(int(thematch.group(1), 16))
    if isinstance(datain, types.ListType): # List case
        dataout = []
        for line in datain:
            lineout = re.sub(r'0[xX]\d+', convert_numbers_hex, line)
            lineout = re.sub(r'\d+', convert_numbers_int, lineout)
            dataout.append(lineout)
    elif isinstance(datain, types.StringType): # String case
        dataout = re.sub(r'0[xX]\d+', convert_numbers_hex, datain)
        dataout = re.sub(r'\d+', convert_numbers_int, dataout)
    return dataout
    for line in rlistlist:
        index_match = re.match(r'ALDSCAN.*INDEX=(\d+)', line)
        if index_match:
            idslist.append(index_match.group(1))

def aldscan_extract_info(rlistlist):
    """ Extract ID information and serial numbers after an ALDSCAN, allowing for repetition for all devices.
    """
    index_list = []
    serial_list = []
    numsub_list = []
    for frame in rlistlist:
        for line in frame:
            index_match = re.search(r"ALDSCAN.+INDEX=(\d+).+SERIAL=\"(\w+)\".*NUMSUB=(\d+).*", line)
            if index_match:
                index_list.append(index_match.group(1))
                serial_list.append(index_match.group(2))
                numsub_list.append(index_match.group(3))
    return index_list, serial_list, numsub_list

def partition_line (line):
    """ Partitions a single line string, such as that returned by frame_extract_data, into a key and a value.
    """
    line.strip('\r')
    # Complicated cases
    ERRORIND_MATCH = re.search(r'ERRORIND', line)
    ald_dev_data_match = re.search(r'(ALDDEVDATA:\s*INDEX=\d+\s*ALDSUB=\d+\s*FIELDNUM=\d+)(.+)\r*', line)
    aldscan_match = re.search(r'(ALDSCAN:\s*PERIOD=\d+\s*INDEX=\d+)(.+)\r*', line)
    alderrstat_match = re.search(r'(ALDERRSTAT:\s*INDEX=\d+\s*ALDSUB=\d+)(.+)\r*', line)
    rettilt_match = re.search(r'(RETTILT:\s*INDEX=\d+\s*ALDSUB=\d+)(.+)\r*', line)
    index_match = re.search(r'([\w\s]+:\s*INDEX=\d+)(.+)\r*', line)
    single_match = re.search(r'([\w\s]+:)(.+)\r*', line)
    if ERRORIND_MATCH:
        raise Exception("partition_line: ERRORIND detected!")
    if ald_dev_data_match:
        return (ald_dev_data_match.group(1), ald_dev_data_match.group(2))
    elif aldscan_match:
        return (aldscan_match.group(1), aldscan_match.group(2))
    elif alderrstat_match:
        return (alderrstat_match.group(1), alderrstat_match.group(2))
    elif rettilt_match:
        return (rettilt_match.group(1), rettilt_match.group(2))
    elif index_match:
        return (index_match.group(1), index_match.group(2))
    # Base case
    elif single_match:
        return (single_match.group(1), single_match.group(2))
    else: # No Partition match!
        raise Exception("partition_line: Partitioning failed!")

def find_errors(thelist):
    """ Search for an 'ERRORIND' in a passed list of strings. Raise an exception if one is found.
    """
    for line in thelist:
        if "ERRORIND" in line:
            raise Exception("find_errors: ERRORIND detected: \n" + str(thelist))

def update_data(datain):
    global GLOBAL_memory_dictionary
    """ Accepts AISG lines, parses them and stores them in a specified dictionary for later comparison.
    """
    for line in datain:
        thekey, theval = partition_line(line)
        GLOBAL_memory_dictionary[thekey] = theval

def frame_send(connection, message):
    """ Sends a specified frame to a specified board_connection and returns TYPE, ID and ARGLIST 
    """
    #global board_connection
    stype, sid, slist = frame_extract_data(message)
    cslist = convert_numbers(slist)
    if stype == None:
        raise Exception("frame_send: Data extraction from frame failed.")
    if stype not in required_typemap:
        raise Exception("frame_send: Invalid message type detected.")
    connection.sendline(message.strip())
    print stype + " message sent."
    return (stype, sid, cslist)

def frame_capture(connection, stype, sid, slist):
    """ Accepts sent TYPE, ID and ARGLIST and captures the resulting AISG responses.
    Returns return TYPELIST, IDLIST and ARGLISTLIST, one entry for each return frame.
    """
    rtypelist, ridlist, rlistlist = ([] for i in range(3))
    expected_types = list(required_typemap[stype])
    accepted_types = list(allowed_typemap[stype])
    while expected_types: # As expected frames come in, the list is truncated. 
        connection.expect("\[.+?\]", expect_timeout)
        rtype, rid, rlist = frame_extract_data(convert_numbers(connection.after))
        if rtype in expected_types: # Expected frame type (hangs until this arrives)
            expected_types.remove(rtype)
            print rtype + " message received."
        elif rtype in accepted_types: # Possible frame type (no hanging, but it's accepted)
            print rtype + " message received."
        elif rtype in required_typemap: # Detected itself
            continue
        elif rtype != stype: #Unexpected, not sent frame detected
            raise Exception("frame_capture: " + rtype + " frame received.")
        rtypelist.append(rtype)
        ridlist.append(rid)
        rlistlist.append(convert_numbers(rlist))
        if any("ERRORIND" in member for member in rlistlist):
            print rlistlist
            raise Exception("frame_capture: ERRORIND detected!")
    return (rtypelist, ridlist, rlistlist)

def store_data(rtypelist, slist, rlistlist):
    """ Decides what information to store based on received frame TYPE and calls update_data 
    Usage: store_data(list[string] rtypelist, list[string] sent_list, list[list[string]] rlistlist, dictionary[str:str] memory)
    """
    global GLOBAL_memory_dictionary
    # for tid, thetype in enumerate(rtypelist):
    #     if thetype == "SETRESPONSE":
    #         update_data(convert_numbers(slist), memory_dictionary)
    #     elif thetype == "ACTIONCOMP":
    #         update_data(rlistlist[tid], memory_dictionary)
    for tid, thetype in enumerate(rtypelist):
        if thetype == "SETRESPONSE":
            update_data(convert_numbers(slist))
        elif thetype == "ACTIONCOMP":
            update_data(convert_numbers(slist))
            
def verify_data(rtypelist, rlistlist):
    """ Takes return typelist, listlist and dictionary and checks whether matches occur.
    Usage: verify_data(list[string] rtypelist, list[list[string]] rlistlist, dictionary[str:str] memory)
    """
    global GLOBAL_memory_dictionary
    #print GLOBAL_mem
    for rid, msgtype in enumerate(rtypelist):
        if msgtype == "GETRESPONSE": # just in case someone else wanders in
            for member in rlistlist[rid]: 
                (thekey, theval) = partition_line(member) # Get key and value
                if thekey in GLOBAL_memory_dictionary:
                    if GLOBAL_memory_dictionary[thekey] != theval:
                        raise Exception("verify_data: Mismatch: " + GLOBAL_memory_dictionary[thekey] + " ::: " + theval)
                    else:
                        print "Match for '" + thekey + "'"
                else:
                    print "Cannot verify '" + thekey + "', no prior data to match '" + theval + "'."

def capture_event(connection, expect_index, action):
    """ Capture a Connect or Disconnect event. Accepts Connection, index of expected device and "dc" or "c" as arguments.
    Throws an exception on timeout.
    Usage: capture_event(PExpect_session connection, int expect_index, string ("c"/"dc"))
    """
    if action == "dc":
        state = "DISCONNECT"
    elif action == "c":
        state = "READY"
    i = connection.expect([pexpect.TIMEOUT, "ALDSTAT: INDEX=" + str(expect_index) + " STATE=" + state], capture_event_timeout)
    if i == 0:
        raise Exception("Expected frame with index " + str(expect_index) + " and state " + state + " didn't arrive!")
    else:
        print("Successfully captured " + str(expect_index) + " " + state + " frame!")

def map_relay_to_index(indices, serials):
    """ Use relay_device_map and passed indices and serials to generate relay -> index map
    Usage: (dictionary[str:int] relay_to_index_map) = map_serial_to_index (list[int] indices, list[string] serials)
    """
    outdict = {}
    for i, ser in enumerate(serials):
        for kser in relay_device_map:
            if convert_numbers(str(ser)) in str(convert_numbers(kser)):
                outdict[relay_device_map[kser]] = indices[i]  # Relay -> Index
    return outdict

def map_index_to_numsub(indices, aldscan_numsub):
    """ Use passed indices and aldscan_numsub to generate index -> index map
    Usage: (dictionary[str:str] index_to_numsub_map) = map_serial_to_index (list[int] indices, list[int] numsubs)
    """
    outdict = {}
    for i, numsub in enumerate(aldscan_numsub):
        outdict[str(indices[i])] = numsub  # Relay -> Index
    return outdict

def map_serial_to_index(serials, indices):
    """ Use passed indices and serials to generate serial -> index map
    Usage: (dictionary[str:int] serial_to_index_map) = map_serial_to_index (list[string] serials, list[int] indices)
    """
    outdict = {}
    for i, serial in enumerate(convert_numbers(serials)):
        outdict[convert_numbers(serial)] = indices[i]  # Relay -> Index
    return outdict

def numsub_process(message):
    """Modifies sent frames based on their NUMSUBS by adding additional entries. Example:
    [ALDERRSTAT: INDEX=2 ALDSUB=1 TILT=40 ->
    [ALDERRSTAT: INDEX=2 ALDSUB=1 TILT=40
     ALDERRSTAT: INDEX=2 ALDSUB=2 TILT=41]
    Usage: (string message) = numsub_process(string message, list GLOBAL_index_numsub_map)"""
    global GLOBAL_index_numsub_map
    numsub_match = re.search(r'ALDERRSTAT:.*?INDEX=(\d+).*', message)
    action_rettilt_match = re.search(r'ACTION.*?INDEX=(\d+).*ALDSUB=(\d+).*TILT=(\d+).*', message)
    get_rettilt_match = re.search(r'GET.*?INDEX=(\d+).*ALDSUB=(\d+).*TILT=(\d+).*', message)
    if numsub_match:
        base_str = ""
        index = numsub_match.group(1)
        for k in range (1, int(GLOBAL_index_numsub_map[index])+1):
            base_str += "ALDERRSTAT: INDEX=" + str(index) + " ALDSUB=" + str(k) + "\n"
        message = re.sub(r'(ALDERRSTAT:.+\n)', base_str, message)
    if action_rettilt_match:
        base_str = ""
        index = action_rettilt_match.group(1)
        tilt = action_rettilt_match.group(3)
        for k in range (1, int(GLOBAL_index_numsub_map[index])+1):
            base_str += "RETTILT: INDEX=" + str(index) + " ALDSUB=" + str(k) + " TILT=" + str(tilt + k - 1) + "\n"
        message = re.sub(r'(RETTILT:.+\n)', base_str, message)
    if get_rettilt_match:
        base_str = ""
        index = get_rettilt_match.group(1)
        tilt = get_rettilt_match.group(3)
        for k in range (1, int(GLOBAL_index_numsub_map[index])+1):
            base_str += "RETTILT: INDEX=" + str(index) + " ALDSUB=" + str(k) + "\n"
        message = re.sub(r'(RETTILT:.+\n)', base_str, message)
    return message

def replace_id(message):
    """Replaces instances of "ID=\d" with a given ID.
    Usage: (string message, int (id + 1)) = replace_id(string message, int id)
    """
    global id_counter
    message = re.sub(r"ID=\d+", "ID=" + str(id_counter), message)
    id_counter += 1
    return message

def handle_download(message, Q):
    """ Searches for SWDLOADREQ ACTION frame. If found, generates an ALDLOADREQ ACTION frame and
    puts it at at the front of the command queue. Note, ID of generated frame will be -1.
    Usage: (new string, new queue) = handle_download(string, queue, GLOBAL_serial_index_map) """
    global GLOBAL_serial_index_map
    SWD_match = re.search(r"SWDLOADREQ:\s*TYPE=(\w+).*?\n", message)
    if SWD_match:
        index = GLOBAL_serial_index_map[convert_numbers("0000DESA092370436")]
        message = re.sub(r"INDEX=\d+", "INDEX=" + index, message)
        newmessage = "[\nMESSAGE: TYPE=ACTION\nTRANSACTION: ID=-1\nALDLOADREQ:INDEX=" + index + " ALDSUB=1 TYPE=" + SWD_match.group(1) + "\n]"
        newmessage = replace_id(newmessage)
        Q.append(newmessage) # Append to right, so it goes next.
    return message, Q

def execute_commands_repeat(connection, command_list, duplicate_list):
    """ Collection for executing repeatable AISG commands.
    """    
    aldind, command_queue = genqueue(command_list)
    command_queue = update_queue(command_queue, command_list[aldind+1:], duplicate_list[aldind+1:])
    while command_queue:
        smessage = numsub_process(command_queue.pop())
        smessage = replace_id(smessage)
        smessage, command_queue = handle_download(smessage, command_queue)
        stype, sid, slist = frame_send(connection, smessage) # Send frame
        rtypelist, ridlist, rlistlist = frame_capture(connection, stype, sid, slist) # Capture all frames
        find_errors(rlistlist)
        store_data(rtypelist, slist, rlistlist) # Update dictionary
        if stype == "GET":
            verify_data(rtypelist, rlistlist)
        print "--------------------------------------------------"
        time.sleep(.2)

def execute_commands_once(connection, command_list):
    """ One-time executing commands, used for setup and ALDSCAN.
    """
#    board_connection = connection
    global GLOBAL_memory_dictionary
    GLOBAL_memory_dictionary = {}
    aldind, command_queue = genqueue(command_list)
    while command_queue:
        smessage = command_queue.pop()
        stype, sid, slist = frame_send(connection, smessage) # Send frame
        rtypelist, ridlist, rlistlist = frame_capture(connection, stype, sid, slist) # Capture all frames
        if any("ALDSCAN" in member for member in slist) and stype == "ACTION":
            aldscan_ids, serial_list, numsub_list = aldscan_extract_info(rlistlist)
            relay_index_map = map_relay_to_index(aldscan_ids, serial_list)
            index_numsub_map = map_index_to_numsub(aldscan_ids, numsub_list)
            serial_index_map = map_serial_to_index(serial_list, aldscan_ids)
            update_data(rlistlist[-1])
        find_errors(rlistlist)
        store_data(rtypelist, slist, rlistlist) # Update dictionary
        if stype == "GET":
            verify_data(rtypelist, rlistlist)
        print "--------------------------------------------------"
        time.sleep(.2)
    return (GLOBAL_memory_dictionary, aldscan_ids, relay_index_map, index_numsub_map, serial_index_map)

if __name__ == "__main__":
    # Ensure that both devices are connected before we start.
    iorelay_command_network(relay_connect, "1off")
    iorelay_command_network(relay_connect, "2off")
    iorelay_command_network(relay_connect, "1on")
    iorelay_command_network(relay_connect, "2on")

    f_once = open(once_commands, 'r+')
    once_list, once_duplicate_list = file_read_blocks(f_once)
    f_repeat = open(repeat_commands, 'r+')
    command_list, duplicate_list = file_read_blocks(f_repeat) 
    board_connection = pexpect.spawn(board_connect_command)
    #board_connection.setecho(False)
    board_connection.logfile_read = sys.stdout
    fout = file('/home/aapollon/aisg_tester_log','w+')
    #board_connection.logfile_read = fout
    #board_connection.logfile = fout

    # global id_counter
    # global GLOBAL_aldscan_ids
    # global GLOBAL_relay_index_map
    # global GLOBAL_index_numsub_map
    # global GLOBAL_serial_index_map
    # id_counter = 0
    # (memory_dictionary_base, GLOBAL_aldscan_ids, GLOBAL_relay_index_map, GLOBAL_index_numsub_map, GLOBAL_serial_index_map) =\
    # execute_commands_once(board_connection, once_list) 
    # for x in range(11):
    #     print "################################################################################"
    #     print "########## GLOBAL ITERATION " + str(x) + " ##########"
    #     print "################################################################################"
    #     print GLOBAL_relay_index_map
    #     # id_counter = execute_commands_repeat(board_connection,ALDSTAT_MESSAGE, [0], newargs, id_counter)
    #     # iorelay_command_network(relay_connect, "2off")
    #     # capture_event(board_connection, int(GLOBAL_relay_index_map['2']), "dc")
    #     # # id_counter = execute_commands_repeat(board_connection,ALDSTAT_MESSAGE, [0], newargs, id_counter)
    #     # iorelay_command_network(relay_connect, "1off")
    #     # capture_event(board_connection, int(GLOBAL_relay_index_map['1']), "dc")
    #     # iorelay_command_network(relay_connect, "1on")
    #     # capture_event(board_connection, int(GLOBAL_relay_index_map['1']), "c")
    #     # iorelay_command_network(relay_connect, "2on")
    #     # capture_event(board_connection, int(GLOBAL_relay_index_map['2']), "c")
        
    #     execute_commands_repeat(board_connection, command_list, duplicate_list)
    #     GLOBAL_memory_dictionary = dict(memory_dictionary_base)
    # board_connection.close()
