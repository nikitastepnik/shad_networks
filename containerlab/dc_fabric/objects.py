from __future__ import annotations

import math
import typing

PORTS = [500, 1000, 1500, 2000, 3000, 4000, 5000, 8000, 10000]
OVERSUBSCRIPTIONS = [1, 2, 3, 4]
LEAF_TYPES = ['48x10G', '48x25G']
SPINE_TYPES = ['32x100G', '64x100G']


class ResultFabric:
    def __init__(
            self, count_ports: int, oversub_coef: int,
            leafs_info: FabricNodesData,
            spines_info: FabricNodesData, transivers_info: FabricNodesData,
            is_fabric_with_super_spines: bool = False,
    ) -> None:
        self.count_ports = count_ports
        self.oversub_coef = oversub_coef
        self.leafs_info = leafs_info
        self.spines_info = spines_info
        self.transivers_info = transivers_info
        self.is_fabric_with_super_spines = is_fabric_with_super_spines
        self.total_cost = self._get_total_cost()
        self.short_title = self._get_short_title()

    def _get_total_cost(self) -> int:
        return (
                self.leafs_info.cost
                + self.spines_info.cost + self.transivers_info.cost
        )

    def _get_short_title(self) -> str:
        return (
            f'Fabric Data Center, '
            f'Ports: {self.count_ports}; '
            f'Leafs: {self.leafs_info.count} [{self.leafs_info.node_type}]; '
            f'Spines: {self.spines_info.count} '
            f'[{self.spines_info.node_type}]; '
            f'Oversub coeff: {self.oversub_coef}; '
            f'Total cost: {self.total_cost}'
        )


class FabricNodesData:
    def __init__(
            self, name: str, count: int,
            node_type: typing.Optional[str] = None,
    ) -> None:
        self.name = name
        self.count = count
        self.node_type = node_type
        self.cost = self._get_cost_nodes()
        self.fabric_node_info = self._get_fabric_node_info()

    def _get_cost_nodes(self) -> int:
        if self.name == Leaf.__name__:
            return Leaf.COST * self.count
        elif self.name == Spine.__name__:
            spine_cost = (
                Spine.COST_32 if self.node_type == SPINE_TYPES[0]
                else Spine.COST_64
            )
            return spine_cost * self.count
        return Transiver.COST * self.count

    def _get_fabric_node_info(self) -> str:
        return (
            f'Node: {self.name}, count: {self.count}, '
            f'type: {self.node_type}, cost: {self.cost}'
        )


class Pod:
    LEAFS_IN_POD = 4
    SPINES_IN_POD = 4


class Transiver:
    COST = 10 ** 3
    TYPE = '100G'


class Spine:
    PORTS_COUNT_32 = 32
    PORTS_COUNT_64 = 64
    LINK_VOLUME = 100
    COST_32 = 2 * 10 ** 4
    COST_64 = 35 * 10 ** 3

    def __init__(self, spine_type: str, count_links_to_spine: int):
        self.spine_type = spine_type
        self.count_links_to_spine = count_links_to_spine
        self.count_spine_ports = None

    def set_count_ports(self) -> None:
        self.count_spine_ports = (
            Spine.PORTS_COUNT_32 if self.spine_type == SPINE_TYPES[0]
            else Spine.PORTS_COUNT_64
        )


class Leaf:
    DOWN_LINK_COUNT_PORTS = 48
    DOWN_LINK_VOLUME_10 = 10
    DOWN_LINK_VOLUME_25 = 25
    UP_LINK_COUNT_PORTS = 8
    UPLINK_VOLUME = 100
    COST = 10 ** 4

    def __init__(self, leaf_type: str, oversub_coef: int) -> None:
        self.leaf_type: str = leaf_type
        self.oversub_coef: int = oversub_coef
        self.leaf_uplink_used_ports = None
        self.leaf_downlink_ports_bandwidth = None

    def set_leaf_downlink_ports_bandwidth(
            self,
            leaf_count_ports: int = DOWN_LINK_COUNT_PORTS,
    ) -> None:
        leaf_downlink_port_bandwidth = (
            self.DOWN_LINK_VOLUME_10
            if self.leaf_type == LEAF_TYPES[0] else self.DOWN_LINK_VOLUME_25
        )
        self.leaf_downlink_ports_bandwidth = (
                leaf_downlink_port_bandwidth * leaf_count_ports
        )

    def set_leaf_uplink_used_ports(self) -> None:
        self.leaf_uplink_used_ports = math.ceil(
            self.leaf_downlink_ports_bandwidth /
            self.oversub_coef / self.UPLINK_VOLUME
        )

    def recalc_leaf_uplink_used_ports(self) -> None:
        leaf_uplink_used_ports_over = (
                self.leaf_uplink_used_ports - self.UP_LINK_COUNT_PORTS
        )
        self.set_leaf_downlink_ports_bandwidth(
            Leaf.DOWN_LINK_COUNT_PORTS - leaf_uplink_used_ports_over,
        )
