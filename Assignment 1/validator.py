import re
INPFILENAME = "fsa.txt"
OUTPFILENAME = "result.txt"
E1 = "E1: A state '%s' is not in set of states"
E2 = "E2: Some states are disjoint"
E3 = "E3: A transition '%s' is not represented in the alphabet"
E4 = "E4: Initial state is not defined"
E5 = "E5: Input file is malformed"
COMPLETE = ("FSA is incomplete", "FSA is complete")
W1 = "W1: Accepting state is not defined"
W2 = "W2: Some states are not reachable from initial state"
W3 = "W3: FSA is nondeterministic"

def validate_fsa():
    fsa = parse_file()
    write_file(fsa)
    return 

# parses an input file containig FSA structure
# gives output in the form [(is there a valid graph), ]
def parse_file():
    report = [True, {'complete': True, 'w1': False, 'w2': False, 'w3': False}]
    fsa = open(INPFILENAME, "r")
    lines = [line.strip().replace(" ", "") for line in fsa.readlines()]
    # checking file format
    if not check_file_format(lines):
        return [False, [E5]]

    lines[0] = lines[0].replace("states={", "").replace(",", " ").replace("}", "")
    lines[1] = lines[1].replace("alpha={", "").replace(",", " ").replace("}", "")
    lines[2] = lines[2].replace("init.st={", "").replace(",", " ").replace("}", "")
    lines[3] = lines[3].replace("fin.st={", "").replace(",", " ").replace("}", "")
    lines[4] = lines[4].replace("trans={", "").replace(",", " ").replace("}", "")

    # making a graph of the form {'node':{'input':'result node'}}
    # and another (unordered) graph of the form {'node':['adjacent nodes']}
    # adding nodes
    graph = dict.fromkeys(lines[0].split(" "))
    unordered = dict.fromkeys(lines[0].split(" "))
    for key in unordered.keys():
        unordered[key] = []
    for key in graph.keys():
        graph[key] = dict.fromkeys(lines[1].split(" "))
    # reading initial states
    initial = lines[2]
    if initial is "":
        return [False, [E4]]
    if initial not in graph.keys():
        return [False, [E1 % initial]]
    # readong final states
    final = lines[3].split(" ")
    if final == ['']:
        report[1]['w1'] = True
    else:
        for state in final:
            if state not in graph.keys():
                return [False, [E1 % state]]
    # adding transitions to the graph
    for transition in lines[4].split(" "):
        trans = transition.split(">")
        if trans[0] not in graph.keys():
            return [False, [E1 % trans[0]]]
        if trans[2] not in graph.keys():
            return [False, [E1 % trans[2]]]
        if trans[1] not in graph[trans[0]].keys():
            return [False, [E3 % trans[1]]]
        if graph[trans[0]][trans[1]] is not None:
            report[1]['w3'] = True
        graph[trans[0]][trans[1]] = trans[2]
    for transition in lines[4].split(" "):
        trans = transition.split(">")
        if trans[0] not in unordered[trans[2]]:
            unordered[trans[0]].append(trans[2])
            unordered[trans[2]].append(trans[0])
    # checking E2 by BFS of unordered graph
    visited = []
    current = initial
    visited.append(initial)
    while (len([i for i in unordered[current] if i not in visited]) > 0):
        [visited.append(i) for i in unordered[current] if i not in visited]
    if len(visited) < len(unordered.keys()):
        return [False, [E2]]
    # checking completeness
    for node in graph.keys():
        for transition in graph[node].keys():
            if graph[node][transition] == None:
                report[1]['complete'] = False
    # checking W2 by BFS of the ordered graph
    visited = []
    current = initial
    visited.append(initial)
    while (len([i for i in list(graph[current].values()) if i not in visited]) > 0):
        [visited.append(i) for i in list(graph[current].values()) if i not in visited]
    for node in graph.keys():
        if node not in visited:
            report[1]['w2'] = True
    fsa.close()
    return report

# checks the file format using regular expressions
def check_file_format(lines):
    l0 = re.match("states=\{([a-zA-Z0-9]*[,]*)+\}", lines[0])
    l1 = re.match("alpha=\{([a-zA-Z_0-9]*[,]*)+\}", lines[1])
    l2 = re.match("init\.st=\{([a-zA-Z_0-9]*[,]*)*\}", lines[2])
    l3 = re.match("fin\.st=\{([a-zA-Z_0-9]*[,]*)*\}", lines[3])
    l4 = re.match("trans=\{(([a-zA-Z_0-9]*)>([a-zA-Z_0-9]*)>([a-zA-Z_0-9]*)[,]*)+\}", lines[4])
    if l0 and l1 and l2 and l3 and l4:
        return True
    else:
        return False

def write_file(report):
    result = open(OUTPFILENAME, "w")
    if report[0] == False:
        result.write("Error:\n")
        result.write(report[1][0])
    else:
        result.write(COMPLETE[report[1]['complete']])
        if report[1]['w1'] == True or report[1]['w2'] == True or report[1]['w3'] == True:
            result.write("\nWarning:")
        if report[1]['w1'] == True:
            result.write('\n' + W1)
        if report[1]['w2'] == True:
            result.write('\n' + W2)
        if report[1]['w3'] == True:
            result.write('\n' + W3)
    result.close()
    return