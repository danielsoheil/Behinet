import time
import hashlib
import ipaddress
import threading
import requests
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
        ROUTES[node2][node1] = node1_to_node2[::-1]  # [::-1] to reverse


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
            threading.Thread(target=refresh).start()
        else:
            ROUTES.clear()

    return jsonify({'error': False, 'behinet_ip': behinet_ip, 'nodes': [node['public_ip'] for node in NODES]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1401)
