#!/usr/bin/env python
"""bcitest is a tool to automate BCI command testing."""
import pexpect
import re
import time
import sys
import argparse
import csv
from copy import deepcopy

re.DOTALL # Period in regexes can match any character, including newline.

VERSION  = 3
BCI_PORT = "7006"
CSV_DELIMITER =","
TEXT_DELIMITER="\""
# Symbol table allows you to change the key symbols
symbol = {'global': '@GLOBAL'
          ,'begintest': '@BEGINTEST'
          ,'new': '@NEW'
          ,'args': '@ARGS'
          ,'wait': '@WAIT'
          ,'timeout': '@TIMEOUT'
          ,'expect': '@EXPECT'
          ,'reject': '@REJECT'
          }
tops = ['global', 'begintest'] # Top level tags
mids = ['new', 'args', 'wait', 'timeout', 'expect', 'reject'] # mid level tags
globalstatebase = {'wait': .1, 'timeout': 10, 'expect': [], 'reject': []}
localstatebase =  {'new': None, 'args': [], 'wait': None, 'timeout': None, 'expect': [], 'reject': []}

def sendcommand(connection, command, args, runargs):
    """Send command to connection."""
    connection.sendline(command + " " + " ".join(args))
    if runargs.verbose == 1 or runargs.verbose >= 3:
        print("Command " + command + " with args [" + " ".join(args)
              + "] sent.")
        
def parseresponse(connection, expect, reject, timeoutval, wait, runargs):
    """Parse response to command, detecting errors."""
    i = connection.expect(['.+\r\n.*?>', pexpect.TIMEOUT], timeout=timeoutval)
    if runargs.verbose == 1 or runargs.verbose >= 3:
        print("Response received.")
    if i == 1:
        return "timeoutfail"
    capture = connection.after
    capture =  '\n'.join(capture.split("\r\n")[:-1])
    if re.search("Unknown command '", capture):
        return "unknowncommand"
    for expectregex in expect: # If any expected regex doesn't match
        if not re.search(expectregex, capture): 
            return ("expectfail", expectregex, capture)
    for rejectregex in reject:  # If any rejected regex matches
        if re.search(rejectregex, capture):
            return ("rejectfail", rejectregex, capture)
    time.sleep(wait)
    return None

def executecommand(connection, gs, ls, runargs):
    """Execute command, including combining global and local state
    and dealing with potential errors that come up."""
    command = ls['new']
    args = ls['args']    
    if command == None:
        print("Attempting to execute command with no specified command. Exiting.")
        sys.exit()
    waitlen = localstate['wait'] or globalstate['wait']    
    timeoutlen = localstate['timeout'] or globalstate['timeout']
    expectlist = localstate['expect'] + globalstate['expect']
    rejectlist = localstate['reject'] + globalstate['reject']

    sendcommand(connection, command, args, runargs)
    resp = parseresponse(connection, expectlist, rejectlist, timeoutlen, waitlen, runargs)
    if resp == "timeoutfail": # Deal with errors
        print("Command " + command + " with args [" + ' '.join(args) + "] has timed out after" + timeoutlen + " seconds. Exiting.")
        sys.exit()
    elif resp == "unknowncommand":
        print("Command " + command + " is not available. Exiting.")
        sys.exit()        
    elif isinstance(resp, tuple) and resp[0] == "expectfail":
        print("Command " + command + " with args [" + ' '.join(args) + "] has not captured the expected"
              + " value " + resp[1] + ".\n")
        print("The full captured response is \n" + resp[2])
        print("\nExiting.")
        sys.exit()        
    elif isinstance(resp, tuple) and resp[0] == "rejectfail":
        print("Command " + command + " with args [" + ' '.join(args) + "] has captured the rejected"
        " value " + resp[1] + ".\n")
        print("The full captured response is \n" + resp[2])
        print("\nExiting.")
        sys.exit()        

def update_global_state(global_state, mid, word):
    if mid == symbol['wait']:
        global_state['wait'] = float(word)
    elif mid == symbol['timeout']:
        global_state['timeout'] = float(word)
    elif mid == symbol['expect']:
        global_state['expect'].append(word)
    elif mid == symbol['reject']:
        global_state['reject'].append(word)
    elif mid in [symbol['args'], symbol['new']]:
        print("Unexpected command execution in global"
              "section. Exiting.")
        sys.exit()

def update_local_state(local_state, mid, word):
    if  mid == symbol['new']:
        local_state['new'] = word
    elif  mid == symbol['args']:
        local_state['args'].append(word) 
    elif  mid == symbol['wait']:
        local_state['wait'] = float(word)
    elif  mid == symbol['timeout']:
        local_state['timeout'] = float(word)
    elif  mid == symbol['expect']:
        local_state['expect'].append(word)
    elif  mid == symbol['reject']:
        local_state['reject'].append(word)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()    
    parser.add_argument("board", help="board address")
    parser.add_argument("file", help="bci command list file")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", default = 0, action="count")
    parser.add_argument("-r", "--repeat", help="set repetitions", default = 1, type=int)
    parser.add_argument("--version", help="print out version and exit",
                        action='version', version='%(prog)s '
                        + str(VERSION))
    args = parser.parse_args()

    for itera in range(args.repeat):
        globalstate = deepcopy(globalstatebase)
        board_connect_command = "telnet " + args.board + " " + BCI_PORT
        if args.verbose == 1 or args.verbose >= 3:
            print("Connecting with \"" + board_connect_command + "\"...") 
        con = pexpect.spawn(board_connect_command)
        if args.verbose > 1:
            con.logfile_read = sys.stdout
        i = con.expect(['login', pexpect.TIMEOUT], timeout=10)
        if i == 1:
            print("Failed to establish a connection with \"" +
                  board_connect_command + "\". Exiting.")
            sys.exit()
        con.sendline('lucent')
        con.expect('assword')
        con.sendline('test')
        con.expect('successful')
        infile = open(args.file, 'r')
        reader = csv.reader(infile, delimiter=CSV_DELIMITER, quotechar=TEXT_DELIMITER)

        # top and mid are used to keep track of parent nodes --
        # top corresponds to @GLOBAL and @BEGINTEST,
        # mid corresponds to every other tag.
        top = None
        mid = None
        for row in reader:
            for word in row:
                word = word.strip()
                if word == "":
                    continue
                elif word in [symbol[x] for x in tops]: # if top-level tag
                    if mid != None and top == symbol['begintest']: # Execute last command when new begins                        
                        executecommand(con, globalstate, localstate, args)
                    top = word
                    mid = None
                elif word == symbol['new']:
                    if mid != None:
                        executecommand(con, globalstate, localstate, args)
                    mid = word
                    localstate = deepcopy(localstatebase)
                elif word in [symbol[x] for x in mids]: # otherwise, if mid-level tag
                    mid = word
                else: # else it's a value
                    if top == symbol['global']:
                        update_global_state(globalstate, mid, word)
                    if top == symbol['begintest']:
                        update_local_state(localstate, mid, word)

        if mid != None:
            executecommand(con, globalstate, localstate, args)
        infile.close()
        con.close()
        if args.verbose == 1 or args.verbose >= 3:
            print("Iteration " + str(itera + 1) + " of " +
                  str(args.repeat) + " completed.") 
    print("\nTest completed, no errors found. Exiting.")
