import copy
import os
import subprocess
import typing

STUDENT_NAME = 'Nikita_Stepanov'
NODES_IP_INTERFACES_MAP = {
    'PC1': {
        'lo': '10.0.254.7/32',
        'eth1': '172.16.11.1/30',
    },
    'PC2': {
        'lo': '10.0.254.8/32',
        'eth1': '172.16.22.1/30',
    },
    'leaf1': {
        'lo': '10.0.254.5/32',
        'eth1': '172.16.112.2/30',
        'eth2': '172.16.111.2/30',
        'eth3': '172.16.11.2/30',
        'eth4': '172.16.113.2/30',
        'eth5': '172.16.114.2/30',
    },
    'leaf2': {
        'lo': '10.0.254.6/32',
        'eth1': '172.16.221.2/30',
        'eth2': '172.16.222.2/30',
        'eth3': '172.16.22.2/30',
        'eth4': '172.16.223.2/30',
        'eth5': '172.16.224.2/30',
    },
    'spine1': {
        'lo': '10.0.254.1/32',
        'eth1': '172.16.221.1/30',
        'eth2': '172.16.111.1/30',
    },
    'spine2': {
        'lo': '10.0.254.2/32',
        'eth1': '172.16.112.1/30',
        'eth2': '172.16.222.1/30',
    },
    'spine3': {
        'lo': '10.0.254.3/32',
        'eth1': '172.16.223.1/30',
        'eth2': '172.16.113.1/30',
    },
    'spine4': {
        'lo': '10.0.254.4/32',
        'eth1': '172.16.114.1/30',
        'eth2': '172.16.224.1/30',
    },
}
ASN_ID_MAP = {
    'PC1': 65100,
    'PC2': 65101,
    'leaf1': 65001,
    'leaf2': 65002,
    'spine1': 65000,
    'spine2': 65000,
    'spine3': 65200,
    'spine4': 65200,
}
BGP_ROUTING_NODES_COMMANDS = {
    'common': [
        '"ip prefix-list DC_LOCAL_SUBNET seq 5 permit 172.16.0.0/16 le 32"',
        '"ip prefix-list DC_LOCAL_SUBNET seq 10 permit 10.0.254.0/24 le 32"',
        '"route-map PERMIT_EBGP permit 10"',
        '"route-map ACCEPT_DC_LOCAL permit 10"',
        '"match ip address prefix-list DC_LOCAL_SUBNET"',
    ],
    'PC': [
        '"router bgp {ASN_ID}"',
        '"bgp router-id {LO_INT_WITHOUT_MASK}"',
        '"neighbor eth1 interface remote-as external"',
        '"address-family ipv4 unicast"',
        '"redistribute connected route-map ACCEPT_DC_LOCAL"',
        '"neighbor eth1 route-map PERMIT_EBGP in"',
        '"neighbor eth1 route-map PERMIT_EBGP out"'
    ],
    'leaf': [
        '"router bgp {ASN_ID}"',
        '"bgp router-id {LO_INT_WITHOUT_MASK}"',
        '"bgp bestpath as-path multipath-relax"',
        '"timers bgp 3 9"',
        '"neighbor FABRIC peer-group"',
        '"neighbor FABRIC remote-as external"',
        '"neighbor FABRIC advertisement-interval 0"',
        '"neighbor FABRIC timers connect 5"',
        '"neighbor eth1 interface peer-group FABRIC"',
        '"neighbor eth2 interface peer-group FABRIC"',
        '"neighbor eth4 interface peer-group FABRIC"',
        '"neighbor eth5 interface peer-group FABRIC"',
        '"neighbor eth3 interface remote-as external"',
        '"address-family ipv4 unicast"',
        '"redistribute connected route-map ACCEPT_DC_LOCAL"',
        '"neighbor FABRIC route-map PERMIT_EBGP in"',
        '"neighbor FABRIC route-map PERMIT_EBGP out"',
        '"neighbor eth3 route-map PERMIT_EBGP in"',
        '"neighbor eth3 route-map PERMIT_EBGP out"',
    ],
    'spine': [
        '"router bgp {ASN_ID}"',
        '"bgp router-id {LO_INT_WITHOUT_MASK}"',
        '"bgp bestpath as-path multipath-relax"',
        '"timers bgp 3 9"',
        '"neighbor FABRIC peer-group"',
        '"neighbor FABRIC remote-as external"',
        '"neighbor FABRIC advertisement-interval 0"',
        '"neighbor FABRIC timers connect 5"',
        '"neighbor eth1 interface peer-group FABRIC"',
        '"neighbor eth2 interface peer-group FABRIC"',
        '"address-family ipv4 unicast"',
        '"redistribute connected route-map ACCEPT_DC_LOCAL"',
        '"neighbor FABRIC route-map PERMIT_EBGP in"',
        '"neighbor FABRIC route-map PERMIT_EBGP out"',
    ]
}


class VtyshOptions:
    COMMAND_SEP = ' -c '


