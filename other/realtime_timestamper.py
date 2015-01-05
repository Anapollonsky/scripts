#!/usr/bin/env python
### Usage: ./realtime_timestamper.py [logfile] [output logfile]
### Writes a new logfile, appending the current time to any lines.
### Useful for real-time timestamping of logfiles as they are created.
### Old logfile is not modified.
import sys
import os.path
import time
import datetime

### config
TIME_FORMAT = "%H:%M:%S" 


### main
if __name__ == "__main__":
    ### Basic I/O
    if len(sys.argv) != 3:
        print("Usage: ./realtime_timestamper.py [logfile] [output logfile]")
        sys.exit()
    log_path = sys.argv[1]
    output_path = sys.argv[2]
    if not os.path.isfile(log_path):
        print("Input logfile does not exist. Please run on existing logfile.")
        sys.exit()
    flog = open(log_path, 'r')
    fout = open(output_path, 'w+')
    
    while 1:
        line = flog.readline()
        if not line:
            time.sleep(0.5)
            continue
        else:
            ts = time.time()
            fout.write("## " +
                       datetime.datetime.fromtimestamp(ts).strftime(TIME_FORMAT)
                       + " ##   " + line)
            fout.flush()
            os.fsync(fout)
