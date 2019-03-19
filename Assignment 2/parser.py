import re
INPFILENAME = "fsa.txt"
OUTPFILENAME = "result.txt"
E1 = "E1: A state '%s' is not in set of states"
E2 = "E2: Some states are disjoint"
E3 = "E3: A transition '%s' is not represented in the alphabet"
E4 = "E4: Initial state is not defined"
E5 = "E5: Input file is malformed"
E6 = "E6: FSA is nondeterministic"


def to_reg_exp():
    regexp = parse_file()
    write_file(regexp)
    return


# parses an input file containig FSA structure
# returns [(is there a valid graph), [Error/warning constant] or [regular expression]] 
def parse_file():
    report = [True, ['']]
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
    states = lines[0].split(" ")
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
        report[1] = "{}"
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
            return [False, [E6]]
        graph[trans[0]][trans[1]] = trans[2]
    for transition in lines[4].split(" "):
        trans = transition.split(">")
        if trans[0] not in unordered[trans[2]]:
            unordered[trans[0]].append(trans[2])
            unordered[trans[2]].append(trans[0])
    # checking E2 by BFS of unordered graph
    visited = []
    current = initial
    queue = []
    visited.append(initial)
    while (len([i for i in unordered[current] if i not in visited]) > 0) or len(queue) > 0:
        [queue.append(i) for i in unordered[current] if i not in visited]
        if len(queue) > 0:
            current = queue[0]
            queue.pop(0)
            visited.append(current)
    if len(visited) < len(unordered.keys()):
        return [False, [E2]]
    fsa.close()
    if report[1] != '{}':
        report[1] = kleenes_alg(graph, unordered, states, initial, final)
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


# computes regular expressions for k = -1
# and passes them over to recursive step
# exp = {first state : {second state : [transitions]}}
def kleenes_alg(graph, unordered_graph, states, initial, final):
    print(graph)
    exp = []
    for i in states:
        exp.append([])
        for j in states:
            exp[states.index(i)].append([])
            if j in unordered_graph[i]:
                for transition in graph[i]:
                    if graph[i][transition] != None and j in graph[i][transition]:
                        exp[states.index(i)][states.index(j)].append(transition)
                    exp[states.index(i)][states.index(j)].sort()
                if i == j:
                    exp[states.index(i)][states.index(j)].append('eps')
                if exp[states.index(i)][states.index(j)] == []:
                    exp[states.index(i)][states.index(j)].append('{}')
            elif i == j:
                exp[states.index(i)][states.index(j)].append('eps')
            else:
                exp[states.index(i)][states.index(j)].append('{}')
    # pass to the recursion with k = 0
    for i in range(len(exp)):
        for j in range(len(exp[i])):
            exp[i][j] = '|'.join(exp[i][j])
    regexplist = kleenes_alg_recursion(0, len(states) - 1, exp, states)
    init_to_final = [regexplist[states.index(initial)][states.index(f)] for f in final]
    # print(init_to_final)
    regexp = "|".join(init_to_final)
    return regexp


def kleenes_alg_recursion(k, kmax, prev_exp, states):
    # compute using the update rule
    if k <= kmax :
        # compute for k
        exp = []
        for i in states:
            exp.append([])
            for j in states:
                exp[states.index(i)].append('')
                print(exp)
                exp[states.index(i)][states.index(j)] = '(' + (prev_exp[states.index(i)][k]) + ')(' +       \
                                                        (prev_exp[k][k]) + ')*(' +                          \
                                                        (prev_exp[k][states.index(j)]) + ')|(' +            \
                                                        (prev_exp[states.index(i)][states.index(j)]) + ')'
                print(exp)
        # print(exp)
        return kleenes_alg_recursion(k + 1, kmax, exp, states)
    else:
        return prev_exp


def write_file(report):
    result = open(OUTPFILENAME, "w")
    if report[0] == False:
        result.write("Error:\n")
        result.write(report[1][0])
    else:
        result.write(report[1])
        pass
    result.close()
    return