import util
from math import comb, factorial
from operator import attrgetter
from itertools import combinations

    

# DATA MANAGEMENT FUNCTIONS

def all_possible_relations_between_ips(ip_list):
    return list(combinations(ip_list, 2))

def store_ip_addresses_into_nodes_set(ip_list):
    nodes_set = set()
    for ip in ip_list: nodes_set.add(util.Node(ip))
    return nodes_set

def set_neighbors_for_nodes(nodes_set):
    for node in nodes_set: node.set_neighbors(nodes_set - set([node]))

def store_initial_data_into_dictionary(initial_data):
    dict = {}
    for triple in initial_data:
        dict[max(str(triple[0]), str(triple[1])) + ' <--p--> ' + min(str(triple[0]), str(triple[1]))] = triple[2]
    return dict

def store_initial_data_into_relations_set(data_dict, nodes_set):
    relations_set = set()
    for tuple in combinations(nodes_set, 2): 
        if tuple[0].ip_address > tuple[1].ip_address: node_1, node_2 = tuple[0], tuple[1] 
        else: node_1, node_2 = tuple[1], tuple[0]  
        ping = direct_cost(data_dict, node_1, node_2)    
        relations_set.add(util.Relation(node_1, node_2, ping))
    return relations_set


# CALCULATION FUNCTIONS

def number_of_all_possible_ways(number_of_nodes):
    cnt = 0
    for k in range(number_of_nodes - 1): cnt += comb(number_of_nodes - 2, k) * factorial(k)
    return cnt    

def number_of_all_possible_ways_with_limit(number_of_nodes, limit):
    cnt = 0
    for k in range(limit + 1): cnt += comb(number_of_nodes - 2, k) * factorial(k)
    return cnt  

def direct_cost(data_dict, node_1, node_2):
    return data_dict[max(node_1.ip_address, node_2.ip_address) + ' <--p--> ' + min(node_1.ip_address, node_2.ip_address)]

def maximum_number_of_nodes_for_optimal_solution(relations_set, minimum_cost_till_now, number_of_nodes):
    relations_list = list(relations_set); relations_list.sort(key=attrgetter('cost'))
    costs_sum = 0; cnt = 0
    while minimum_cost_till_now > costs_sum and cnt < len(relations_list):
        costs_sum += relations_list[cnt].cost; cnt += 1
    return cnt if cnt < number_of_nodes else number_of_nodes


# DATA PRUNING FUNCTIONS 

def prune_data_based_on_minimum_cost(relations_set, minimum_cost_till_now):
    prune_set = set()
    for relation in relations_set:
        if relation.cost > minimum_cost_till_now:
            relation.node_1.remove_neighbor(relation.node_2); relation.node_2.remove_neighbor(relation.node_1)
            prune_set.add(relation)
    return relations_set - prune_set

def prune_data_based_on_cost_from_source(relations_set, data_dict, source): 
    prune_set = set()
    for relation in relations_set:
        if relation.node_1 != source and relation.node_2 != source:
            direct_cost_1 = direct_cost(data_dict, source, relation.node_1)
            if relation.cost >= direct_cost_1: relation.node_2.remove_neighbor(relation.node_1)
            direct_cost_2 = direct_cost(data_dict, source, relation.node_2)
            if relation.cost >= direct_cost_2: relation.node_1.remove_neighbor(relation.node_2)
            if  relation.cost >= direct_cost_1 and relation.cost >= direct_cost_2: prune_set.add(relation)
    return relations_set - prune_set

def prune_data_based_on_cost_to_target(relations_set, data_dict, target): 
    prune_set = set()
    for relation in relations_set:
        if relation.node_1 != target and relation.node_2 != target:
            direct_cost_1 = direct_cost(data_dict, relation.node_1, target)
            if relation.cost >= direct_cost_1: relation.node_1.remove_neighbor(relation.node_2)
            direct_cost_2 = direct_cost(data_dict, relation.node_2, target)
            if relation.cost >= direct_cost_2: relation.node_2.remove_neighbor(relation.node_1)
            if  relation.cost >= direct_cost_1 and relation.cost >= direct_cost_2: prune_set.add(relation)
    return relations_set - prune_set