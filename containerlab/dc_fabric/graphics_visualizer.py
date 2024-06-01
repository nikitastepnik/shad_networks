import typing

import matplotlib.pyplot as plt

from objects import ResultFabric, PORTS, SPINE_TYPES, OVERSUBSCRIPTIONS

COLORS = ['green', 'blue', 'purple', 'orange', 'brown']


def _get_graph_cost_by_oversub_coef(
    generated_fabrics: typing.List[ResultFabric],
) -> None:
    plt.figure(figsize=(10, 7))
    plt.xlabel('Oversubscription coef')
    plt.ylabel('Total cost')
    plt.xticks(OVERSUBSCRIPTIONS)
    plt.grid()
    plt.title(
        'Dependence of the total cost by oversubscription coef',
        fontsize=16
    )
    for fabric in generated_fabrics:
        plt.scatter(
            fabric.oversub_coef, fabric.total_cost,
            c=COLORS[fabric.oversub_coef]
        )
    plt.show()


def _get_graph_cost_by_ports_spin_types(
        generated_fabrics: typing.List[ResultFabric], used_ports: int = PORTS
) -> None:
    for spin_type in SPINE_TYPES:
        plt.figure(figsize=(10, 7))
        plt.xlabel('Count ports')
        plt.ylabel('Total cost')
        plt.xticks(used_ports)
        plt.grid()
        plt.title(
            'Dependence of the total cost by count ports, '
            f'spin type: {spin_type}',
            fontsize=16
        )
        for fabric in generated_fabrics:
            if (
                    fabric.spines_info.node_type == spin_type
                    and fabric.count_ports in used_ports
            ):
                plt.scatter(
                    fabric.count_ports, fabric.total_cost,
                    c=COLORS[0] if spin_type == SPINE_TYPES[0] else COLORS[1]
                )
        plt.show()


def _get_graph_cost_by_ports(
        generated_fabrics: typing.List[ResultFabric], used_ports: int = PORTS
) -> None:
    plt.figure(figsize=(10, 7))
    plt.xlabel('Count ports')
    plt.ylabel('Total cost')
    plt.xticks(used_ports)
    plt.grid()
    plt.title("Dependence of the total cost by count ports", fontsize=16)
    for fabric in generated_fabrics:
        if fabric.count_ports in used_ports:
            plt.scatter(fabric.count_ports, fabric.total_cost)
    plt.show()


def visualize_graphics(generated_fabrics: typing.List[ResultFabric]) -> None:
    ports_for_fabric_without_superspines = PORTS[:5]
    _get_graph_cost_by_ports(generated_fabrics)
    _get_graph_cost_by_ports(
        generated_fabrics, ports_for_fabric_without_superspines
    )
    _get_graph_cost_by_ports_spin_types(generated_fabrics)
    _get_graph_cost_by_ports_spin_types(
        generated_fabrics, ports_for_fabric_without_superspines
    )
    _get_graph_cost_by_oversub_coef(generated_fabrics)
