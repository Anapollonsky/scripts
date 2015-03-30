#! /usr/bin/python
import pexpect
import time
import sys

con = pexpect.spawn("telnet 135.112.98.16 7006")
# con.logfile_read = sys.stdout
con.expect('ogin')
con.sendline('lucent')
con.expect('assword')
con.sendline('password')
time.sleep(1)

count = 0
iters = 0
itersmax = 1000
for k in range(itersmax):
    con.sendline('/pltf/txpath/fpgawrite 0x204 0x1')
    con.expect('SUCCESS')
    for i in range(7):
        con.sendline('/pltf/bsp/rreg 1 0x3500 0x18')
        con.expect(' 0000 0000 0000 0000')
        val = con.before[-4:-2]
        con.expect('0000 0000 0000 0000 0000 0000 0000') 
        con.expect(' 0000 0000 0000 0000')
        if val == '00':
            count += 1
        iters += 1
    con.sendline('/pltf/txpath/fpgawrite 0x204 0x0')
    con.expect('SUCCESS')
    for i in range(7):
        con.sendline('/pltf/bsp/rreg 1 0x3500 0x18')
        con.expect(' 0000 0000 0000 0000')
        val = con.before[-4:-2]
        con.expect('0000 0000 0000 0000 0000 0000 0000') 
        con.expect(' 0000 0000 0000 0000')
        if val == '00':
            count += 1
        iters += 1

    print(str(count) + "/" + str(iters))

# 11/2716 on old sw

