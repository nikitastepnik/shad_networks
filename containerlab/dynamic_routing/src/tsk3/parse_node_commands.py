import enum
import os
import subprocess
import typing

NODES = ['router1', 'router2', 'router3', 'PC1', 'PC2', 'PC3']
ROUTES_IP_ADDRESSES = {
    'router1': '10.10.10.1',
    'router2': '10.10.10.2',
    'router3': '10.10.10.3'
}
PC_IP_ADDRESSES = {
    'PC1': '192.168.11.4',
    'PC2': '192.168.22.4',
    'PC3': '192.168.33.4'
}


class VtyshOptions(enum.Enum):
    COMMAND_SEP = ' -c '


class Commands(enum.Enum):
    DOCKER_PS = 'sudo docker ps'
    CONNECT_TO_NODE_CONTAINER_VTYSH = (
        'sudo docker exec -it clab-frrlab1_1-{node} vtysh'
    )
    CONNECT_TO_NODE_CONTAINER_BASH = (
        'sudo docker exec -it clab-frrlab1_1-{node} bash'
    )
    SH_RUN = '"sh run"'
    SH_IP_ROUTE = '"sh ip route"'
    PING = '"ping {address} -c 3"'
    TRACEROUTE = '"traceroute {address}"'
    SHOW_ISIS_INTERFACES_BRIEF = '"show interface brief"'
    SHOW_ISIS_INTERFACES = '"show interface"'
    SHOW_ISIS_DATABASE = '"show isis database"'
    SHOW_ISIS_DATABASE_DETAIL = '"show isis database detail"'


def _save_data_to_file(
        commands_parsed_data: str,
) -> None:
    file_name = 'output.txt'
    if os.path.exists(file_name):
        os.remove(file_name)
    with open(file_name, 'a') as file:
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
def _get_sh_isis_database_data(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SHOW_ISIS_DATABASE.value
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SHOW_ISIS_DATABASE_DETAIL.value
    )
    sh_isis_interfaces_data = (
        command + '\n' + _get_command_result(command)
    )
    return sh_isis_interfaces_data


@_pretty_format_output
def _get_sh_isis_interfaces_data(node: str) -> str:
    command = (
        Commands.CONNECT_TO_NODE_CONTAINER_VTYSH.value.format(node=node)
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SHOW_ISIS_INTERFACES_BRIEF.value
        + VtyshOptions.COMMAND_SEP.value
        + Commands.SHOW_ISIS_INTERFACES.value
    )
    sh_isis_interfaces_data = (
        command + '\n' + _get_command_result(command)
    )
    return sh_isis_interfaces_data


@_pretty_format_output
def _get_traceroute_parsed_data(node: str) -> str:
    traceroute_parsed_data = ''
    addresses = None
    if 'router' in node:
        addresses = ROUTES_IP_ADDRESSES
    else:
        addresses = PC_IP_ADDRESSES
    for route_node in addresses:
        if route_node == node:
            continue
        command = (
            Commands.CONNECT_TO_NODE_CONTAINER_BASH.value.format(node=node)
            + VtyshOptions.COMMAND_SEP.value
            + Commands.TRACEROUTE.value.format(address=addresses[route_node])
        )
        traceroute_parsed_data += (
            command + '\n' + _get_command_result(command) + '\n\n'
        )
    return traceroute_parsed_data


@_pretty_format_output
def _get_ping_parsed_data(node: str) -> str:
    ping_parsed_data = ''
    addresses = None
    if 'router' in node:
        addresses = ROUTES_IP_ADDRESSES
    else:
        addresses = PC_IP_ADDRESSES
    for route_node in addresses:
        if route_node == node:
            continue
        command = (
            Commands.CONNECT_TO_NODE_CONTAINER_BASH.value.format(node=node)
            + VtyshOptions.COMMAND_SEP.value
            + Commands.PING.value.format(address=addresses[route_node])
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
    node_commands_parsed_data += _get_sh_isis_interfaces_data(node)
    node_commands_parsed_data += _get_sh_isis_database_data(node)
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
