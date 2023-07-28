#!/usr/bin/python3

color_priority = []
N = 0
Report = []
debug = False
final_csp = None

class Variable:
    def __init__(self, position, number, color):
        self.row = position[0]
        self.column = position[1]

        if number == '*':
            self.number = 0
        else:
            self.number = int(number)

        if color == '#':
            self.color = None
        else:
            self.color = color

        self.number_domain = []
        if self.number == 0:
            self.number_domain = [i for i in range(1, N + 1)]

        self.color_domain = []
        if self.color == None:
            self.color_domain = color_priority[1:]

        self.number_degree = 0
        self.color_degree = 0

        self.number_neighbors = []
        self.color_neighbors  = []

    def cal_degree(self):
        self.number_degree = 0
        for n in self.number_neighbors:
            if n.number == 0:
                self.number_degree = self.number_degree + 1
        self.color_degree = 0
        for c in self.color_neighbors:
            if c.color == None:
                self.color_degree = self.color_degree + 1

    ## add neighbor to neighbor lists
    def add_neighbor(self, is_number, neighbor):
        if is_number:
            self.number_neighbors.append(neighbor)
        else:
            self.color_neighbors.append(neighbor)

    ## assign value to number or color
    def assign(self, value):
        if color_priority.count(value) != 0:
            self.color = value
        else:
            self.number = value

        self.remove_value_from_domain(value)

    ## return True if both number & color have value
    def is_fully_assigned(self):
        if self.number == 0 or self.color == None:
            return False
        return True

    ## return True if unassigned var have an empty domain
    def can_assign(self):
        if self.number == 0 and self.number_domain.__len__() == 0:
            return False

        if self.color == None and self.color_domain == []:
            return False

        return True

    ## remove value from domain
    def remove_value_from_domain(self, value):
        try:
            if color_priority.count(value) != 0:
                self.color_domain.remove(value)
            else:
                self.number_domain.remove(value)
        except:
            ## value is not in the domain
            pass

    def remove_range_value_from_domain(self, is_number, start, to_up):
        if is_number:
            if to_up:
                for i in range(start + 1, N + 1):
                    self.remove_value_from_domain(i)
            else:
                for i in range(1, start):
                    self.remove_value_from_domain(i)
        else:
            if to_up:
                for i in range(color_priority.index(start) + 1, color_priority.__len__()):
                    self.remove_value_from_domain(color_priority[i])
            else:
                for i in range(1, color_priority.index(start)):
                    self.remove_value_from_domain(color_priority[i])

    ## return copy of object
    def copy(self):
        new_var = Variable([self.row, self.column], self.number, self.color)
        new_var.number_domain = self.number_domain.copy()
        new_var.color_domain = self.color_domain.copy()
        return new_var

    def p(self):
        print("pos: " + str(self.row + 1) + ' ' + str(self.column + 1))
        print("number = " + str(self.number) + "   color = " + str(self.color))
        print("number domain: " + str(self.number_domain))
        print("number color : " + str(self.color_domain))

