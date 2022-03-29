import time
import redis
import hashlib
import ipaddress
from flask import Flask, request, jsonify

app = Flask(__name__)

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
    if nodes_after_timeout != nodes_befor_timeout:
        # refresh()
        pass
    is_routernode = 'imrouternode' in request.form and hashlib.sha256(
            request.form['imrouternode'].encode('utf-8')
    ).hexdigest() == 'c3f4a78a0a2d83c1cba2bdeb7f5c9522cd424c3792ab163b1c09035e3afaaec4'

    if is_routernode:
        # refresh()
        pass


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
    nodes = []
    for node in nodes_after_timeout:
        if node.decode().split(',')[0] != request.remote_addr:
            nodes.append(node.decode().split(',')[0])

    return jsonify({'error': False, 'behinet_ip': behinet_ip, 'nodes': nodes})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1401)