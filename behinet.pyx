import subprocess
import threading
import ipaddress
import os

routed_ips = []


class Route:
    def __init__(self, ip_address, gateway):
        self.ip_address = ip_address
        self.gateway = gateway

    def add(self):
        if self.is_routed():
            return True

        if os.name == 'nt':
            subprocess.Popen(f'route ADD {self.ip_address} MASK 255.255.255.255 {self.gateway}'.split())
        else:
            subprocess.Popen(f'ip route add {self.ip_address}/32 via {self.gateway}'.split())

        return self.is_routed()

    def delete(self):
        if not self.is_routed():
            return True

        if os.name == 'nt':
            subprocess.Popen(f'route DELETE {self.ip_address} MASK 255.255.255.255 {self.gateway}'.split())
        else:
            subprocess.Popen(f'ip route del {self.ip_address}/32 via {self.gateway}'.split())

        return not self.is_routed()

    def is_routed(self):
        if os.name == 'nt':
            cmd = 'route print'
        else:
            cmd = 'ip route'

        output = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).communicate()[0]
        for line in output.decode("utf-8").splitlines():
            if self.ip_address in line and self.gateway in line: return True

        return False


def main():
    for interface in interfaces():
        threading.Thread(target=monitor_interface, args=interface).start()


def dependency(name):
    if os.name == 'nt':
        name += '.exe'

    return os.path.join(os.path.dirname(__file__), "dependencies", name)


def interfaces():
    p = subprocess.Popen((dependency('tcpdump'), '-D'), stdout=subprocess.PIPE)
    interfaces_list = []
    for row in iter(p.stdout.readline, b''):
        interface = str(row.rstrip()).split('\'')[1].split('.')[0]
        interfaces_list.append(interface)

    return interfaces_list


def monitor_interface(interface):
    p = subprocess.Popen((dependency('tcpdump'), '-nn', '-i', interface), stdout=subprocess.PIPE)
    for row in iter(p.stdout.readline, b''):
        line = str(row.rstrip())
        try:
            ip_and_port_splited = line.split('> ')[1].split(':')[0].split('.')
            ip = f"{ip_and_port_splited[0]}.{ip_and_port_splited[1]}.{ip_and_port_splited[2]}.{ip_and_port_splited[3]}"
            threading.Thread(target=route_ip, args=(ip, )).start()
        except IndexError:
            pass


def route_ip(ip):
    if not ipaddress.ip_address(ip).is_private and ip not in routed_ips:
        routed_ips.append(ip)
        print(ip)
