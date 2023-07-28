#!/usr/bin/python3
import gc

## K is number of column (from input)
K = 0
## N is number of card for each color (from input)
N = 0

## nodes statistics
generated_nodes = 0
expanded_nodes  = 0

## queue with fifo method
class lifo_queue:
    def __init__(self):
        self.queue = []

    ## remove first element and return
    def get_element(self):
        p = self.queue.pop(self.queue.__len__() - 1)
        return p

    ## add element to queue
    def add_element(self, element):
        self.queue.append(element)

    ## add list of elements to queue
    def add_elements(self, elements):
        for i in range(elements.__len__() - 1, -1, -1):
            self.queue.append(elements[i])

    def is_empty(self):
        if self.queue.__len__() == 0:
            return True
        return False

## node object
class node:
    def __init__(self, state, parent, previous_action, depth):
        self.state = state
        self.actions = []
        self.children = []
        self.parent = parent
        self.previous_action = previous_action
        self.depth = depth
        global generated_nodes
        generated_nodes = generated_nodes + 1

    ## find all posible actions
    def calculate_actions(self):
        actions = []
        for i in range(0, K):
            if self.state[i] != []:
                for j in range(0, K):
                    if i != j:
                        if self.state[j] == []:
                            actions.append([i, j])
                        elif self.state[j][-1][0] > self.state[i][-1][0]:
                            actions.append([i, j])
        return actions

    ## return node if do action 'act'
    def do_action(self, act):
        new_state = [i[:] for i in self.state]

        p = new_state[act[0]].pop(-1)
        new_state[act[1]].append(p)

        return node(new_state, self, act, self.depth + 1)

    ## do all actions in self.actions and return list of nodes
    ## if this func dont call, then we havent self.actions and self.children which means node DID NOT expanded 
    def get_children(self):
        global expanded_nodes
        expanded_nodes = expanded_nodes + 1
        self.actions = self.calculate_actions()
        c = []
        for a in self.actions:
            c.append(self.do_action(a))
        self.children = c.copy()
        return c

    ## check state is goal or not
    def goal_test(self):
        for i in self.state:
            if i != []:
                color = i[0][1]
                for j in i:
                    if j[1] != color:
                        return False
                n = N
                for j in i:
                    if j[0] != n:
                        return False
                    n = n - 1

        return True

## dfs algorithm
## *** input: problem
## *** problem should have this variables and functions:
## **** node.hash : uniq number or string
## **** node.goal_test() : return True if node state is goal and False if not
## **** node.get_children() : return list of nodes that could be reach from current state
def dls(problem, limit):
    frontier = lifo_queue()
    frontier.add_element(problem)

    it = 0
    while not frontier.is_empty():
        current_node = frontier.get_element()

        ## goal_test
        if current_node.goal_test():
            return current_node

        if current_node.depth == limit:
            continue

        if it % 1000 == 0:
            gc.collect()
            print('*', end='')
        it = it + 1

        ## expand current_node
        # print("expanding node with hash: " + str(current_node.hash))
        ## get current_node children and add to frontier
        frontier.add_elements(current_node.get_children())
    
    return None

def get_input():
    global K
    global N
    
    print("Enter inputs:")
    k, m, n = input().split(' ')
    k = int(k)
    m = int(m)
    n = int(n)
    K = k
    N = n

    input_states = []
    for i in range(0, k):
        input_states.append(input())

    limit = int(input("Enter limit start point: "))

    states = []
    for i in input_states:
        if i == '#':
            states.append([])
        else:
            states.append(i.split(' '))
    
    ## convert input to new format
    ## ex: "4y" -> [4, 'y']   or    '#' -> []
    format_states = []
    for i in states:
        temp = []
        for j in i:
            s = [[], []]
            s[1] = j[-1]
            s[0] = int(j[:-1])
            temp.append(s)
        format_states.append(temp)

    return format_states, limit

if __name__ == '__main__':
    Input, limit = get_input()
    print("\nFirst State: ")
    for t in Input:
        print(t)

    problem = node(Input, None, None, 0)
    
    print("\nSearch started!")
    while True:
        ## if you dont have memory limit comment this part for faster search
        gc.collect()

        print("\nTry with limit = " + str(limit))

        a = dls(problem, limit)

        if a != None:
            print("\nSuccess with limit " + str(limit))
            answer_node = a
            break

        print("\nFailed with limit " + str(limit))
        print("Number of generated nodes: " + str(generated_nodes))
        print("Number of expanded  nodes: " + str(expanded_nodes))
        limit = limit + 1

        ## reset statistics
        generated_nodes = 1
        expanded_nodes  = 0

    gc.collect()
    print("\nSearch finished!")
    res = answer_node

    ## create report ...
    result_report = []
    while (answer_node.previous_action != None):
        act = answer_node.previous_action
        answer_node = answer_node.parent
        report = "Move " + str(answer_node.state[act[0]][-1][0]) + answer_node.state[act[0]][-1][1] + " from column " + str(act[0] + 1) + " to column " + str(act[1] + 1)
        result_report.insert(0, report)

    print("\nSearch depth = " + str(result_report.__len__()))
    
    print("\nReport:")
    for r in result_report:
        print(r)

    print("\nNumber of node generated = " + str(generated_nodes))
    print("Number of node expanded  = " + str(expanded_nodes))

    print("\nFinal state:")
    for r in res.state:
        if r == []:
            print('#')
        else:
            for rr in r:
                print(str(rr[0]) + rr[1], end=' ')
            print()
