#!/usr/bin/python
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

class CalRecord:
    
    def __init__(self, name, recid):
        self.name = name
        self.recid = recid
        self.axisdata = []
        self.singdata = []
        
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

    # http://stackoverflow.com/questions/3768895/python-how-to-make-a-class-json-serializable
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
class Axis:
    def __init__(self, name, data):
        self.axisname = name
        self.axisdata = data

class Singular:
    def __init__(self, name, data):
        self.singname = name
        self.singdata = data

# Create object        
Record1 = CalRecord("TXFREQ", "17")
Record1.add_axis(Axis("Frequency", [1,2,3,4,5]))
Record1.add_axis(Axis("Magic Dissipation", [1,2,3,4,7]))
Record1.add_singular(Singular("Who:?", 5))

# Write to file
f = open('testfile', 'w+')
f.write(Record1.to_JSON())
f.close()


