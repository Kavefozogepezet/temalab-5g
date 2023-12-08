from networkx import DiGraph, draw_networkx, draw_networkx_edge_labels, get_edge_attributes, spring_layout, draw_networkx_edges, random_clustered_graph, get_node_attributes, draw_networkx_nodes
from matplotlib import pyplot
from random import randint
from math import sqrt
from numpy import random as r

class Edge:
    def __init__(self, ends: (int, int), cost, capacity):
        self.ends = tuple(ends)
        self.cost = cost
        self.capacity = capacity


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.ends == other.ends
    

    def __hash__(self) -> int:
        return hash(self.ends)
    

    def __str__(self) -> str:
        return '{' + ",".join(str(i) for i in self.ends) + '}'
    

    def __repr__(self):
        return self.__str__()
    

class Network:
    def __init__(self, edges = []) -> None:
        self.nodes = 0
        self.edges = set()
        self.g = DiGraph()
        for e in edges:
            self.add(*e)

    def add(self, *params):
        edge = Edge(*params)
        self.edges.add(edge)
        self.nodes = max(self.nodes, edge.ends[0] + 1, edge.ends[1] + 1)

    def plot(self):
        pos = self.__get_pos()
        draw_networkx(self.g, pos, node_color='none', edgecolors='black', with_labels=False)
        labels = get_edge_attributes(self.g, 'cost')
        #draw_networkx_edge_labels(self.g, pos)

    def plot_path(self, path:[Edge], color: str, width = 2):
        pos = self.__get_pos()
        path_edges = [tuple(e.ends) for e in path]
        labels = get_edge_attributes(self.g, 'cost')

        draw_networkx_edges(self.g, pos, path_edges, width=width, edge_color=color, arrowsize=20)
        #draw_networkx_edge_labels(self.g, pos, edge_labels=labels)

    def plot_nodes(self, nodes, color: str):
        pos = self.__get_pos()
        draw_networkx_nodes(self.g, pos, nodes, node_color=color)

    def show(self):
        pyplot.show()

    def __get_pos(self):
        if self.g is None:
            self.g = DiGraph()
            for e in self.edges:
                self.g.add_edge(*e.ends, cost=e.cost)

        pos = None
        try: pos = get_node_attributes(self.g,'pos')
        except: pos = spring_layout(self.g)
        return pos

    
    def random(node_table_size, degree):
        rand_pos = [[i * 100, j * 100] for i in range(0, node_table_size) for j in range(0, node_table_size)]
        for i in range(0, len(rand_pos)):
            rand_pos[i] = [rand_pos[i][0] + randint(0, 60), rand_pos[i][1] + randint(0, 60)]

        node_count = node_table_size ** 2

        node_pos = [(*(rand_pos[i]), i) for i in range(0, node_count)]
        network = Network()
        network.g = DiGraph()

        d2 = lambda n1, n2: (n1[0] - n2[0]) ** 2 + (n1[1] - n2[1]) ** 2

        for n in node_pos:
            network.g.add_node(n[2], pos=(n[0], n[1]))

        for n in node_pos:
            sorted_pos = sorted(node_pos, key=lambda s:d2(n, s))

            for i in range(1, degree + 1):
                s = sorted_pos[i]
                network.add((n[2], s[2]), max(1, int(sqrt(d2(n, s)))), 10)
                network.add((s[2], n[2]), max(1, int(sqrt(d2(n, s)))), 10)

        for e in network.edges:
            network.g.add_edge(*e.ends, cost=e.cost)

        return network


class Network5G(Network):
    def uniform_simple_network(ue_connections: [[]]):
        net = Network5G()
        net.ue_count = len(ue_connections)
        net.ues = range(net.ue_count)

        net.g_count = 0

        for ue in net.ues:
            for c in ue_connections[ue]:
                net.add((ue, net.ue_count + c), 1, 10)
                net.g_count = max(net.g_count, c + 1)

        net.gnodes = range(net.ue_count, net.ue_count + net.g_count)

        net.gateway = net.ue_count + net.g_count
        for gnode in net.gnodes:
            net.add((gnode, net.gateway), 1, 50)

        net.positions = [ (0, 0) ] * (net.gateway + 1)

        net.g = DiGraph()
        for i in net.ues:
            net.positions[i] = (0, ((net.ue_count - 1) / 2 - i) * 10)
            net.g.add_node(i, pos=net.positions[i])

        for i in net.gnodes:
            net.positions[i] = (50, ((net.g_count - 1) / 2 - i + net.ue_count) * 10)
            net.g.add_node(i, pos=net.positions[i])

        net.positions[net.gateway] = (100, 0)
        net.g.add_node(net.gateway, pos=net.positions[net.gateway])

        for e in net.edges:
            net.g.add_edge(*e.ends, cost=e.cost)

        return net
    

    def __distance(self, u, g):
        pu = self.positions[u]
        pg = self.positions[g]

        return sqrt((pu[0] - pg[0]) ** 2 + (pu[1] - pg[1]) ** 2)
    

    def random_ue_distance_weight(gnb_grid_size, gnb_capacity, gnb_radius, ue_count, ue_capacity, base_cost = 0):
        net = Network5G()

        net.ue_count = ue_count
        net.g_count = gnb_grid_size ** 2

        net.ues = range(net.ue_count)
        net.gnodes = range(net.ue_count, net.ue_count + net.g_count)

        net.gateway = net.ue_count + net.g_count

        net.positions = [ (0, 0) ] * (net.gateway + 1)
        net.positions[net.gateway] = (0, gnb_radius * gnb_grid_size)
        net.g.add_node(net.gateway, pos=net.positions[net.gateway])

        pos_multipliers = [ (x * 2 + 1, y * 2 + 1) for x in range(gnb_grid_size) for y in range(gnb_grid_size)]
        for (g, pm) in zip(net.gnodes, pos_multipliers):
            net.add((g, net.gateway), 1, gnb_capacity)
            net.positions[g] = (pm[0] * gnb_radius, pm[1] * gnb_radius)
            net.g.add_node(g, pos=net.positions[g])

        pos_range = 2 * gnb_radius * gnb_grid_size
        for u in net.ues:
            net.positions[u] = (randint(0, pos_range), randint(0, pos_range))
            net.g.add_node(u, pos=net.positions[u])
            for g in net.gnodes:
                net.add((u, g), round(net.__distance(u, g) / 1000 + base_cost, 2), ue_capacity)

        for e in net.edges:
            net.g.add_edge(*e.ends, cost=e.cost)

        return net


    def __init__(self) -> None:
        super().__init__()
        self.ue_count = 0
        self.ues = range(self.ue_count)

        self.g_count = 0
        self.gnodes = range(self.ue_count, self.ue_count + self.g_count)

        self.gateway = 1

        self.positions = []


    def node_pos(self, node_id):
        return self.positions[node_id]
