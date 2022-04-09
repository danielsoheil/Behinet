import util
import random
from copy import deepcopy
from data_mining_tools import direct_cost
from itertools import combinations, permutations



def generate_random_chains_in_frontier(frontier, data_dict, source, target, attempts, nodes_num):
    for _ in range(attempts):
        try:
            new_action_chain = util.ActionChain(source, target)
            for _ in range(nodes_num - 2):
                origin = new_action_chain.nodes_arrangement[-1]
                neighbors = new_action_chain.nodes_arrangement[-1].neighbors - set([target] + new_action_chain.nodes_arrangement)
                goal = random.sample(neighbors, 1)[0]
                new_action = util.Action(new_action_chain.chain[-1], origin, goal, direct_cost(data_dict, origin, goal))
                new_action_chain.attach_action(new_action)
            new_action_chain.complete_action_chain_immediately(data_dict)
            frontier.add_layer(new_action_chain)
        except:
            continue
     
def generate_all_possible_chains_in_frontier(frontier, data_dict, source, target, nodes_lim):
    def generate_chains(frontier, data_dict, origin, target, action_chain, nodes_lim):
        if origin == target and len(action_chain.nodes_arrangement) <= nodes_lim:
            frontier.add_layer(action_chain); return
        
        for neighbor_node in origin.neighbors - set(action_chain.nodes_arrangement):
            new_action = util.Action(action_chain.chain[-1], origin, neighbor_node, direct_cost(data_dict, origin, neighbor_node))
            new_action_chain = deepcopy(action_chain); new_action_chain.attach_action(new_action)
            generate_chains(frontier, data_dict, neighbor_node, target, new_action_chain, nodes_lim)
            
    generate_chains(frontier, data_dict, source, target, util.ActionChain(source, target), nodes_lim)    
  
def generate_all_possible_chains_in_frontier_with_certain_length(frontier, data_dict, source, target, nodes_num):
    def generate_chains(frontier, data_dict, origin, target, action_chain, nodes_num):
        if origin == target and len(action_chain.nodes_arrangement) == nodes_num:
            frontier.add_layer(action_chain); return
        
        for neighbor_node in origin.neighbors - set(action_chain.nodes_arrangement):
            new_action = util.Action(action_chain.chain[-1], origin, neighbor_node, direct_cost(data_dict, origin, neighbor_node))
            new_action_chain = deepcopy(action_chain); new_action_chain.attach_action(new_action)
            generate_chains(frontier, data_dict, neighbor_node, target, new_action_chain, nodes_num)
            
    generate_chains(frontier, data_dict, source, target, util.ActionChain(source, target), nodes_num)    
        
def generate_chains_with_minimum_climb_in_frontier(frontier, data_dict, source, target, attempts, nodes_lim):
    for _ in range(attempts):
        new_chain = util.ActionChain(source, target)
        current_node = source; nodes_cnt = 1
        while nodes_cnt < nodes_lim - 1 and len(new_chain.possible_actions_for_node_in_chain(frontier, current_node, data_dict)):
            new_action = new_chain.action_with_minimum_cost_for_node(frontier, current_node, data_dict)
            new_chain.attach_action(new_action)
            current_node = new_chain.nodes_arrangement[-1]
            nodes_cnt += 1
        if current_node != target:
            try: new_chain.complete_action_chain_immediately(data_dict)
            except: pass
        frontier.add_layer(new_chain)
        
def generate_chains_with_middle_climb_in_frontier(frontier, data_dict, source, target, attempts, nodes_lim):
    for _ in range(attempts):
        new_chain = util.ActionChain(source, target)
        current_node = source; nodes_cnt = 1
        while nodes_cnt < nodes_lim - 1 and len(new_chain.possible_actions_for_node_in_chain(frontier, current_node, data_dict)):
            new_action = new_chain.action_with_middle_cost_for_node(frontier, current_node, data_dict)
            for action in new_chain.possible_actions_for_node_in_chain(frontier, current_node, data_dict): print(action)
            new_chain.attach_action(new_action)
            current_node = new_chain.nodes_arrangement[-1]
            nodes_cnt += 1
        if current_node != target:
            try: new_chain.complete_action_chain_immediately(data_dict)
            except: pass
        frontier.add_layer(new_chain)         
        
def generate_chains_with_maximum_climb_in_frontier(frontier, data_dict, source, target, attempts, nodes_lim):
    for _ in range(attempts):
        new_chain = util.ActionChain(source, target)
        current_node = source; nodes_cnt = 1
        while nodes_cnt < nodes_lim - 1 and len(new_chain.possible_actions_for_node_in_chain(frontier, current_node, data_dict)):
            new_action = new_chain.action_with_maximum_cost_for_node(frontier, current_node, data_dict)
            new_chain.attach_action(new_action)
            current_node = new_chain.nodes_arrangement[-1]
            nodes_cnt += 1
        if current_node != target:
            try: new_chain.complete_action_chain_immediately(data_dict)
            except: pass
        frontier.add_layer(new_chain)   

def generate_chains_intelligently(frontier, data_dict, source, target, attempts, nodes_lim):
    def generate_chains(frontier, data_dict, origin, target, action_chain, nodes_lim, attempts_cnt):
        if attempts_cnt > attempts: print('0'); return
            
        if action_chain.total_cost > frontier.best_layer.total_cost:
            frontier.add_layer(action_chain); attempts_cnt += 1; print('1'); return
            
        if origin == target and len(action_chain.nodes_arrangement) <= nodes_lim:
            frontier.add_layer(action_chain); attempts_cnt += 1; print('2'); return
        
        for neighbor_node in origin.neighbors - set(action_chain.nodes_arrangement): 
            print('3')
            new_action = util.Action(action_chain.chain[-1], origin, neighbor_node, direct_cost(data_dict, origin, neighbor_node))
            new_action_chain = deepcopy(action_chain); new_action_chain.attach_action(new_action)
            generate_chains(frontier, data_dict, neighbor_node, target, new_action_chain, nodes_lim, attempts_cnt)

    generate_chains(frontier, data_dict, source, target, util.ActionChain(source, target), nodes_lim, 0)
        

 