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

re.DOTALL
VERSION  = 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--version", help="print version and exit", action="store_true")
    parser.add_argument("board", help="board address")
    parser.add_argument("file", help="bci command list file")
    args = parser.parse_args()


    if args.version:
        print("bcitest version " + VERSION); 
        
