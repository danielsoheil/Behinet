import math
import random
from copy import deepcopy
from operator import attrgetter



class Node:
    def __new__(cls, ip_address):
        self = super().__new__(cls)
        self.ip_address = ip_address
        self.neighbors = set()
        return self 

    def __getnewargs__(self):
        return (self.ip_address,)

    def __eq__(self, other):
        return self.ip_address == other.ip_address
        
    def __hash__(self):
        return hash(self.ip_address)
    
    def __str__(self):
        return self.ip_address
    
    def __repr__(self):
        return self.ip_address
    
    def set_neighbors(self, nodes_set):
        self.neighbors = nodes_set
    
    def append_neighbors(self, nodes_set):
        self.neighbors.update(nodes_set)
        
    def add_neighbor(self, node):
        self.neighbors.add(node)
        
    def prune_neighbors(self, prune_set):
        try: self.neighbors -= prune_set
        except: pass
        
    def remove_neighbor(self, node):
        try: self.neighbors.remove(node)
        except: pass
        
    def empty_neighbors(self):
        self.neighbors.clear()
        
    def possible_goals_for_next_action(self, current_action):
        possible_goals = deepcopy(self.neighbors)
        action = current_action
        while action is not None and action.parent is not None:
            try: possible_goals.remove(action.origin)
            except: pass
            action = action.parent
        try: possible_goals.remove(action.origin)
        except: pass
        return possible_goals
            


class Relation:
    def __init__(self, node_1, node_2, ping):
        self.node_1 = node_1
        self.node_2 = node_2
        self.cost = ping
        
    def __eq__(self, other):
        return (self.node_1 == other.node_1 and self.node_2 == other.node_2) or \
               (self.node_1 == other.node_2 and self.node_2 == other.node_1)
               
    def __hash__(self):
        return hash((self.node_1, self.node_2))
    
    def __str__(self):
        return self.node_1.ip_address + ' <--p--> ' + self.node_2.ip_address + ' : ' + str(self.cost)



class Action:
    def __init__(self, former_action, origin_node, goal_node, ping):
        self.parent = former_action
        self.origin = origin_node
        self.goal = goal_node
        self.cost = ping
        self.cost_till_now = ping if former_action is None else former_action.cost_till_now + ping

    def __eq__(self, other):
        return self.origin == other.origin and self.goal == other.goal
        
    def __hash__(self):
        return hash((self.origin, self.goal))    
        
    def __str__(self):
        return self.origin.ip_address + ' ---> ' + self.goal.ip_address    
        
    def change_parent(self, new_parent_action):
        self.parent = new_parent_action
        self.cost_till_now = new_parent_action.cost_till_now + self.cost if new_parent_action is not None else self.cost
    
    def is_first_action(self, source):
        return True if self.origin == source else False
    
    def is_middle_action(self, source, target):
        return True if self.origin != source and self.goal != target else False
    
    def is_final_action(self, target):
        return True if self.goal == target else False



