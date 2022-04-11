import time
import hashlib
import ipaddress
import requests
import copy
import behinet_ai
import data_mining_tools as dmt
from flask import Flask, request, jsonify

app = Flask(__name__)
NODES = list()
PINGS = dict()
ROUTES = dict()


def refresh():
    all_relations_in_tuple_form = dmt.all_possible_relations_between_ips([node['public_ip'] for node in NODES])

    initial_data = []
    ip_list = []
    for node1, node2 in all_relations_in_tuple_form:
        # noinspection PyBroadException
        try:
            ping = requests.get(f'http://{node1}:1403/ping/{node2}/0').json()['ping']
            initial_data.append((node1, node2, ping))
            ip_list.append(node1)
            ip_list.append(node2)
        except Exception:
            pass

    for node1, node2, *_ in initial_data:
        node1_to_node2 = behinet_ai.best_route(ip_list, node1, node2, initial_data)

        if node1 not in ROUTES:
            ROUTES[node1] = {}
        ROUTES[node1][node2] = node1_to_node2

        if node2 not in ROUTES:
            ROUTES[node2] = {}

        node2_to_node1 = copy.deepcopy(node1_to_node2)
        node2_to_node1['routes'] = node1_to_node2['routes'][::-1]  # [::-1] to reverse
        ROUTES[node2][node1] = node2_to_node1


@app.route('/hi_boss', methods=['GET', 'POST'])
def hi_boss():
    nodes_to_remove = []
    for node in NODES:
        if node['lastupdate'] < (int(time.time()) - 60):
            nodes_to_remove.append(node)

    for node in nodes_to_remove:
        NODES.remove(node)

    do_refresh = len(nodes_to_remove) > 0

    is_routernode = 'imrouternode' in request.form and hashlib.sha256(
            request.form['imrouternode'].encode('utf-8')
    ).hexdigest() == 'c3f4a78a0a2d83c1cba2bdeb7f5c9522cd424c3792ab163b1c09035e3afaaec4'

    if 'behinet_ip' in request.form:
        behinet_ip = request.form['behinet_ip']
    else:
        for ip in ipaddress.IPv4Network('10.0.0.0/16').hosts():
            invalid_behinet_ip = False

            for node in NODES:
                if node['behinet_ip'] == str(ip):
                    invalid_behinet_ip = True

            if invalid_behinet_ip:
                continue
            else:
                behinet_ip = str(ip)
                break

    node_data = {
        'public_ip': request.remote_addr,
        'behinet_ip': behinet_ip,
        'is_routernode': is_routernode,
        'lastupdate': time.time()
    }

    old_node = False
    for node in range(len(NODES)):
        if NODES[node]['public_ip'] == request.remote_addr:
            old_node = True
            NODES[node] = node_data

    if not old_node:
        NODES.append(node_data)

    do_refresh = do_refresh or (not old_node and is_routernode)

    if do_refresh:
        if len(NODES) > 1:
            # run on new thread if need
            refresh()
        else:
            ROUTES.clear()

    return jsonify({'error': False, 'behinet_ip': behinet_ip, 'nodes': routernodes(request.remote_addr)})


def routernodes(self_ip):
    res = []
    for node in NODES:
        if node['is_routernode'] and node['public_ip'] != self_ip:
            res.append(node['public_ip'])

    return res


@app.route('/behiroute/<firstnode>/<ip>/<client_ping>', methods=['GET', 'POST'])
def behiroute(firstnode, ip, client_ping):
    if firstnode not in routernodes(request.remote_addr):
        return {'error': True, 'message': 'invalid firstnode'}

    best = None
    for node in routernodes(request.remote_addr):
        # noinspection PyBroadException
        try:
            ping = requests.get(f'http://{node}:1403/ping/{ip}/0').json()['ping']
            if best is None or ping < best['ping']:
                best = {'node': node, 'ping': ping}
        except Exception:
            pass

    if best is not None:
        lastnode = best['node']
    else:
        return {'error': True, 'message': 'firstnode dont have route to this ip'}

    res = {}
    ROUTES_COPY = copy.deepcopy(ROUTES)
    if firstnode == lastnode:
        res['ping'] = best['ping']
        res['routes'] = [firstnode]
    else:
        res['ping'] = ROUTES_COPY[firstnode][lastnode]['ping'] + best['ping']
        res['routes'] = ROUTES_COPY[firstnode][lastnode]['routes']

    if int(client_ping) > res['ping']:
        route_in_behinet(ip, res['routes'])

    for node in range(len(res['routes'])):
        if ip_public_to_behinet(res['routes'][node]) is not None:
            res['routes'][node] = ip_public_to_behinet(res['routes'][node])

    res['routes'].append(ip)
    return {'error': False, **res}


def route_in_behinet(ip, routes):
    routes = routes[::-1]
    do_again_with_new_routes = False
    for route in range(len(routes)):
        try:
            req = requests.get(f'http://{routes[route + 1]}:1403/boss_say_route/{ip}/{ip_public_to_behinet(routes[route])}')
            if req.status_code == 200 and 'error' in req.json() and req.json()['error']:
                raise requests.exceptions.RequestException
        except IndexError:
            pass
        except requests.exceptions.RequestException:
            routes.remove(routes[route + 1])
            do_again_with_new_routes = True
            break

    if do_again_with_new_routes:
        route_in_behinet(ip, routes[::-1])


def ip_behinet_to_public(ip):
    for node in NODES:
        if node['behinet_ip'] == ip:
            return node['public_ip']


def ip_public_to_behinet(ip):
    for node in NODES:
        if node['public_ip'] == ip:
            return node['behinet_ip']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1401)
