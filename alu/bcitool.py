#!/usr/bin/env python
""" bcitool.py
Performs indexing and search operations on BCI commands. Run bcitool.py help for more information.
"""
import pickle
import pexpect
import re
import collections
import time
import sys
import pprint
import os
import textwrap

re.DOTALL

BCI_DIR = os.environ['HOME'] + "/.bcitool/"

TREE_FILE = BCI_DIR + "bci.pkl"

BCI_PORT = "7006"
TEXTWRAP = 80
VERSION = 2
# def dicts(t): return {k: dicts(t[k]) for k in t} https://gist.github.com/hrldcpr/2012250

def tree(): #http://stackoverflow.com/questions/3009935/looking-for-a-good-python-tree-data-structure
    """A tree is a dictionary with a dictionary as a default inner value"""
    return collections.defaultdict(tree)

def separate_node_title2(stringin):
    """Separate bci command name and description"""
    separate_match = re.search("(\w+)\s+(.*)", stringin)
    return (separate_match.group(1), separate_match.group(2))

def separate_node_title3(stringin):
    """Separate bci command path, name and description"""
    separate_match = re.search("(.*)\|\|\|(\w+)\|\|\|(.*)", stringin)
    return (separate_match.group(1), separate_match.group(2), separate_match.group(3))

def build_tree(connection, tree_root, tree_cur):
    """Recursively navigate the BCI interface and build internal database, a tree in
    the form of a recursive dictionary"""
    connection.sendline('ls')
    time.sleep(.1)
    connection.expect('.+\r\n.*?>')
    lsret = connection.after
    command_list = [x.strip() for x in lsret.split("\r\n")[2:-1]] # list of available commands/directories
    path = re.search("(.*)>", lsret.split("\r\n")[-1]).group(1) # current path, extracted from ()> prompt
    if path == "":
        path = "/"
    for member in command_list:
        if "..." in member:  # Some ...'s in the BCI ruin the regexes
            continue
        if len(member.split(' ')) == 1:
            name = member
            desc = ""
        else:
            (name, desc) = separate_node_title2(member)
        if path == "/":
            nodename = path + "|||" + name + "|||" + desc
        else:
            nodename = path + "/|||" + name + "|||" + desc
        if re.search("^>", member): # tree node
            tree_cur[nodename] = {}
            connection.sendline("cd " + name)
            connection.expect("/.*>")
            build_tree(connection, tree_root, tree_cur[nodename])
            connection.sendline("cd "+ path)
            connection.expect(">")
        else:
            tree_cur[nodename] = 1
    if (tree_root == tree_cur) :
        connection.close()

def is_dictionary(x):
    """IS THIS A DICTIONARY?!?!"""
    if isinstance(x, dict):
        return True
    else:
        return None

def search_tree(tree_root, tree_cur, results, phrase, search_case_sens, search_name, search_descr):
    """ Performs recursive searching through a local tree, adding matching entries to a list and returning it
in the format [(str path, str name, str description, bool isdict?)] (list of tuples of str,str,str,bool)
"""
    for key in tree_cur:
        is_dict = False
        if is_dictionary(tree_cur[key]):
            is_dict = True
        fini = False
        (path_string, name, descr) = separate_node_title3(key)
        if search_case_sens:
            if search_name and phrase in name:
                results.append((path_string, name, descr, is_dict))
                fini = True
            if search_descr and phrase in descr and fini == False:
                results.append((path_string, name, descr, is_dict))
        else:
            if search_name and phrase.upper() in name.upper():
                results.append((path_string, name, descr, is_dict))
                fini = True
            if search_descr and phrase.upper() in descr.upper() and fini == False:
                results.append((path_string, name, descr, is_dict))
        if is_dict == True:
            search_tree(tree_root, tree_cur[key], results, phrase, search_case_sens, search_name, search_descr)
    if tree_cur == tree_root:
        return results

def print_search_results(results):
    """Prints out a given list of search results in the format (str path, str name, str description, bool isdict?)
"""
    if (results == []):
        print("No results found!")
        return
    dirhead = "**"
    orphanhead = "  "
    (lens_0, lens_1, lens_2) = ([], [], [])
    for k in results:
        numslash = k[0].count("/")
        lens_0.append(len(k[0]) + 2 * (numslash - 1))
        lens_1.append(len(k[1]))
        lens_2.append(len(k[2]))
    maxlen_0 = reduce(max, lens_0)
    maxlen_1 = reduce(max, lens_1)
    maxlen_2 = reduce(max, lens_2)
    for k in results:
        numslash = k[0].count("/")
        if k[3] == True:
            head = dirhead
        else:
            head = orphanhead
        print("  " * (numslash - 1) + head + "  " + k[0] + " "*(2 + maxlen_0 - len(k[0]) - (2*numslash-1)) + k[1] + " " * (2 + maxlen_1 - len(k[1])) + k[2])

