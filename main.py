import subprocess
import threading
import ipaddress
import os
import time
from subprocess import Popen
from typing import Any, Union

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


class Ping:
    ping_process: Union[Popen[bytes], Popen[Any]]
    def __init__(self, target):
        self.target = target
        self.times = []
        threading.Thread(target=self.start).start()

    def start(self):
        cmd = ['ping', self.target]
        if os.name == 'nt':
            cmd.append('-t')

        self.ping_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        for line in iter(self.ping_process.stdout.readline, b''):
            for attribute in line.decode('utf-8').split():
                try:
                    if attribute.split('=')[0] == 'time':
                        if len(self.times) >= 10 * 60:
                             self.times.pop(0)

                        self.times.append(int(attribute.split('=')[1].replace('ms', '')))
                except IndexError:
                    continue

    def average_time(self):
        return int(sum(self.times) / len(self.times))

    def kill(self):
        if self.ping_process.pid:
            self.ping_process.kill()


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


if __name__ == '__main__':
    main()
