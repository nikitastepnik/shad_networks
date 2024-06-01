import enum
import os
import subprocess
import typing

NODES = ['router1', 'router2', 'router3', 'PC1', 'PC2', 'PC3']
NODES_IP_INTERFACES_MAP = {
    'router1': {
        'eth1': '192.168.1.1/24',
        'eth2': '192.168.2.1/24',
        'eth3': '192.168.11.1/24',
        'lo': '10.10.10.1/32',
    },
    'router2': {
        'eth1': '192.168.1.2/24',
        'eth2': '192.168.3.2/24',
        'eth3': '192.168.22.2/24',
        'lo': '10.10.10.2/32'
    },
    'router3': {
        'eth1': '192.168.2.3/24',
        'eth2': '192.168.3.3/24',
        'eth3': '192.168.33.3/24',
        'lo': '10.10.10.3/32'
    },
    'PC1': {
        'eth1': '192.168.11.4/24'
    },
    'PC2': {
        'eth1': '192.168.22.4/24'
    },
    'PC3': {
        'eth1': '192.168.33.4/24'
    }
}
NODES_STATIC_ROUTING_MAP = {
    'router1': {
        '10.10.10.2/32 192.168.1.2': 'eth1',
        '10.10.10.3/32 192.168.2.3': 'eth2',
        '192.168.22.0/24 192.168.1.2': 'eth1',
        '192.168.33.0/24 192.168.2.3': 'eth2'
    },
    'router2': {
        '192.168.11.0/24 192.168.1.1': 'eth1',
        '192.168.33.0/24 192.168.3.3': 'eth2',
        '10.10.10.1/32 192.168.1.1': 'eth1',
        '10.10.10.3/32 192.168.3.3': 'eth2'
    },
    'router3': {
        '192.168.11.0/24 192.168.2.1': 'eth1',
        '192.168.22.0/24 192.168.3.2': 'eth2',
        '10.10.10.1/32 192.168.2.1': 'eth1',
        '10.10.10.2/32 192.168.3.2': 'eth2'
    },
    'PC1': {
        '10.10.10.0/24 192.168.11.1': 'eth1',
        '192.168.22.0/24 192.168.11.1': 'eth1',
        '192.168.33.0/24 192.168.11.1': 'eth1'
    },
    'PC2': {
        '10.10.10.0/24 192.168.22.2': 'eth1',
        '192.168.11.0/24 192.168.22.2': 'eth1',
        '192.168.33.0/24 192.168.22.2': 'eth1'
    },
    'PC3': {
        '10.10.10.0/24 192.168.33.3': 'eth1',
        '192.168.11.0/24 192.168.33.3': 'eth1',
        '192.168.22.0/24 192.168.33.3': 'eth1'
    }
}
STUDENT_NAME = 'Nikita_Stepanov'


class VtyshOptions(enum.Enum):
    COMMAND_SEP = ' -c '


class Commands(enum.Enum):
    CONNECT_TO_NODE_CONTAINER = (
        'sudo docker exec -it clab-frrlab1_1-{node} vtysh'
    )
    START_CONFIGURATION = 'conf'
    SAVE_CONFIGURATION = '"do wr"'
    SET_INTERFACE = '"int {interface}"'
    SET_IP_ADDRESS = '"ip address {address}"'
    SET_HOSTNAME = '"hostname {hostname}"'
    SET_IP_ROUTE = '"ip route {route} {interface}"'


def _execute_command(command: str) -> None:
    process = subprocess.run(
        command,
        shell=True,
    )
    process.check_returncode()


def _save_configuration_to_file(
        configuration_content: str, node: str, 
        first_execution: bool = False,
) -> None:
    file_name = STUDENT_NAME + f'_{node}.conf'
    if first_execution and os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, 'a') as file:
        file.write(configuration_content + '\n')


def _get_static_routing_command(node: str) -> str:
    static_routing_command = ''
    static_routing_command += Commands.CONNECT_TO_NODE_CONTAINER.value.format(
        node=node
    )
    node_static_routes: typing.Dict[str, str] = NODES_STATIC_ROUTING_MAP[node]
    static_routing_command += (
        VtyshOptions.COMMAND_SEP.value + Commands.START_CONFIGURATION.value
    )
    static_routing_command += (
        VtyshOptions.COMMAND_SEP.value + Commands.SET_HOSTNAME.value.format(
            hostname=node,
        )
    )
    for route in node_static_routes:
        static_routing_command += (
            VtyshOptions.COMMAND_SEP.value
            + Commands.SET_IP_ROUTE.value.format(
                route=route, interface=node_static_routes[route],
            )
        )
    static_routing_command += (
        VtyshOptions.COMMAND_SEP.value + Commands.SAVE_CONFIGURATION.value
    )
    return static_routing_command


def _get_ip_conf_command(node: str) -> str:
    ip_conf_command = ''
    ip_conf_command += Commands.CONNECT_TO_NODE_CONTAINER.value.format(
        node=node
    )
    node_interfaces: typing.Dict[str, str] = NODES_IP_INTERFACES_MAP[node]
    ip_conf_command += (
        VtyshOptions.COMMAND_SEP.value + Commands.START_CONFIGURATION.value
    )
    for interface in node_interfaces:
        ip_conf_command += (
            VtyshOptions.COMMAND_SEP.value
            + Commands.SET_INTERFACE.value.format(
                interface=interface
            )
        )
        ip_conf_command += (
            VtyshOptions.COMMAND_SEP.value
            + Commands.SET_IP_ADDRESS.value.format(
                address=node_interfaces[interface]
            )
        )
    ip_conf_command += (
        VtyshOptions.COMMAND_SEP.value + Commands.SAVE_CONFIGURATION.value
    )
    return ip_conf_command


def _configure_node_static_routing(node: str) -> str:
    static_routing_command: str = _get_static_routing_command(node)
    _execute_command(static_routing_command)
    _save_configuration_to_file(static_routing_command, node)


def _configure_nodes_static_routing() -> str:
    for node in NODES:
        _configure_node_static_routing(node)


def _configure_node_ip_addreses(node: str) -> None:
    ip_conf_command: str = _get_ip_conf_command(node)
    _execute_command(ip_conf_command)
    _save_configuration_to_file(ip_conf_command, node, first_execution=True)


def _configure_nodes_ip_addreses() -> None:
    for node in NODES:
        _configure_node_ip_addreses(node)


def _configure_topology() -> None:
    _configure_nodes_ip_addreses()
    _configure_nodes_static_routing()


if __name__ == '__main__':
    _configure_topology()
