#!/usr/bin/python3

## K is number of columns (from input)
K = 0
## colors is list of all colors (generate from input)
colors = []
## N is number of card for each color (from input)
N = 0

## nodes statistics
generated_nodes = 0
expanded_nodes  = 0

## rates for point
rate_satisfying = 100
rate_higher     = 10
rate_coloring   = 10   # ***** this should be lower than rate_satisfying
rate_cost       = 33

## queue with sort when add element
class priority_queue:
    def __init__(self):
        self.queue = []

    ## remove first element and return
    def get_element(self):
        p = self.queue.pop(0)
        return p

    ## add element to end of queue
    def add_element(self, element):
        self.queue.append(element)
        self.queue.sort(reverse=True, key=self.sort_queue)

    def is_empty(self):
        if self.queue.__len__() == 0:
            return True
        return False

    def sort_queue(self, node):
        return node.point

## node object
class node:
    def __init__(self, state, parent, previous_action, cost):
        self.state = state
        self.actions = []
        self.cost = cost
        self.children = []
        self.parent = parent
        self.previous_action = previous_action
        self.hash = hash(str(self.state))
        self.point = 0
        self.calculate_point()
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

        return node(new_state, self, act, self.cost + 1)

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

    ## estimate how many actions left to goal
    def calculate_point(self):
        point = 0

        ## Method 1: satisfying cards
        for c in colors:
            column_number = -1
            for s in range(0, K):
                if self.state[s] != []:
                    if self.state[s][0][0] == N and self.state[s][0][1] == c:
                        column_number = s
                        point = point + N * rate_satisfying
                        break

            if column_number == -1:
                continue

            for i in range(N - 1, 0, -1):
                try:
                    if self.state[column_number][N - i][0] == i and self.state[column_number][N - i][1] == c:
                        point = point + i * rate_satisfying
                    else:
                        break
                except:
                    break

        ## Method 2: choose higher card
        for s in self.state:
            if not s.__len__() < 2:
                if s[-2][0] < s[-1][0]:
                    point = point - (s[-1][0] - s[-2][0]) * rate_higher

        ## Method 3: choose better color
        for s in self.state:
            if not s.__len__() < 2:
                if s[-2][1] == s[-1][1]:
                    point = point - rate_coloring

        ## Method 4: choose lower cost
        point = point - self.cost * rate_cost

        self.point = point

def A_star(problem):
    frontier = priority_queue()
    frontier.add_element(problem)
    explored = []

    it = 0
    while not frontier.is_empty():
        ## get first element of queue which have the minimum cost + estimated_actions
        current_node = frontier.get_element()

        ## check if node explored or not
        if explored.count(current_node.hash) != 0:
            continue

        if it % 1000 == 0:
            print('*', end='')
        it = it + 1

        ## expand current_node and add to explored list
        # print("expanding node with hash: " + str(current_node.hash))
        explored.append(current_node.hash)
        if current_node.goal_test():
            return current_node
        else:
            ## get current_node children
            ch = current_node.get_children()
            ## add each child to frontier if child wan not explored
            for c in ch:
                if explored.count(c.hash) == 0:
                    ## priority_queue object sort immedietly if add new element (base on node.cost + node.estimated_actions)
                    frontier.add_element(c)
                    ## frontier.sort()
    
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

    global colors
    for f in format_states:
        for s in f:
            if colors.count(s[1]) == 0:
                colors.append(s[1])
    # print(colors)

    return format_states

if __name__ == '__main__':
    Input = get_input()
    print("\nFirst State: ")
    for t in Input:
        print(t)

    problem = node(Input, None, None, 0)
    
    print("\nSearch started!")
    answer_node = A_star(problem)
    print("\nSearch finished!")
    import gc
    gc.collect()
    res = answer_node

    if answer_node == None:
        print("Javab nadareh!")
        quit()

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
