#!/usr/bin/python
import json
import jsonpickle

class CalRecord:
    axisdata = []
    singdata = []
    
    def __init__(self, name, recid):
        self.name = name
        self.recid = recid

    def add_axis(self, axis):
        self.axisdata.append(axis)

    def add_singular(self, sing):
        self.singdata.append(sing)

    def print_axes(self):
        for k in self.axisdata:
            print(k.axisname + ": " + str(k.axisdata))

    def print_singular(self):
        for k in self.singdata:
            print(k.singname + ": " + str(k.singdata)) 

class Axis:
    def __init__(self, name, data):
        self.axisname = name
        self.axisdata = data

class Singular:
    def __init__(self, name, data):
        self.singname = name
        self.singdata = data


# Read from file
f2 = open('testfile', 'r')
thawed = jsonpickle.decode(f2.read())
f2.close()

thawed.print_axes()