def check_tree_file():
    if not os.path.isfile(TREE_FILE):
        print "No indexed data! Exiting."
        sys.exit()


if __name__ == "__main__":
    args = sys.argv
    ## startup
    if not os.path.exists(BCI_DIR):
        os.makedirs(BCI_DIR)
    # Initial helping
    if len(args) == 1:
        out1 = "bcitool allows for quick search of Alcatel-Lucent BCI commands. The BCI menus are first indexed, the resulting database stored locally. Search commands are made available to find the desired command quickly. To find out how to use a certain command, use the commands below, e.g. 'bcitool help index'"
        out2 = """

Commands:
index -- Connects to a board and begins indexing the bci commands.
search -- Perform a basic search on the indexed commands.
dump -- Print out all nodes for use with external programs like "grep".
"""
        print textwrap.fill(out1,TEXTWRAP) + out2                
    ## indexing
    elif args[1] == "index" or args[1] == "i":
        BOARD_IP = args[2]
        print("Indexing files on " + BOARD_IP + "...")
        board_connect_command = "telnet " + BOARD_IP + " " + BCI_PORT
        con = pexpect.spawn(board_connect_command)        
        if "-v" in args:
            con.logfile_read = sys.stdout
            args.remove("-v")
        if "--verbose" in args:
            con.logfile_read = sys.stdout            
            args.remove("--verbose")
        bcitree = tree()
        con.expect('login')
        con.sendline('lucent')
        con.expect('assword')
        con.sendline('test')
        con.expect('successful')
        build_tree(con, bcitree, bcitree)
        output = open(TREE_FILE, 'w+b')
        pickle.dump(bcitree, output)
        output.close()
        print("Index completed!")

    ## searching
    elif args[1] == "grep" or args[1] == "search":
        check_tree_file()
        searchdescr = True
        searchtitles = True
        searchcase = False
        if "--case-sensitive" in args:
            searchcase = True
            args.remove("--case-sensitive")
        if "-c" in args:
            searchcase = True
            args.remove("-c") 
        if "--titles-only" in args:
             searchdescr = False
             args.remove("--titles-only")
        if "-t" in args:
            searchdescr = False
            args.remove("-t")
        if "--descriptions-only" in args:
            searchtitles = False
            args.remove("--descriptions-only")
        if "-d" in args:
            searchtitles = False
            args.remove("-d")            
        infile = open(TREE_FILE, 'r+')
        bcitree = pickle.load(infile)
        infile.close()
        search_results = search_tree(bcitree, bcitree, [], args[2], searchcase, searchtitles, searchdescr)
        print("Printing search results for " + args[2] + "...")
        print_search_results(search_results)

    ## dumping
    elif args[1] == "dump":
        check_tree_file()
        infile = open(TREE_FILE, 'r+')
        bcitree = pickle.load(infile)
        infile.close()
        search_results = search_tree(bcitree, bcitree, [], "", False, True, True)
        print_search_results(search_results)

    # version
    elif args[1] == "-v" or args[1] == "--version":
        print "bcitool v" + str(VERSION)

    ## helping
    elif len(args) == 1 or args[1] == "help":
        if len(args) == 2:
            out1 = "bcitool allows for quick search of Alcatel-Lucent BCI commands. The BCI menus are first indexed, the resulting database stored locally. Search commands are made available to find the desired command quickly. To find out how to use a certain command, use the commands below, e.g. 'bcitool help index'"
            out2 = """

Commands:
index -- Connects to a board and begins indexing the bci commands.
search -- Perform a basic search on the indexed commands.
dump -- Print out all nodes for use with external programs like "grep".
"""
            print textwrap.fill(out1,TEXTWRAP) + out2        

        elif args[2] == "index":
            out1 = "'bcitool index|i [ipaddress] [-v|--verbose]' connects to either the hardcoded or the given board address, enters the bci menu, and begins indexing all available commands. The commands are saved to a local file for use by the search facilities. -v prints out the progress of the indexer during the operation, recommended for ensuring correct functionality. Note, if the bci commands are unreachable (due to launch being off, for example), this will fail!"
            print textwrap.fill(out1, TEXTWRAP)

        elif args[2] == "search":
            out1 = "'bcitool search|grep keyword [--case-sensitive|-c] [--titles-only|-t] [--descriptions-only|-d]' searches the local database for the given keyword. -c makes the search case-sensitive, -t only searches command titles, and -d only searches command descriptions. Default is case insensitive search of both titles and descriptions. The path is not included in the search."
            print textwrap.fill(out1, TEXTWRAP)

        elif args[2] == "dump":
            out1 = "'bcitool dump' flattens and prints out the internal command database. This command can be used effectively with external tools like 'grep' and so forth, in particular for regular expression searches."
            print textwrap.fill(out1, TEXTWRAP)
