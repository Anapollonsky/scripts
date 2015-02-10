#!/usr/bin/env python

import pexpect
import re
import collections
import time
import sys
import pprint
import os
import textwrap
import argparse
import csv

re.DOTALL

VERSION  = 1
BCI_PORT = "7006"

symbol = {'global': '@GLOBAL'
          ,'begintest': 'BEGINTEST'
          ,'new': '@NEW'
          ,'args': '@ARGS'
          ,'wait': '@WAIT'
          ,'timeout': '@TIMEOUT'
          ,'expect': '@EXPECT'
          ,'reject': '@REJECT'
          }

globalstate = {'wait': None, 'timeout': None, 'expect': [], 'reject': []}
localstatebase =  {'new': None, 'args': None, 'wait': None, 'timeout': None, 'expect': [], 'reject': []}

def sendcommand(connection, command, args):
    """Deliver command to connection."""
    connection.sendline(command + " " + ' '.join(args))

def parseresponse(connection, expect, reject, TIMEOUT, wait):
    """Parse response to command."""
    i = connection.expect('.+\r\n.*?>', timeout=TIMEOUT)
    if i == 1:
        return "timeoutfail"
    capture = connection.after
    capture =  '\n'.join(capture.split("\r\n")[:-1])
    for expectregex in expect:
        if not re.search(expectregex, capture):
            return ("expectfail", expectregex, capture)
    for rejectregex in reject:
        if re.seach(rejectregex, capture):
            return ("rejectfail", rejectregex, capture)
    time.sleep(wait)
    return None

def executecommand(connection, gs, ls):
    if ls['new'] == None:
        print("Attempting to execute command with no specified command. Exiting.")
        sys.exit()
    if localstate['wait'] != None:
        waitlen = localstate['wait']
    else:
        waitlen = globalstate['wait']
    if localstate['timeout'] != None:
        timeoutlen = localstate['timeout']
    else:
        timeoutlen = globalstate['timeout']
    if localstate['expect'] != []:
        expectlist = localstate['expect']
    else:
        expectlist = globalstate['expect']
    if localstate['reject'] != []:
        rejectlist = localstate['reject']
    else:
        rejectlist = globalstate['reject']        

    sendcommand(connection, command, args)
    resp = parseresponse(connection, expectlist, rejectlist, timeoutlen, waitlen)
    if resp == "timeoutfail":
        print("Command " + command + " with args [" + args + "] has timed out after"
              + timeoutlen + " seconds. Exiting.")
        sys.exit()
    elif isinstance(resp, tuple) and resp[0] == "expectfail":
        print("Command " + command + " with args [" + args + "] has not captured the expected"
              + " value " + resp[1] + ".\n")
        print("The full captured response is \n" + resp[2])
        print("Exiting.")
        sys.exit()        
    elif isinstance(resp, tuple) and resp[0] == "rejectfail":
        print("Command " + command + " with args [" + args + "] has captured the rejected"
        " value " + resp[1] + ".\n")
        print("The full captured response is \n" + resp[2])
        print("Exiting.")
        sys.exit()        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--version", help="print version and exit", action="store_true")
    # parser.add_argument("board", help="board address")
    parser.add_argument("file", help="bci command list file")
    args = parser.parse_args()

    if args.version:
        print("bcitest version " + VERSION); 

    infile = open(args.file, 'r')
    reader = csv.reader(infile, delimiter=',', quotechar='|')
    top = None
    mid = None
    for row in reader:
        for word in row:
            if word == symbol['global']:
                top = symbol['global']
            if word == symbol['begintest']:
                top = symbol['begintest']                
            elif word == symbol['new']:
                if mid == symbol['new']:
                    executecommand(conn, globalstate, localstate)                    
                mid = symbol['new']
                localstate = dict(localstatebase)
            else:
                if top == symbol['global']:
                    if mid == symbol['wait']:
                        globalstate['wait'] = int(word)
                    elif  mid == symbol['timeout']:
                        globalstate['timeout'] = int(word)
                    elif  mid == symbol['expect']:
                        globalstate['expect'].append(word)
                    elif  mid == symbol['reject']:
                        globalstate['reject'].append(word)
                        
                if top == symbol['begintest']:
                    if  mid == symbol['new']:
                        localstate['new'] = word
                    elif  mid == symbol['args']:
                        localstate['args'].append(word)                                            
                    elif  mid == symbol['wait']:
                        localstate['wait'] = int(word)
                    elif  mid == symbol['timeout']:
                        localstate['timeout'] = int(word)
                    elif  mid == symbol['expect']:
                        localstate['expect'].append(word)
                    elif  mid == symbol['reject']:
                        localstate['reject'].append(word)
            
