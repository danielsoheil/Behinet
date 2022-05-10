import util
import func_timeout
import algorithms as alg
#import neural_nets
import data_mining_tools as dmt



def best_route(ip_list, source_ip, target_ip, initial_data):
    source = util.Node(source_ip); target = util.Node(target_ip)

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

    def search():
        if num_of_limited_possible_ways < 200000:
            alg.generate_all_possible_chains_in_frontier(frontier, data_dict, source, target, nodes_limit)
        else:
            alg.generate_chains_with_minimum_climb_in_frontier(frontier, data_dict, source, target, 1000, nodes_limit)
            alg.generate_chains_with_middle_climb_in_frontier(frontier, data_dict, source, target, 1000, nodes_limit)
            alg.generate_chains_with_maximum_climb_in_frontier(frontier, data_dict, source, target, 1000, nodes_limit)
            
            if nodes_limit <= 10:
                for i in range(3, nodes_limit + 1):
                    alg.generate_chains_intelligently(frontier, data_dict, source, target, 700, nodes_limit)
                    if dmt.number_of_all_possible_ways_with_limit(nodes_num, i) <= 150:
                        alg.generate_all_possible_chains_in_frontier_with_certain_length(frontier, data_dict, source, target, i)
                    else:
                        alg.generate_random_chains_in_frontier(frontier, data_dict, source, target, 150, i)
            else:
                for i in range(3, 11):
                    alg.generate_chains_intelligently(frontier, data_dict, source, target, 700, 10)
                    if dmt.number_of_all_possible_ways_with_limit(nodes_num, i) <= 150:
                        alg.generate_all_possible_chains_in_frontier_with_certain_length(frontier, data_dict, source, target, i)        
                    else:
                        alg.generate_random_chains_in_frontier(frontier, data_dict, source, target, 150, i)

    try: func_timeout.func_timeout(120, search)
    except: pass
    
    return {'routes': [str(ip) for ip in frontier.best_layer.nodes_arrangement], 'action_chain': frontier.best_layer, 'ping': frontier.best_layer.total_cost}
                
    
def best_route_by_knot_method(ip_list, source_ip, target_ip, initial_data, routes_dict):
    source = util.Node(source_ip); target = util.Node(target_ip)
    
    ip_list.remove(source.ip_address()); ip_list.remove(target.ip_address())
    nodes_dict = dmt.store_ip_addresses_into_nodes_dict(ip_list)
    nodes_dict[source.ip_address()] = source; nodes_dict[target.ip_address()] = target
    
    ach_list = []
    for node_1 in nodes_dict:
        for node_2 in nodes_dict:
            if node_1 != node_2:
                ach_list.append(routes_dict[node_1][node_2]['action_chain'])
                
    for ach_1 in ach_list:
        for ach_2 in ach_list:
            ach_1.add_neighbor(ach_2)
            
    for ach in ach_list:
        for neighbor in ach.neighbors:
            neighbor.target.empty_neighbors()
            nodes_dict[ach.target.ip_address].add_neighbor(nodes_dict[neighbor.target.ip_address])
            initial_data.append((ach.target.ip_address, neighbor.target.ip_address, neighbor.total_cost))
            
    data_dict = dmt.store_initial_data_into_dictionary(initial_data)
    
    nodes_set = set()
    for node in nodes_dict.values(): nodes_set.add(node)
        
    relations_set = dmt.store_initial_data_into_relations_set(data_dict, nodes_set)
    
    minimum_cost_till_now = dmt.direct_cost(data_dict, source, target)
    
    relations_set = dmt.prune_data_based_on_minimum_cost(relations_set, minimum_cost_till_now)
    relations_set = dmt.prune_data_based_on_cost_from_source(relations_set, data_dict, source)
    relations_set = dmt.prune_data_based_on_cost_to_target(relations_set, data_dict, target)
                

    nodes_dict[source.ip_address] = source; nodes_dict[target.ip_address] = target
    
    first_action_chain = util.ActionChain(source, target)
    first_action_chain.attach_action(util.Action(None, source, target, dmt.direct_cost(data_dict, source, target)))
    frontier = util.Frontier(); frontier.add_layer(first_action_chain)
    
    nodes_limit = dmt.maximum_number_of_nodes_for_optimal_solution(relations_set, minimum_cost_till_now, len(nodes_dict))
    
    def search():
        try: func_timeout.func_timeout(3, alg.generate_all_possible_chains_in_frontier(frontier, data_dict, source, target, nodes_limit))
        except: pass       
        alg.generate_chains_with_minimum_climb_in_frontier(frontier, data_dict, source, target, 50, nodes_limit)
        alg.generate_chains_with_middle_climb_in_frontier(frontier, data_dict, source, target, 50, nodes_limit)
        alg.generate_chains_with_maximum_climb_in_frontier(frontier, data_dict, source, target, 50, nodes_limit)    
        alg.generate_chains_intelligently(frontier, data_dict, source, target, 400, nodes_limit)

    try: func_timeout.func_timeout(10, search)
    except: pass
    
    first_sight_nodes_arrangement =  frontier.best_layer.nodes_arrangement
    best_route_action_chain = util.ActionChain(source, target)
    
    if len(first_sight_nodes_arrangement) == 2:
        return {'routes': [source.ip_address, target.ip_address], 'action_chain': frontier.best_layer, 'ping': frontier.best_layer.total_cost}
    
    if len(first_sight_nodes_arrangement) == 3:
        best_route_action_chain.attach_action(frontier.best_layer.chain[0])
        best_route_action_chain.attach_action(frontier.best_layer.chain[-1])
        return {'routes': [str(ip) for ip in best_route_action_chain.nodes_arrangement], 'action_chain': best_route_action_chain, 'ping': best_route_action_chain.total_cost}
    
    best_route_action_chain.attach_action(frontier.best_layer.chain[0])
    for i in range(1, len(first_sight_nodes_arrangement) - 2):
        node_1 = first_sight_nodes_arrangement[i]; node_2 = first_sight_nodes_arrangement[i+1]
        baby_chain = routes_dict[node_1.ip_address][node_2.ip_address]['action_chain'].export_baby_chain_using_nodes(node_1, node_2)
        best_route_action_chain.attach_baby_chain(baby_chain)
    best_route_action_chain.attach_action(frontier.best_layer.chain[-1])
    return {'routes': [str(ip) for ip in best_route_action_chain.nodes_arrangement], 'action_chain': best_route_action_chain, 'ping': best_route_action_chain.total_cost}
