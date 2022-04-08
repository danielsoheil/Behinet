import time
import redis
import hashlib
import ipaddress
import threading
import requests
import behinet_ai
import data_mining_tools as dmt
from flask import Flask, request, jsonify

app = Flask(__name__)
NODES = set()
PINGS = dict()
ROUTES = dict()

def refresh():
    nodes_to_delete = []
    for node in NODES:
        try:
            req = requests.get(f'http://{node}:1403/pings')
            if req.status_code != 200:
                raise requests.exceptions.RequestException

            PINGS[node] = req.json()['pings']
        except requests.exceptions.RequestException:
            nodes_to_delete.append(node)

    for node in nodes_to_delete:
        NODES.remove(node)

    all_relations_in_tuple_form = dmt.all_possible_relations_between_ips(NODES)

    initial_data = []
    for node1, node2 in all_relations_in_tuple_form:
        initial_data.append((node1, node2, PINGS[node1][node2]))

    ROUTES = {}
    for node1, node2 in all_relations_in_tuple_form:
        node1_to_node2 = behinet_ai.best_route(NODES, node1, node2, initial_data)

        if node1 not in ROUTES:
            ROUTES[node1] = {}
        ROUTES[node1][node2] = node1_to_node2

        if node2 not in ROUTES:
            ROUTES[node2] = {}
        ROUTES[node2][node1] = node1_to_node2.reverse()


@app.route('/', methods=['GET', 'POST'])
def main():
    r = redis.Redis(
        host='ipv4.sohe.ir',
        port=6379,
        password=''
    )
    nodes_befor_timeout = r.zrange('nodes', '0', '-1')
    r.zremrangebyscore('nodes', '-inf', str(int(time.time()) - 60))
    nodes_after_timeout = r.zrange('nodes', '0', '-1')

    do_refresh = len(nodes_after_timeout) < len(nodes_befor_timeout)

    is_routernode = 'imrouternode' in request.form and hashlib.sha256(
            request.form['imrouternode'].encode('utf-8')
    ).hexdigest() == 'c3f4a78a0a2d83c1cba2bdeb7f5c9522cd424c3792ab163b1c09035e3afaaec4'

    old_node = False
    for node in nodes_after_timeout:
        if node.decode().split(',')[0] == request.remote_addr:
            old_node = True

    if 'behinet_ip' in request.form:
        behinet_ip = request.form['behinet_ip']
    else:
        for ip in ipaddress.IPv4Network('10.0.0.0/16').hosts():
            invalid_behinet_ip = False

            for node in nodes_after_timeout:
                if node.decode().split(',')[1] == str(ip):
                    invalid_behinet_ip = True

            if invalid_behinet_ip:
                continue
            else:
                behinet_ip = str(ip)
                break

    r.zadd('nodes', {','.join([request.remote_addr, behinet_ip, str(is_routernode)]): str(int(time.time()))})
    
    nodes_after_add_new = r.zrange('nodes', '0', '-1')
    do_refresh = do_refresh or (len(nodes_after_timeout) < len(nodes_after_add_new) and is_routernode)

    res = set()
    NODES.clear()
    for node in nodes_after_add_new:
        node_pub_ip = node.decode().split(',')[0]
        if node.decode().split(',')[2] == 'True':
            NODES.add(node_pub_ip)
            if node_pub_ip != request.remote_addr:
                res.add(node_pub_ip)

    if do_refresh and len(NODES) > 1:
        threading.Thread(target=refresh).start()

    return jsonify({'error': False, 'behinet_ip': behinet_ip, 'nodes': list(NODES)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1401)
