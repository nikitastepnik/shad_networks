import enum
import os
import subprocess
import typing

NODES = ['router1', 'router2', 'router3', 'PC1', 'PC2', 'PC3']
NODES_INTERFACES_MAP = {
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
        'lo': '10.10.10.2/32',
    },
    'router3': {
        'eth1': '192.168.2.3/24',
        'eth2': '192.168.3.3/24',
        'eth3': '192.168.33.3/24',
        'lo': '10.10.10.3/32',
    },
    'PC1': {
        'eth1': '192.168.11.4/24',
        'lo': '-'
    },
    'PC2': {
        'eth1': '192.168.22.4/24',
        'lo': '-'
    },
    'PC3': {
        'eth1': '192.168.33.4/24',
        'lo': '-'
    }
}
NODE_NET_ADRESSES_MAP = {
    'router1': '49.0001.1000.0000.1001.00',
    'router2': '49.0001.2000.0000.2000.00',
    'router3': '49.0001.3000.0000.3000.00',
    'PC1':     '49.0001.0000.0000.0001.00',
    'PC2':     '49.0001.2000.0000.2002.00',
    'PC3':     '49.0001.3000.0000.3003.00'
}
STUDENT_NAME = 'Nikita_Stepanov'


class VtyshOptions(enum.Enum):
    COMMAND_SEP = ' -c '


class ISISCommands(enum.Enum):
    START_ISIS_CONF_ROUTER = '"router isis 1"'
    SET_CONCRETE_LEVEL = '"is-type level-2-only"'
    SET_NET_ADDRESS = '"net {address}"'
    START_ISIS_CONF_IP = '"ip router isis 1"'
    SET_PASSIVE_INTERFACE = '"isis passive"'
    SET_LEVEL_CIRCUIT_TYPE = '"isis circuit-type level-2-only"'
    SET_ETH_NETWORK_TYPE = '"isis network point-to-point"'


class IPConfCommands(enum.Enum):
    SET_INTERFACE = '"int {interface}"'
    SET_IP_ADDRESS = '"ip address {address}"'


class BaseCommands(enum.Enum):
    CONNECT_TO_NODE_CONTAINER = (
        'sudo docker exec -it clab-frrlab1_1-{node} vtysh'
    )
    START_CONFIGURATION = 'conf'
    SAVE_CONFIGURATION = '"do wr"'
    EXIT = 'exit'


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


def _get_eth_isis_conf_commmand(eth_interface: str) -> str:
    eth_isis_conf_commmand = ''
    eth_isis_conf_commmand += (
        VtyshOptions.COMMAND_SEP.value
        + IPConfCommands.SET_INTERFACE.value.format(interface=eth_interface)
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.START_ISIS_CONF_IP.value
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.SET_LEVEL_CIRCUIT_TYPE.value
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.SET_ETH_NETWORK_TYPE.value
        + VtyshOptions.COMMAND_SEP.value
        + BaseCommands.EXIT.value
    )
    return eth_isis_conf_commmand


def _get_lo_isis_conf_commmand(lo_interface: str) -> str:
    lo_isis_conf_commmand = ''
    lo_isis_conf_commmand += (
        VtyshOptions.COMMAND_SEP.value
        + IPConfCommands.SET_INTERFACE.value.format(interface=lo_interface)
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.START_ISIS_CONF_IP.value
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.SET_PASSIVE_INTERFACE.value
        + VtyshOptions.COMMAND_SEP.value
        + BaseCommands.EXIT.value
    )
    return lo_isis_conf_commmand


def _get_net_isis_conf_command(node: str) -> str:
    net_isis_conf_command = ''
    node_net_address: str = NODE_NET_ADRESSES_MAP[node]
    net_isis_conf_command += (
        VtyshOptions.COMMAND_SEP.value
        + ISISCommands.START_ISIS_CONF_ROUTER.value
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.SET_CONCRETE_LEVEL.value
        + VtyshOptions.COMMAND_SEP.value
        + ISISCommands.SET_NET_ADDRESS.value.format(address=node_net_address)
        + VtyshOptions.COMMAND_SEP.value
        + BaseCommands.EXIT.value
    )
    return net_isis_conf_command


def _get_dynamic_routing_command(node: str) -> str:
    dynamic_routing_command = ''
    dynamic_routing_command += (
        BaseCommands.CONNECT_TO_NODE_CONTAINER.value.format(
            node=node
        )
        + VtyshOptions.COMMAND_SEP.value
        + BaseCommands.START_CONFIGURATION.value
    )
    net_isis_conf_command = _get_net_isis_conf_command(node)
    dynamic_routing_command += net_isis_conf_command
    node_interfaces: typing.Dict[str, str] = NODES_INTERFACES_MAP[node]
    for interface in node_interfaces:
        if 'lo' in interface:
            lo_isis_conf_commmand: str = _get_lo_isis_conf_commmand(interface)
            dynamic_routing_command += lo_isis_conf_commmand
        else:
            eth_isis_conf_commmand: str = _get_eth_isis_conf_commmand(
                interface
            )
            dynamic_routing_command += eth_isis_conf_commmand
    return dynamic_routing_command


def _get_ip_conf_command(node: str) -> str:
    ip_conf_command = ''
    ip_conf_command += BaseCommands.CONNECT_TO_NODE_CONTAINER.value.format(
        node=node
    )
    node_interfaces: typing.Dict[str, str] = NODES_INTERFACES_MAP[node]
    ip_conf_command += (
        VtyshOptions.COMMAND_SEP.value + BaseCommands.START_CONFIGURATION.value
    )
    for interface in node_interfaces:
        if 'PC' in node and 'lo' in interface:
            continue
        ip_conf_command += (
            VtyshOptions.COMMAND_SEP.value
            + IPConfCommands.SET_INTERFACE.value.format(
                interface=interface
            )
        )
        ip_conf_command += (
            VtyshOptions.COMMAND_SEP.value
            + IPConfCommands.SET_IP_ADDRESS.value.format(
                address=node_interfaces[interface]
            )
        )
    ip_conf_command += (
        VtyshOptions.COMMAND_SEP.value + BaseCommands.SAVE_CONFIGURATION.value
    )
    return ip_conf_command


def _configure_node_dynamic_routing(node: str) -> str:
    dynamic_routing_command: str = _get_dynamic_routing_command(node)
    _execute_command(dynamic_routing_command)
    _save_configuration_to_file(dynamic_routing_command, node)


def _configure_nodes_dynamic_routing() -> str:
    for node in NODES:
        _configure_node_dynamic_routing(node)


def _configure_node_ip_addreses(node: str) -> None:
    ip_conf_command: str = _get_ip_conf_command(node)
    _execute_command(ip_conf_command)
    _save_configuration_to_file(ip_conf_command, node, first_execution=True)


def _configure_nodes_ip_addreses() -> None:
    for node in NODES:
        _configure_node_ip_addreses(node)


def _configure_topology() -> None:
    _configure_nodes_ip_addreses()
    _configure_nodes_dynamic_routing()


if __name__ == '__main__':
    _configure_topology()