class ActionChain:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.neighbors = set()
        self.chain = [None]
        self.nodes_arrangement = [source]
        self.total_cost = 0
        
    def __eq__(self, other):
        return self.nodes_arrangement == other.nodes_arrangement
    
    def __str__(self):
        str = self.nodes_arrangement[0].ip_address
        for node in self.nodes_arrangement[1:]:
            str += ' --> ' + node.ip_address
        return str
    
    def __hash__(self):
        return hash(tuple(self.nodes_arrangement))
    
    def find_action_by_origin(self, node):
        for action in self.chain: 
            if action.origin == node: return action
        return None
    
    def find_action_by_goal(self, node):
        for action in self.chain[1:]:
            if action.goal == node: return action
        return None
    
    def attach_action(self, action):
        if action.origin != self.nodes_arrangement[-1] or self.nodes_arrangement[-1] == self.target: 
            raise Exception("Action is impossible at this point")
        #if action.goal in self.nodes_arrangement or action in self.chain:
        #    raise Exception("Action is duplicate")
        action_copy = deepcopy(action)
        action_copy.change_parent(self.chain[-1])
        self.chain.append(action_copy)
        self.nodes_arrangement.append(action_copy.goal)
        self.total_cost = action_copy.cost_till_now
    
    def detach_action(self, action):
        try: 
            self.chain = self.chain[:self.chain.index(action)]
            self.nodes_arrangement = self.nodes_arrangement[:self.nodes_arrangement.index(action.goal)]
            self.total_cost = self.chain[-1].cost_till_now
        except: 
            raise Exception("Action is not in chain")
    
    def is_complete(self):
        return True if self.nodes_arrangement[-1] == self.target else False
    
    def possible_actions_for_node_in_chain(self, frontier, node, data_dict):
        
        def duplicate_neighbors_in_frontier(frontier, current_node):
            duplicate_neighbors = set()
            arrangement_till_current_node = self.nodes_arrangement[:self.nodes_arrangement.index(current_node)]
            for layer in frontier.layers:
                if current_node in layer.nodes_arrangement: 
                    if layer.nodes_arrangement[:layer.nodes_arrangement.index(current_node)] == arrangement_till_current_node:
                        try: duplicate_neighbors.add(layer.nodes_arrangement[layer.nodes_arrangement.index(current_node)+1])
                        except: pass
            return duplicate_neighbors

        current_action = self.find_action_by_goal(node)
        possible_goals = node.possible_goals_for_next_action(current_action) - duplicate_neighbors_in_frontier(frontier, node)
        possible_actions = set()
        for goal in possible_goals:
            ping = find_direct_cost(data_dict, node, goal)
            possible_actions.add(Action(current_action, node, goal, ping))
        return possible_actions
    
    def average_weight_for_node_in_chain(self, frontier, node):
        all_cost = sum(action.cost for action in self.possible_actions_for_node_in_chain(frontier, node))
        average = all_cost / len(self.possible_actions_for_node_in_chain(frontier, node)) 
        return average
    
    def action_with_minimum_cost_for_node(self, frontier, node, data_dict):
        return min(self.possible_actions_for_node_in_chain(frontier, node, data_dict), key=attrgetter('cost'))
    
    def action_with_middle_cost_for_node(self, frontier, node, data_dict):
        action_list = list(self.possible_actions_for_node_in_chain(frontier, node, data_dict))
        action_list.sort(key=attrgetter('cost'))
        return action_list[math.floor(len(action_list)/2)]
        
    def action_with_maximum_cost_for_node(self, frontier, node, data_dict):
        return max(self.possible_actions_for_node_in_chain(frontier, node, data_dict), key=attrgetter('cost'))

    def action_with_random_choice_for_node(self, frontier, node):
        return random.choice(self.possible_actions_for_node_in_chain(frontier, node))
    
    
    class BabyActionChain:
        def __init__(self, chain, nodes_arrangement, cost):
            self.start_node = nodes_arrangement[0]
            self.end_node = nodes_arrangement[-1]
            self.chain = chain
            self.nodes_arrangement = nodes_arrangement
            self.total_cost = cost
    
        def __eq__(self, other):
            return self.nodes_arrangement == other.nodes_arrangement
        
        def __hash__(self):
            return hash(tuple(self.nodes_arrangement))
                   
    def export_baby_chain_using_nodes(self, node_1, node_2):
        action_1 = self.find_action_by_origin(node_1); action_2 = self.find_action_by_goal(node_2)
        chain = self.chain[self.chain.index(action_1):self.chain.index(action_2)+1]
        nodes_arrangement = self.nodes_arrangement[self.nodes_arrangement.index(node_1):self.nodes_arrangement.index(node_2)+1]
        cost = action_2.cost_till_now - action_1.parent.cost_till_now if action_1.parent is not None else action_2.cost_till_now
        return self.BabyActionChain(chain, nodes_arrangement, cost)

    def export_baby_chain_using_actions(self, action_1, action_2):
        chain = self.chain[self.chain.index(action_1):self.chain.index(action_2)+1]
        nodes_arrangement = self.nodes_arrangement[self.nodes_arrangement.index(action_1.origin):self.nodes_arrangement.index(action_2.goal)+1]
        cost = action_2.cost_till_now - action_1.parent.cost_till_now if action_1.parent is not None else action_2.cost_till_now
        return self.BabyActionChain(chain, nodes_arrangement, cost)
    
    def attach_baby_chain(self, baby_chain):
        baby_chain_copy = deepcopy(baby_chain)
        baby_chain_copy.chain[0].change_parent(self.chain[-1])
        self.chain += baby_chain.chain
        self.nodes_arrangement += baby_chain.nodes_arrangement[1:]
        self.total_cost += baby_chain.total_cost

    def deep_attach_baby_chain(self, baby_chain, data_dict):
        baby_chain_copy = deepcopy(baby_chain)
        baby_chain_copy.chain[0].change_parent(self.chain[-1])
        if self.baby_chain_is_ready_for_attaching(baby_chain_copy): 
            self.attach_baby_chain(baby_chain_copy)
        elif not len(set(baby_chain_copy.nodes_arrangement[1:]) & set(self.nodes_arrangement)):
            ping = find_direct_cost(data_dict, self.nodes_arrangement[-1], baby_chain_copy.nodes_arrangement[0])
            self.attach_action(Action(self.chain[-1], self.nodes_arrangement[-1], baby_chain_copy.nodes_arrangement[0], ping))
            self.attach_baby_chain(baby_chain_copy)
        
    def baby_chain_is_ready_for_attaching(self, baby_chain):
        if baby_chain.start_node == self.nodes_arrangement[-1]:
            if len(set(baby_chain.nodes_arrangement[1:]) & set(self.nodes_arrangement)) == 0:
                return True
        return False

    def create_action_chain_from_node(self, node, action):
        action_chain = ActionChain(self.source, self.target)
        action_chain.attach_baby_chain(self.export_baby_chain_using_nodes(self.source, node))
        action_chain.attach_action(action)
        return action_chain

    def complete_action_chain_immediately(self, data_dict):
        if self.target in self.nodes_arrangement[-1].neighbors:
            ping = find_direct_cost(data_dict, self.nodes_arrangement[-1], self.target)
            self.attach_action(Action(self.chain[-1], self.nodes_arrangement[-1], self.target, ping))
        else: 
            raise Exception("Action chain completion is impossible at this point")
        
    def add_neighbor(self, action_chain):
        if self.target == action_chain.source and not len(set(self.nodes_arrangement).intersection(action_chain.nodes_arrangement[1:])):
            self.neighbors.add(action_chain)
            
        
        
class Frontier:
    def __init__(self):
        self.layers = []
        self.successful_layers = []
        self.unsuccessful_layers = []
        self.best_layer = None
    
    def add_layer(self, action_chain):
        if action_chain not in self.layers:
            layer = deepcopy(action_chain)
            self.layers.append(layer)
            if layer.is_complete():
                self.successful_layers.append(layer)
                if self.best_layer is None or layer.total_cost < self.best_layer.total_cost:
                    self.best_layer = layer
            else:
                self.unsuccessful_layers.append(layer)
        
    def action_chain_is_optimal(self, action_chain):
        return True if action_chain.total_cost <= self.best_layer.total_cost else False
    
    def success_percentage(self):
        try: return (len(self.successful_layers) / len(self.layers)) * 100
        except: return 0
        
    def empty_frontier(self):
        del self.layers[:]
        del self.successful_layers[:]
        del self.unsuccessful_layers[:]
        self.best_layer = None
    
          

def find_direct_cost(data_dict, node_1, node_2):
    return data_dict[max(node_1.ip_address, node_2.ip_address) + ' <--p--> ' + min(node_1.ip_address, node_2.ip_address)]