class CSP:
    def __init__(self, state, forward_check_on_init):
        self.state = state

        ## define number neighbors
        ## row
        for row in self.state:
            for r1 in range(N):
                for r2 in range(N):
                    if r1 != r2:
                        row[r1].add_neighbor(True, row[r2])
        ## column
        for col in range(N):
            for r1 in range(N):
                for r2 in range(N):
                    if r1 != r2:
                        self.state[r1][col].add_neighbor(True, self.state[r2][col])

        ## define color neighbors
        ## row
        for row in self.state:
            for col in range(N - 1):
                row[col].add_neighbor(False, row[col + 1])
                row[col + 1].add_neighbor(False, row[col])
        ## column
        for col in range(N):
            for row in range(N - 1):
                self.state[row][col].add_neighbor(False, self.state[row + 1][col])
                self.state[row + 1][col].add_neighbor(False, self.state[row][col])

        ## forward checking for initial state
        self.fc_succeed_on_init = True
        coun = True
        if forward_check_on_init:
            for row in self.state:
                if coun:
                    for col in row:
                        if col.number != 0:
                            fc_succeed = self.forward_checking(col, col.number)
                            if not fc_succeed:
                                self.fc_succeed_on_init = False
                                coun = False
                                break

                        if col.color != None:
                            fc_succeed = self.forward_checking(col, col.color)
                            if not fc_succeed:
                                self.fc_succeed_on_init = False
                                coun = False
                                break
                else:
                    break

    ## return a variable which should assign. base on MRV and degree heuristic
    def get_unassigned_variable(self):
        ## MRV
        min_length = N + color_priority.__len__() + 1
        for row in self.state:
            for col in row:
                if col.number == 0 and col.number_domain.__len__() < min_length:
                    min_length = col.number_domain.__len__()
                if col.color == None and col.color_domain.__len__() < min_length:
                    min_length = col.color_domain.__len__()

        if min_length == N + color_priority.__len__() + 1:
            return None, None

        unassigned_numbers = []
        unassigned_colors  = []
        for row in self.state:
            for col in row:
                if col.number == 0 and col.number_domain.__len__() == min_length:
                    unassigned_numbers.append(col)
                    col.cal_degree()
                if col.color == None and col.color_domain.__len__() == min_length:
                    unassigned_colors.append(col)
                    col.cal_degree()

        ## Degree
        ## always degree of number_neighbors >= color_neighbors
        if unassigned_numbers.__len__() != 0:
            unassigned_numbers.sort(key= lambda x : x.number_degree, reverse=True)
            return unassigned_numbers[0], unassigned_numbers[0].number_domain[:]

        unassigned_colors.sort(key= lambda x : x.color_degree, reverse=True)
        return unassigned_colors[0], unassigned_colors[0].color_domain[:]

    ## forward checking after 'value' assigned to 'variable'
    def forward_checking(self, variable, value):
        ## if assigned value is color: for each neighbor without color, remove color from domain
        if color_priority.count(value) != 0:
            for neighbor in variable.color_neighbors:
                if neighbor.color == None:
                    neighbor.remove_value_from_domain(value)
        ## if assigned value is number: for each neighbor without number, remove number from domain
        else:
            for neighbor in variable.number_neighbors:
                if neighbor.number == 0:
                    neighbor.remove_value_from_domain(value)

        ## remove invalid values because of 'higher card, higher color' condition
        for neighbor in variable.color_neighbors:
            an = False
            if variable.number != 0:
                an = True
            ac = False
            if variable.color != None:
                ac = True
            nn = False
            if neighbor.number != 0:
                nn = True
            nc = False
            if neighbor.color != None:
                nc = True

            number_of_assigned = 0
            if (not nn) and (not nc):
                if an and ac:
                    number_of_assigned = 2
                else:
                    number_of_assigned = 1
            elif nn and nc:
                if an and ac:
                    number_of_assigned = 4
                else:
                    number_of_assigned = 3
            else:
                if an and ac:
                    number_of_assigned = 3
                else:
                    number_of_assigned = 2

            if number_of_assigned == 1:
                if an:
                    if variable.number == N:
                        variable.remove_value_from_domain(color_priority[1])
                        neighbor.remove_value_from_domain(color_priority[-1])
                    elif variable.number == 1:
                        variable.remove_value_from_domain(color_priority[-1])
                        neighbor.remove_value_from_domain(color_priority[1])
                elif ac:
                    if variable.number == color_priority[-1]:
                        variable.remove_value_from_domain(1)
                        neighbor.remove_value_from_domain(N)
                    elif variable.number == color_priority[1]:
                        variable.remove_value_from_domain(N)
                        neighbor.remove_value_from_domain(1)
            elif number_of_assigned == 2:
                if an and ac:
                    if variable.number == N:
                        neighbor.remove_range_value_from_domain(is_number=False, start=variable.color, to_up=True)
                    elif variable.number == 1:
                        neighbor.remove_range_value_from_domain(is_number=False, start=variable.color, to_up=False)
                    if variable.color == color_priority[-1]:
                        neighbor.remove_range_value_from_domain(is_number=True, start=variable.number, to_up=True)
                    elif variable.color == color_priority[1]:
                        neighbor.remove_range_value_from_domain(is_number=True, start=variable.number, to_up=False)
                elif an and nc:
                    if variable.number == N:
                        variable.remove_range_value_from_domain(is_number=False, start=neighbor.color, to_up=False)
                    elif variable.number == 1:
                        variable.remove_range_value_from_domain(is_number=False, start=neighbor.color, to_up=True)
                    if neighbor.color == color_priority[-1]:
                        neighbor.remove_range_value_from_domain(is_number=True, start=variable.number, to_up=False)
                    elif neighbor.color == color_priority[1]:
                        neighbor.remove_range_value_from_domain(is_number=True, start=variable.number, to_up=True)
                elif ac and nn:
                    if neighbor.number == N:
                        neighbor.remove_range_value_from_domain(is_number=False, start=variable.color, to_up=False)
                    elif neighbor.number == 1:
                        neighbor.remove_range_value_from_domain(is_number=False, start=variable.color, to_up=True)
                    if variable.color == color_priority[-1]:
                        variable.remove_range_value_from_domain(is_number=True, start=neighbor.number, to_up=False)
                    elif variable.color == color_priority[1]:
                        variable.remove_range_value_from_domain(is_number=True, start=neighbor.number, to_up=True)
            elif number_of_assigned == 3:
                if an and ac and nn:
                    if variable.number > neighbor.number:
                        neighbor.remove_range_value_from_domain(is_number=False, start=variable.color, to_up=True)
                    else:
                        neighbor.remove_range_value_from_domain(is_number=False, start=variable.color, to_up=False)
                elif an and ac and nc:
                    if color_priority.index(variable.color) < color_priority.index(neighbor.color):
                        neighbor.remove_range_value_from_domain(is_number=True, start=variable.number, to_up=False)
                    else:
                        neighbor.remove_range_value_from_domain(is_number=True, start=variable.number, to_up=True)
                elif an and nn and nc:
                    if variable.number > neighbor.number:
                        variable.remove_range_value_from_domain(is_number=False, start=neighbor.color, to_up=False)
                    else:
                        variable.remove_range_value_from_domain(is_number=False, start=neighbor.color, to_up=True)
                elif ac and nn and nc:
                    if color_priority.index(variable.color) > color_priority.index(neighbor.color):
                        variable.remove_range_value_from_domain(is_number=True, start=neighbor.number, to_up=False)
                    else:
                        variable.remove_range_value_from_domain(is_number=True, start=neighbor.number, to_up=True)


        ## check if unassigned variables domain is not empty
        if not variable.can_assign():
            if debug:
                print("empty domain at : [" + str(variable.row + 1) + ", " + str(variable.column + 1) + "]")
            return False

        ## check if unassigned neighbors domain is not empty
        for neighbor in variable.color_neighbors:
            if not neighbor.can_assign():
                if debug:
                    print("empty domain at : [" + str(neighbor.row + 1) + ", " + str(neighbor.column + 1) + "]")
                return False
        for neighbor in variable.number_neighbors:
            if not neighbor.can_assign():
                if debug:
                    print("empty domain at : [" + str(neighbor.row + 1) + ", " + str(neighbor.column + 1) + "]")
                return False

        return True

    ## return copy of object
    def copy(self):
        new_state = []
        for row in self.state:
            tmp = []
            for col in row:
                tmp.append(col.copy())
            new_state.append(tmp)

        new_csp = CSP(new_state, forward_check_on_init=False)
        return new_csp

    def pp(self):
        for row in self.state:
            for col in row:
                cc = col.color
                if col.color == None:
                    cc = '#'
                print(str(col.number) + cc, end=' ')
            print()

