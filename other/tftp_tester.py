#!/usr/bin/env python

import pexpect

modImage = "das_image_v60"
modImageSize = "0x2000000"

NUMITER = 1000
TFTP_SERVER = "135.112.98.252"
board_connect_command1 = "ssh "
expected_crc = "4284bd26"

connection = pexpect.spawn(board_connect_command)
connection.logfile_read = sys.stdout

match_counter, total_counter = 0
# crc for all blank "crc32 0x01000000 0x2000000 : 59450445
# crc for blank -> written tftp: 4284bd26

for i in range(NUMITER):
    total_counter = total_counter + 1
    connection.sendline("mw.l 0x1000000 0 0x800000")
    connection.expect("uboot")
    connection.sendline("tftp 0x01000000 " + TFTP_SERVER + ":" + modImage)
    connection.expect("Bytes transferred")
    connection.sendline("crc32 0x01000000 0x2000000")
    i = connection.expect("CRC32") 
    crc_match = re.search(r'==> (\w{8})', connection.after) #    CRC32 for 01000000 ... 02ffffff ==> 4284bd26
    crc_val = crc_match.group(1)
    if crc_val== expected_crc:
        match_counter = match_counter + 1
        print "Successful comparison " + match_counter + "/" + total_counter + "."
    else:
        print "Failed comparison " + (total_counter - match_counter) + "/" + total_counter + "."

# modImage=fsblDoesNotExist.bin
# tftp 0x01000000 ${modImage}

# crc32 - checksum calculation
# Usage:
# crc32 address count [addr]
#     - compute CRC32 checksum [save at addr]

# cmp - memory compare
# Usage:
# cmp [.b, .w, .l] addr1 addr2 count

# mw - memory write (fill)
# Usage:
# mw [.b, .w, .l] address value [count]
