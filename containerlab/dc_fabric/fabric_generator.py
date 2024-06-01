from objects import *

import graph_visualizer
import graphics_visualizer


def _get_result_msg(result_fabric: ResultFabric) -> str:
    result_msg = 'Data center fabric with the following topology:\n'
    result_msg += f'  User ports count: {result_fabric.count_ports}\n'
    result_msg += f'  Oversubscription coeff: {result_fabric.oversub_coef}\n'
    result_msg += f'  Fabric with super spines: '
    result_msg += f'{result_fabric.is_fabric_with_super_spines}\n'
    result_msg += f'  {result_fabric.leafs_info.fabric_node_info}\n'
    result_msg += f'  {result_fabric.spines_info.fabric_node_info}\n'
    result_msg += f'  {result_fabric.transivers_info.fabric_node_info}\n'
    result_msg += f'  Fabric total cost: {result_fabric.total_cost}\n\n'
    return result_msg


def _save_result_to_file(
        result_fabric: typing.Optional[ResultFabric] = None,
        implemented_err_msg: typing.Optional[str] = '',
) -> None:
    with open('result.txt', 'a+') as result_file:
        if implemented_err_msg:
            result_file.write(implemented_err_msg)
            return
        if result_fabric:
            result_msg = _get_result_msg(result_fabric)
            result_file.write(result_msg)


def _calculate_spine_node(spine_type: str, count_links_to_spine: int) -> Spine:
    spine = Spine(spine_type, count_links_to_spine)
    spine.set_count_ports()
    return spine


def _calculate_leaf_node(leaf_type: str, oversub_coef: int) -> Leaf:
    leaf = Leaf(leaf_type, oversub_coef)
    leaf.set_leaf_downlink_ports_bandwidth()
    leaf.set_leaf_uplink_used_ports()
    if leaf.leaf_uplink_used_ports > Leaf.UP_LINK_COUNT_PORTS:
        leaf.recalc_leaf_uplink_used_ports()
    return leaf


def _gen_fabric_with_super_spines(
        count_ports: int, count_leafs: int,
        oversub_coef: int, leaf_type: str, spine_type: str,
) -> typing.Optional[ResultFabric]:
    # pod – group with 4 tors (level 0) connected with 4 spines (level 1)
    # each spine in pod connected with each super spine (level 2)
    spine_ports = (
        Spine.PORTS_COUNT_32 if spine_type == SPINE_TYPES[0]
        else Spine.PORTS_COUNT_64
    )
    leaf_node = _calculate_leaf_node(leaf_type, oversub_coef)
    count_links_to_spines = count_leafs * leaf_node.leaf_uplink_used_ports
    count_spines = math.ceil(
        math.ceil(count_links_to_spines / spine_ports) / Pod.SPINES_IN_POD
    )
    if count_spines > spine_ports:
        #  can't implement fabric even with super spines
        implemented_err_msg = (
            'Fabric implemented error, '
            f'count leafs: {count_leafs}, spin type: {spine_type}\n\n'
        )
        _save_result_to_file(implemented_err_msg=implemented_err_msg)
        return None
    count_superspines = count_spines // 2 # symmetry
    count_links_to_superspines = (
        count_spines * count_superspines
    )
    count_transivers = (count_links_to_spines + count_links_to_superspines) * 2
    fabric_leafs = FabricNodesData(Leaf.__name__, count_leafs, leaf_type)
    fabric_spines = FabricNodesData(
        Spine.__name__, count_spines + count_superspines, spine_type
    )
    fabric_transivers = FabricNodesData(
        Transiver.__name__, count_transivers, Transiver.TYPE
    )
    result_fabric = ResultFabric(
        count_ports, oversub_coef,
        fabric_leafs, fabric_spines, fabric_transivers,
        is_fabric_with_super_spines=True,
    )
    _save_result_to_file(result_fabric)
    return result_fabric


def _gen_fabric_without_super_spines(
        count_ports: int, count_leafs: int, oversub_coef: int,
        leaf_type: str, spine_type: str,
) -> ResultFabric:
    leaf_node = _calculate_leaf_node(leaf_type, oversub_coef)
    count_links_to_spines = count_leafs * leaf_node.leaf_uplink_used_ports
    spine_node = _calculate_spine_node(spine_type, count_links_to_spines)
    count_spines = math.ceil(
        count_links_to_spines / spine_node.count_spine_ports
    )
    if count_spines == 1:
        count_spines = 2  # avoid SPOF (single point of failure)
    count_transivers = count_links_to_spines * 2
    fabric_leafs = FabricNodesData(Leaf.__name__, count_leafs, leaf_type)
    fabric_spines = FabricNodesData(Spine.__name__, count_spines, spine_type)
    fabric_transivers = FabricNodesData(
        Transiver.__name__, count_transivers, Transiver.TYPE
    )
    result_fabric = ResultFabric(
        count_ports, oversub_coef,
        fabric_leafs, fabric_spines, fabric_transivers
    )
    _save_result_to_file(result_fabric)
    return result_fabric


def _generate_fabric(
        count_ports: int, oversub_coef: int, leaf_type: str, spine_type: str,
) -> typing.Optional[ResultFabric]:
    count_leafs = math.ceil(count_ports / Leaf.DOWN_LINK_COUNT_PORTS)
    if count_leafs > Spine.PORTS_COUNT_64 or (
            count_leafs > Spine.PORTS_COUNT_32 and spine_type==SPINE_TYPES[0]
    ):
        return _gen_fabric_with_super_spines(
            count_ports, count_leafs, oversub_coef, leaf_type, spine_type,
        )
    return _gen_fabric_without_super_spines(
        count_ports, count_leafs, oversub_coef, leaf_type, spine_type,
    )


def _generate_fabrics() -> typing.List[ResultFabric]:
    generated_fabrics: typing.List[ResultFabric] = []
    for count_ports in PORTS:
        for oversub_coef in OVERSUBSCRIPTIONS:
            for leaf_type in LEAF_TYPES:
                for spine_type in SPINE_TYPES:
                    generate_fabric: typing.Optional[
                        ResultFabric
                    ] = _generate_fabric(
                        count_ports, oversub_coef, leaf_type, spine_type,
                    )
                    if generate_fabric:
                        generated_fabrics.append(generate_fabric)
    return generated_fabrics


if __name__ == '__main__':
    generated_fabrics = _generate_fabrics()
    graphics_visualizer.visualize_graphics(generated_fabrics)
    graph_visualizer.visualize_graph(generated_fabrics)
