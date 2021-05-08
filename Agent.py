import random
from copy import copy


OK = 1
NO_GOOD = 2
CONNECTION_REQUEST = 3
CONNECTION_SUCCESSFUL = 4
INDIRECT = 5
NO_SOLUTION = 6


class Agent:
    def __init__(self, index, options, verbose=False):
        self.index = index
        self.options = options
        self.neighbors = []
        self.indirect_neighbors = []
        self.number = None
        self.agent_view = []
        self.no_goods = []
        self.messages = []
        self.no_sol = False
        self.verbose = verbose

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def message(self, message):
        self.print_info(message)
        self.messages.append(message)

    def process_messages(self, initial_assignment=None):
        self.print_info('=' * 100)
        self.print_info(f'Processing Agent {self.index}')
        self.print_info('=' * 100)

        if self.number is None:
            # Assign self random number
            if initial_assignment is not None:
                self.number = initial_assignment
            else:
                self.number = random.choice(self.options)
            self.print_info(f'Agent {self.index} assigned itself {self.number}')
            # Send all neighbors with lower priority current number
            for neighbor in self.neighbors:
                if neighbor.index > self.index:
                    self.print_info(f'Sent agent {neighbor.index} message {(self.index, self.number)}')
                    neighbor.message((OK, (self.index, self.number)))

        if self.no_sol:
            self.messages = []
            return

        # Process received messages
        for message_type, message_content in self.messages:
            # Process Ok? Messages
            if message_type == OK:
                self.print_info(f'Agent {self.index} processing ok message {message_content}')
                agent_index, updated_number = message_content
                updated = False
                for i in range(len(self.agent_view)):
                    if self.agent_view[i][0] == agent_index:
                        self.agent_view[i] = (agent_index, updated_number)
                        updated = True
                        break
                if not updated:
                    self.agent_view.append((agent_index, updated_number))
                self.print_info(f'Agent {self.index} agent_view is now {self.agent_view}')
                self.check_agent_view()
                continue
            if message_type == NO_GOOD:
                source_index, no_good = message_content
                self.print_info(f'Agent {self.index} processing no_good {no_good}')
                self.no_goods.append(no_good)
                new_connections = set(x[0] for x in no_good) - (set(
                    x[0] for x in self.indirect_neighbors).union(set(x.index for x in self.neighbors)).union(
                    {self.index}))
                for index in new_connections:
                    if len(self.neighbors):
                        self.print_info(f'Agent {self.index} sending connection_request to Agent {index} through Agent '
                                        f'{self.neighbors[0].index}')
                        self.neighbors[0].message((CONNECTION_REQUEST, (self.index, index, [self.index], [self.index]
                                                                          )))
                    else:
                        print('ERROR: Agent has no neighbors')
                        exit()
                self.check_agent_view()
                sent = False
                for agent in self.neighbors:
                    if agent.index == source_index:
                        agent.message((OK, (self.index, self.number)))
                        sent = True
                        break
                if not sent:
                    for index, path in self.indirect_neighbors:
                        if index == source_index:
                            self.send_indirect(path, (OK, (self.index, self.number)))
                            sent = True
                            break
                if not sent:
                    print('ERROR: Source Index is not a neighbor')
                    exit()
                continue
            if message_type == INDIRECT:
                path, message = message_content
                found = False
                for agent in self.neighbors:
                    if agent.index == path[0]:
                        found = True
                        if len(path) == 1:
                            agent.message(message)
                        else:
                            agent.message((INDIRECT, (path[1:], message)))
                        break
                if not found:
                    print(f'ERROR: Agent missing on path {path}')
                    exit()
                continue
            if message_type == CONNECTION_REQUEST:
                self.print_info(f'Agent {self.index} processing connection_request')
                source_index, target_index, path, visited = message_content
                if self.index == target_index:
                    self.indirect_neighbors.append((source_index, path[::-1]))
                    for agent in self.neighbors:
                        if agent.index == path[-1]:
                            agent.message((INDIRECT, (path[::-1][1:], (CONNECTION_SUCCESSFUL,
                                                                         [*path[1:], self.index]))))
                    self.send_indirect(path[::-1], (OK, (self.index, self.number)))
                    continue
                if self.index == source_index:
                    print(f'ERROR: Connection Request Failed, '
                          f'No Path between Agent {source_index} and Agent {target_index}')
                    exit()
                sent = False
                for agent in self.neighbors:
                    if agent.index not in visited:
                        self.print_info(f'Agent {self.index} transfering connection_request with target Agent {target_index}'
                              f' to Agent {agent.index}')
                        agent.message((CONNECTION_REQUEST, (source_index, target_index, [*path, self.index],
                                                              [*visited, self.index])))
                        sent = True
                if not sent:
                    for agent in self.neighbors:
                        if agent.index == path[-1]:
                            self.print_info(
                                f'Agent {self.index} transfering connection_request with target Agent {target_index}'
                                f' to Agent {agent.index}')
                            agent.message((CONNECTION_REQUEST, (source_index, target_index,
                                                                  path[:-1], [*visited, self.index])))
                            sent = True
                if not sent:
                    print('ERROR: Connection Request failed unexpectedly')
                    exit()
                continue
            if message_type == CONNECTION_SUCCESSFUL:
                path = message_content
                index = path[-1]
                self.indirect_neighbors.append((index, path))
                self.print_info(f'Connection between Agent {self.index} and Agent {index} successful')
                continue
            if message_type == NO_SOLUTION:
                self.no_sol = True
                for agent in self.neighbors:
                    if not agent.no_sol:
                        agent.message((NO_SOLUTION, None))
                break
            print('ERROR: Invalid message type')
            exit()
        self.messages = []

    def check_agent_view(self):
        if not self.is_consistent(self.number):
            self.print_info(f'Agent {self.index} with number {self.number} is inconsistent with agent_view {self.agent_view}')
            new_value = None
            for number in self.options:
                if self.is_consistent(number):
                    new_value = number
                    break
            if new_value is None:
                self.print_info(f'Agent {self.index} has no value consistent with agent_view {self.agent_view}'
                                f' - Backtracking')
                self.backtrack()
            else:
                self.print_info(f'Agent {self.index} assigned new value {new_value}')
                self.number = new_value
                for neighbor in self.neighbors:
                    if neighbor.index > self.index:
                        neighbor.message((OK, (self.index, self.number)))
                for index, path in self.indirect_neighbors:
                    if index > self.index:
                        self.send_indirect(path, (OK, (self.index, self.number)))
        else:
            self.print_info(f'Agent {self.index} with number {self.number} is consistent with agent_view {self.agent_view}')

    def backtrack(self):
        # More efficient versions of ABT try to find a minimal no_good here
        no_good = copy(self.agent_view)

        if len(no_good) == 0:
            for agent in self.neighbors:
                agent.message((NO_SOLUTION, None))
            return

        max_index, corresponding_number = max(no_good, key=lambda p: p[0])
        res_agent = None
        res_agent_path = None
        for agent in self.neighbors:
            if agent.index == max_index:
                res_agent = agent
                break
        if res_agent:
            self.print_info(f'Agent {self.index} sending no_good {no_good} to Agent {max_index}')
            res_agent.message((NO_GOOD, (self.index, no_good)))
        else:
            for index, path in self.indirect_neighbors:
                if index == max_index:
                    res_agent_path = path
            if res_agent_path:
                for agent in self.neighbors:
                    if agent.index == res_agent_path[0]:
                        agent.message((INDIRECT, (res_agent_path[1:], (NO_GOOD, (self.index, no_good)))))
                        break
            else:
                print('ERROR: No_good contains non-neighbor')
        for index, number in self.agent_view:
            if index == max_index:
                self.agent_view.remove((index, number))
                break
        self.check_agent_view()

    def send_indirect(self, path, message):
        for agent in self.neighbors:
            if agent.index == path[0]:
                agent.message((INDIRECT, (path[1:], message)))
                return
        print(f'ERROR: Indirect Message Failed. Path = {path}, Message = {message}')

    def is_consistent(self, number):
        for index, agent_number in self.agent_view:
            is_neighbor = False
            for agent in self.neighbors:
                if agent.index == index:
                    is_neighbor = True
                    break
            if not is_neighbor:
                continue
            if agent_number == number:
                return False
        for no_good in self.no_goods:
            if set(no_good).issubset({*self.agent_view, (self.index, number)}):
                return False
        return True

    def print_info(self, string):
        if self.verbose:
            print(string)