class Commands:
    CONNECT_TO_NODE_CONTAINER = (
        'sudo docker exec -it clab-frrlab4-{node} vtysh'
    )
    START_CONFIGURATION = 'conf'
    SAVE_CONFIGURATION = '"do wr"'
    SET_INTERFACE = '"int {interface}"'
    SET_IP_ADDRESS = '"ip address {address}"'
    SET_HOSTNAME = '"hostname {hostname}"'


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


def _get_bgp_routing_command(node: str, ) -> str:
    bgp_routing_command = ''
    bgp_routing_command += Commands.CONNECT_TO_NODE_CONTAINER.format(
        node=node
    )
    bgp_routing_command += (
        VtyshOptions.COMMAND_SEP + Commands.START_CONFIGURATION
    )
    bgp_common_commands_prep = VtyshOptions.COMMAND_SEP + VtyshOptions.COMMAND_SEP.join(
        BGP_ROUTING_NODES_COMMANDS['common']
    )
    bgp_routing_command += bgp_common_commands_prep
    if 'PC' in node:
        bgp_pc_commands = copy.deepcopy(BGP_ROUTING_NODES_COMMANDS['PC'])
        bgp_pc_commands[0] = bgp_pc_commands[0].format(ASN_ID=ASN_ID_MAP[node])
        bgp_pc_commands[1] = bgp_pc_commands[1].format(
            LO_INT_WITHOUT_MASK=NODES_IP_INTERFACES_MAP[node]['lo'].split('/')[0]
        )
        bgp_pc_commands_prep = VtyshOptions.COMMAND_SEP + VtyshOptions.COMMAND_SEP.join(bgp_pc_commands)
        bgp_routing_command += bgp_pc_commands_prep
    elif 'leaf' in node:
        bgp_leaf_commands = copy.deepcopy(BGP_ROUTING_NODES_COMMANDS['leaf'])
        bgp_leaf_commands[0] = bgp_leaf_commands[0].format(
            ASN_ID=ASN_ID_MAP[node],
        )
        bgp_leaf_commands[1] = bgp_leaf_commands[1].format(
            LO_INT_WITHOUT_MASK=NODES_IP_INTERFACES_MAP[node]['lo'].split('/')[0],
        )
        bgp_leaf_commands_prep = VtyshOptions.COMMAND_SEP + VtyshOptions.COMMAND_SEP.join(bgp_leaf_commands)
        bgp_routing_command += bgp_leaf_commands_prep
    else:
        bgp_spine_commands = copy.deepcopy(BGP_ROUTING_NODES_COMMANDS['spine'])
        bgp_spine_commands[0] = bgp_spine_commands[0].format(
            ASN_ID=ASN_ID_MAP[node],
        )
        bgp_spine_commands[1] = bgp_spine_commands[1].format(
            LO_INT_WITHOUT_MASK=NODES_IP_INTERFACES_MAP[node]['lo'].split('/')[0],
        )
        bgp_spine_commands_prep = VtyshOptions.COMMAND_SEP + VtyshOptions.COMMAND_SEP.join(bgp_spine_commands)
        bgp_routing_command += bgp_spine_commands_prep
    return bgp_routing_command


def _get_ip_conf_command(node: str) -> str:
    ip_conf_command = ''
    ip_conf_command += Commands.CONNECT_TO_NODE_CONTAINER.format(
        node=node
    )
    node_interfaces: typing.Dict[str, str] = NODES_IP_INTERFACES_MAP[node]
    ip_conf_command += (
        VtyshOptions.COMMAND_SEP + Commands.START_CONFIGURATION
    )
    for interface in node_interfaces:
        ip_conf_command += (
            VtyshOptions.COMMAND_SEP
            + Commands.SET_INTERFACE.format(
                interface=interface
            )
        )
        ip_conf_command += (
            VtyshOptions.COMMAND_SEP
            + Commands.SET_IP_ADDRESS.format(
                address=node_interfaces[interface]
            )
        )
    ip_conf_command += (
        VtyshOptions.COMMAND_SEP + Commands.SAVE_CONFIGURATION
    )
    return ip_conf_command


def _configure_node_bgp_routing(node: str) -> str:
    bgp_routing: str = _get_bgp_routing_command(node)
    _execute_command(bgp_routing)
    _save_configuration_to_file(bgp_routing, node)


def _configure_nodes_bgp_routing(nodes: typing.List[str], ) -> str:
    for node in nodes:
        _configure_node_bgp_routing(node)


def _configure_node_ip_addreses(node: str) -> None:
    ip_conf_command: str = _get_ip_conf_command(node)
    _execute_command(ip_conf_command)
    _save_configuration_to_file(ip_conf_command, node, first_execution=True)


def _configure_nodes_ip_addreses(nodes: typing.List[str], ) -> None:
    for node in nodes:
        _configure_node_ip_addreses(node)


def _configure_topology() -> None:
    nodes: typing.List[str] = NODES_IP_INTERFACES_MAP.keys()
    _configure_nodes_ip_addreses(nodes, )
    _configure_nodes_bgp_routing(nodes, )


if __name__ == '__main__':
    _configure_topology()
