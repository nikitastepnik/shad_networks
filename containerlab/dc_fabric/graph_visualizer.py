import random
import typing

import networkx as nx
from matplotlib import pyplot as plt

from objects import ResultFabric

COLORS = ['green', 'blue', 'purple', 'orange', 'brown', 'red', 'yellow',
          'pink', 'gray', 'turquoise',
          'lavender', 'coral', 'indigo']


def visualize_graph(generated_fabrics: typing.List[ResultFabric]) -> None:
    for fabric in generated_fabrics:
        if fabric.count_ports > 3000:
            continue
        if fabric.is_fabric_with_super_spines:  # not implemented
            continue
        leafs_info = fabric.leafs_info
        spines_info = fabric.spines_info

        G = nx.Graph()

        leafs = [f'Leaf{k}' for k in range(1, leafs_info.count + 1)]
        spines = [f'Spine{k}' for k in range(1, spines_info.count + 1)]
        node_colors_leafs = [
            random.choice(COLORS) for _ in leafs
        ]
        node_colors_spines = ['gray' for _ in spines]
        all_colors = node_colors_leafs + node_colors_spines

        G.add_nodes_from(leafs, bipartite=0)
        G.add_nodes_from(spines, bipartite=1)

        for idx, leaf in enumerate(leafs):
            for spine in spines:
                G.add_edges_from(
                    [(leaf, spine, {"color": node_colors_leafs[idx]})]
                )

        pos = nx.bipartite_layout(G, spines)
        new_pos = {}
        for node, (x, y) in pos.items():
            new_pos[node] = (y, -x)

        edges = G.edges()
        edge_colors = [G[u][v]['color'] for u, v in edges]

        ax = plt.gca()
        ax.set_title(fabric.short_title, fontsize=7)

        nx.draw(
            G, new_pos, with_labels=True,
            node_color=all_colors,
            edge_color=edge_colors,
            width=2, font_size=8, node_size=500, node_shape='s',
            font_weight='bold', ax=ax
        )

        plt.show()
