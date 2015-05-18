
from collections import namedtuple, defaultdict, deque


# Will be assuming that times are from 0-100, with stopover time being 10. Cities are strings.

city = namedtuple("city", ["name", "flights"])
flight = namedtuple("flight", ["tstart", "tstop", "cstart", "cstop"])
pathnode = namedtuple("pathnode", ["last", "time"])

a = city('a', [])
b = city('b', [])
c = city('c', [])

flights = [flight(10, 40, a, b),
           flight(55, 80, b, c),
           flight(40, 90, a, c)]

for flight in flights:
    flight.cstart.flights.append(flight)

def shortest_path(citya, cityb):
    shortest_paths = {citya.name: pathnode(None, 0)}
    queue = deque()
    queue.append(citya)

    while queue:
        print(shortest_paths)
        latest = queue.pop()
        if latest == cityb:
            path = [latest]
            parent = shortest_paths[latest.name].last
            while(parent):
                path.append(parent)
                parent = shortest_path[parent.name]
            return path
        arrive_time = shortest_paths[latest.name].time % 100
        for flight in latest.flights:
            if arrive_time + 10 < flight.tstart:
                best_time = flight.tstop
            else:
                best_time = flight.tstop + 100
            if (flight.cstop.name in shortest_paths and
                    best_time < shortest_paths[flight.cstop.name]):
                shortest_paths[flight.cstop.name] = pathnode(latest, best_time)
            elif flight.cstop.name not in shortest_paths:
                shortest_paths[flight.cstop.name] = pathnode(latest, best_time)
                queue.append(flight.cstop)
print(shortest_path(a, b))
