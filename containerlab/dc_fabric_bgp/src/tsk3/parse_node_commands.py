import enum
import os
import subprocess
import typing

NODES = ['PC1', 'PC2', 'leaf1', 'leaf2', 'spine1', 'spine2', 'spine3', 'spine4']
PC_LO_INT_ADDRESSES = {
    'PC1': '10.0.254.7',
    'PC2': '10.0.254.8',
}
LEAF_LO_INT_ADDRESSES = {
    'leaf1': '10.0.254.5',
    'leaf2': '10.0.254.6'
}
RESULT_FILE = 'output.txt'


class VtyshOptions(enum.Enum):
    COMMAND_SEP = ' -c '


class Commands(enum.Enum):
    DOCKER_PS = 'sudo docker ps'
    CONNECT_TO_NODE_CONTAINER_VTYSH = (
        'sudo docker exec -it clab-frrlab4-{node} vtysh'
    )
    CONNECT_TO_NODE_CONTAINER_BASH = (
        'sudo docker exec -it clab-frrlab4-{node} bash'
    )
    SH_RUN = '"sh run"'
    SH_IP_ROUTE = '"sh ip route"'
    PING = '"ping {address} -c 3"'
    TRACEROUTE = '"traceroute {address}"'
    SHOW_IP_BGP_SUMMARY = '"show ip bgp summary"'
    SHOW_IP_BGP_NEIGHBORS = '"show ip bgp neighbors"'
    SH_IP_BGP = '"sh ip bgp"'
    SH_IP_BGP_ADDR = '"sh ip bgp {address}"'


def _save_data_to_file(
        commands_parsed_data: str,
) -> None:
    if os.path.exists(RESULT_FILE):
        os.remove(RESULT_FILE)
    with open(RESULT_FILE, 'a') as file:
        file.write(commands_parsed_data)


def _pretty_format_output(
        get_parsed_data_func: typing.Callable,
) -> typing.Callable:
    def wrapper(*args, **kwargs):
        parsed_data = get_parsed_data_func(*args, **kwargs)
        parsed_data += '\n\n\n'
        return parsed_data
    return wrapper


def _get_command_result(command: str) -> str:
    process_output = subprocess.check_output(
        command,
        shell=True,
    ).decode().strip()
    return process_output


@_pretty_format_output
def _get_sh_ip_bgp_addr(node: str) -> str:
    if node == 'PC1':
        target_addr = LEAF_LO_INT_ADDRESSES['leaf2']
    else:
        target_addr = LEAF_LO_INT_ADDRESSES['leaf1']
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SH_IP_BGP_ADDR.value.format(address=target_addr)
    )
    sh_ip_bgp_addr = (
        command + '\n' + _get_command_result(command)
    )
    return sh_ip_bgp_addr


@_pretty_format_output
def _get_sh_ip_bgp(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SH_IP_BGP.value
    )
    sh_ip_bgp_data = (
        command + '\n' + _get_command_result(command)
    )
    return sh_ip_bgp_data


@_pretty_format_output
def _get_show_ip_bgp_neighbors_data(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SHOW_IP_BGP_NEIGHBORS.value
    )
    show_ip_bgp_neighbors_data = (
        command + '\n' + _get_command_result(command)
    )
    return show_ip_bgp_neighbors_data


@_pretty_format_output
def _get_show_ip_bgp_summary_data(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SHOW_IP_BGP_SUMMARY.value
    )
    show_ip_bgp_summary_data = (
        command + '\n' + _get_command_result(command)
    )
    return show_ip_bgp_summary_data


@_pretty_format_output
def _get_traceroute_parsed_data(node: str) -> str:
    traceroute_parsed_data = ''
    for pc_lo_addrr in PC_LO_INT_ADDRESSES.values():
        command = (
            Commands.CONNECT_TO_NODE_CONTAINER_BASH.value.format(node=node)
            + VtyshOptions.COMMAND_SEP.value
            + Commands.TRACEROUTE.value.format(address=pc_lo_addrr)
        )
        traceroute_parsed_data += (
            command + '\n' + _get_command_result(command) + '\n\n'
        )
    return traceroute_parsed_data


@_pretty_format_output
def _get_ping_parsed_data(node: str) -> str:
    ping_parsed_data = ''
    for pc_lo_addrr in PC_LO_INT_ADDRESSES.values():
        command = (
            Commands.CONNECT_TO_NODE_CONTAINER_BASH.value.format(node=node)
            + VtyshOptions.COMMAND_SEP.value
            + Commands.PING.value.format(address=pc_lo_addrr)
        )
        ping_parsed_data += (
            command + '\n' + _get_command_result(command) + '\n\n'
        )
    return ping_parsed_data


@_pretty_format_output
def _get_sh_ip_route_parsed_data(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SH_IP_ROUTE.value
    )
    sh_ip_route_parsed_data = (
        command + '\n' + _get_command_result(command)
    )
    return sh_ip_route_parsed_data


@_pretty_format_output
def _get_sh_run_parsed_data(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SH_RUN.value
    )
    sh_run_parsed_data = command + '\n' + _get_command_result(command)
    return sh_run_parsed_data


def _get_node_commands_parsed_data(node: str) -> str:
    node_commands_parsed_data = ''
    node_commands_parsed_data += _get_sh_run_parsed_data(node)
    node_commands_parsed_data += _get_sh_ip_route_parsed_data(node)
    node_commands_parsed_data += _get_ping_parsed_data(node)
    node_commands_parsed_data += _get_traceroute_parsed_data(node)
    node_commands_parsed_data += _get_show_ip_bgp_summary_data(node)
    node_commands_parsed_data += _get_show_ip_bgp_neighbors_data(node)
    node_commands_parsed_data += _get_sh_ip_bgp(node)
    if node in ['PC1', 'PC2']:
        node_commands_parsed_data += _get_sh_ip_bgp_addr(node)
    return node_commands_parsed_data


@_pretty_format_output
def _get_docker_ps_parsed_data() -> str:
    docker_ps_parsed_data = (
        Commands.DOCKER_PS.value + '\n'
        + _get_command_result(Commands.DOCKER_PS.value)
    )
    return docker_ps_parsed_data


def _get_commands_parsed_data() -> str:
    commands_parsed_data: str = ''
    commands_parsed_data += _get_docker_ps_parsed_data()
    for node in NODES:
        commands_parsed_data += _get_node_commands_parsed_data(node)
    return commands_parsed_data.strip()


if __name__ == '__main__':
    commands_parsed_data: str = _get_commands_parsed_data()
    _save_data_to_file(commands_parsed_data)
