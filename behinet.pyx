import subprocess
import threading
import ipaddress
import os

routed_ips = []


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