def back_tracking(csp):
    variable, domain_values = csp.get_unassigned_variable()

    ## check if is there any unassign variable or not
    if variable == None:
        return True

    if debug:
        print("\nchoose variable: [" + str(variable.row + 1) + ", " + str(variable.column + 1) + "]")
        print("variable domain: " + str(domain_values))

    for value in domain_values:
        ## take an snapshot of csp if assign value goes wrong
        csp_backup = csp.copy()

        ## assign a value to current variable and remove that value from variable domain
        variable.assign(value)

        if debug:
            print("choose value: " + str(value) + " -> [" + str(variable.row + 1) + ", " + str(variable.column + 1) + "]")

        ## forward checking and modify related variables domain
        fc_succeed = csp.forward_checking(variable, value)

        ## if after forward checking, unassign variables domain is empty, then value for current variable is wrong
        ## and restore csp before assign value to current variable
        if not fc_succeed:
            if debug:
                print("forward checking return Fasle. backtracking...")
            csp = csp_backup
            variable = csp.state[variable.row][variable.column]
            continue

        if debug:
            print("forward checking return True.")

        ## do back_tracking with modified csp
        if not back_tracking(csp):
            if debug:
                print("no answer with " + str(value) + " -> [" + str(variable.row + 1) + ", " + str(variable.column + 1) + "]" + " backtracking...")
            ## restore csp before assign value to current variable
            csp = csp_backup
            variable = csp.state[variable.row][variable.column]
        else:
            final_csp.state[variable.row][variable.column].assign(value)
            report = "assign value " + str(value) + " to variable: [" + str(variable.row + 1) + ", " + str(variable.column + 1) + "]"
            global Report
            Report.insert(0, report)
            return True

    return False

def get_input():
    n = int(input().split(' ')[1])
    ## m = input ...  ## no need
    global N
    N = n

    global color_priority
    color_priority = [i[:] for i in input().split(' ')]
    color_priority.reverse()
    color_priority.insert(0, None)

    initial_state = []
    for i in range(n):
        row = input().split(' ')
        tmp = []
        for j in range(n):
            square = Variable([i, j], row[j][:-1], row[j][-1])
            tmp.append(square)
        initial_state.append(tmp)

    return initial_state


if __name__ == "__main__":
    Input = get_input()

    csp = CSP(Input, forward_check_on_init=True)
    final_csp = csp
    if not csp.fc_succeed_on_init:
        print("No answer")
        quit()

    answer = back_tracking(csp)
    if not answer:
        print("No answer")
        quit()

    for line in Report:
        print(line)

    final_csp.pp()
