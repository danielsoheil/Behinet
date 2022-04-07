import time
import util
import algorithms as alg
#import neural_nets
import data_mining_tools as dmt



def best_route(ip_list, source_ip, target_ip, initial_data):
    source = util.Node(source_ip); target = util.Node(target_ip)

    start_time = time.time()

    data_dict = dmt.store_initial_data_into_dictionary(initial_data)
    ip_list.remove(source.ip_address); ip_list.remove(target.ip_address)
    nodes_set = dmt.store_ip_addresses_into_nodes_set(ip_list)
    nodes_set.add(source); nodes_set.add(target); nodes_num = len(nodes_set)
    dmt.set_neighbors_for_nodes(nodes_set); target.neighbors = set()
    relations_set = dmt.store_initial_data_into_relations_set(data_dict, nodes_set)

    first_action_chain = util.ActionChain(source, target)
    first_action_chain.attach_action(util.Action(None, source, target, dmt.direct_cost(data_dict, source, target)))
    frontier = util.Frontier(); frontier.add_layer(first_action_chain)

    minimum_cost_till_now = dmt.direct_cost(data_dict, source, target)
    nodes_limit = dmt.maximum_number_of_nodes_for_optimal_solution(relations_set, minimum_cost_till_now, nodes_num)
    num_of_possible_ways = dmt.number_of_all_possible_ways(nodes_num)
    num_of_limited_possible_ways = dmt.number_of_all_possible_ways_with_limit(nodes_num, nodes_limit)

    relations_set = dmt.prune_data_based_on_minimum_cost(relations_set, minimum_cost_till_now)
    relations_set = dmt.prune_data_based_on_cost_from_source(relations_set, data_dict, source)
    relations_set = dmt.prune_data_based_on_cost_to_target(relations_set, data_dict, target)


    if num_of_limited_possible_ways < 200000:
        alg.generate_all_possible_chains_in_frontier(frontier, data_dict, source, target, nodes_limit)
    else:
        alg.generate_chains_with_minimum_climb_in_frontier(frontier, data_dict, source, target, 1000, nodes_limit)
        alg.generate_chains_with_middle_climb_in_frontier(frontier, data_dict, source, target, 1000, nodes_limit)
        alg.generate_chains_with_maximum_climb_in_frontier(frontier, data_dict, source, target, 1000, nodes_limit)
        
        if nodes_limit <= 10:
            for i in range(3, nodes_limit + 1):
                alg.generate_chains_intelligently(frontier, data_dict, source, target, 700, nodes_limit)
                if dmt.number_of_all_possible_ways_with_limit(nodes_num, i) <= 150 and time.time() - start_time <= 120:
                    alg.generate_all_possible_chains_in_frontier_with_certain_length(frontier, data_dict, source, target, i)
                elif time.time() - start_time <= 120:
                    alg.generate_random_chains_in_frontier(frontier, data_dict, source, target, 150, i)
        else:
            for i in range(3, 11):
                alg.generate_chains_intelligently(frontier, data_dict, source, target, 700, 10)
                if dmt.number_of_all_possible_ways_with_limit(nodes_num, i) <= 150 and time.time() - start_time <= 120:
                    alg.generate_all_possible_chains_in_frontier_with_certain_length(frontier, data_dict, source, target, i)        
                elif time.time() - start_time <= 120:
                    alg.generate_random_chains_in_frontier(frontier, data_dict, source, target, 150, i)
                    
    return [str(ip) for ip in frontier.best_layer.nodes_arrangement]
                
    
    