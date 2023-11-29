from dataclasses import dataclass
from network import Network
from docplex.mp.model import Model
from network import Edge, Network
from random import randint, sample

def solve_k_routes(network: Network, source, destination, k):
    model = Model('network')

    selected = model.binary_var_dict(keys=network.edges, name='selected')
    cost = model.integer_var(name='cost', lb=0)

    model.minimize(cost)

    model.add_constraint(
        cost == model.sum(selected[e] * e.cost for e in network.edges)
    )
    
    for i in range(network.nodes):
        count = 0
        if i == source: count = k
        elif i == destination: count = -k

        out_sum = model.sum(selected[e] for e in network.edges if i == e.ends[0])
        in_sum = model.sum(selected[e] for e in network.edges if i == e.ends[1])

        model.add_constraint(
            count == out_sum - in_sum
        )

    model.solve()
    path = []
    for edge in selected:
        if selected[edge].solution_value == 1:
            path.append(edge)

    return path


@dataclass
class User:
    source: int
    destination: int
    protection: float = 1
    demand: int = randint(1, 9)


def solve_multiple_user(network: Network, users: [User]):
    model = Model('network')

    selections = []
    costs = []

    for u in range(len(users)):
        selections.append(model.binary_var_dict(keys=network.edges, name=f'user{u}_selection'))
        costs.append(model.integer_var(name=f'user{u}_cost', lb=0))

        model.add_constraint(
            costs[u] == model.sum(selections[u][e] * e.cost for e in network.edges)
        )
    
        for i in range(network.nodes):
            count = 0
            if i == users[u].source: count = 1
            elif i == users[u].destination: count = -1

            out_sum = model.sum(selections[u][e] for e in network.edges if i == e.ends[0])
            in_sum = model.sum(selections[u][e] for e in network.edges if i == e.ends[1])

            model.add_constraint(
                count == out_sum - in_sum
            )

    model.minimize(model.sum(cost for cost in costs))

    for e in network.edges:
        throughput = model.sum(selections[u][e] * users[u].demand for u in range(len(users)))
        model.add_constraint(throughput <= e.capacity)

    model.solve()

    paths = []
    for u in range(len(users)):
        path = []
        for edge in selections[u]:
            if selections[u][edge].solution_value == 1:
                path.append(edge)
        paths.append(path)
    return paths


@dataclass
class Path:
    main: [Edge]
    protection: [Edge]


def solve_multiple_user_with_protection(network: Network, users: [User]):
    model = Model('network')

    x = []
    y = []
    costs = []

    for u in range(len(users)):
        x.append(model.binary_var_dict(keys=network.edges, name=f'user{u}_x'))
        y.append(model.binary_var_dict(keys=network.edges, name=f'user{u}_y'))
        costs.append(model.integer_var(name=f'user{u}_cost', lb=0))

        model.add_constraint(
            costs[u] == model.sum((x[u][e] + y[u][e] * users[u].protection) * e.cost for e in network.edges)
        )
    
        for i in range(network.nodes):
            count = 0
            if i == users[u].source: count = 1
            elif i == users[u].destination: count = -1

            io_sum = lambda s, end: model.sum(s[u][e] for e in network.edges if i == e.ends[end])

            model.add_constraint(count == io_sum(x, 0) - io_sum(x, 1))
            model.add_constraint(count == io_sum(y, 0) - io_sum(y, 1))

    for e in network.edges:
        for u in range(len(users)):
            model.add_constraint(x[u][e] + y[u][e] <= 1)

        throughput = model.sum((x[u][e] + y[u][e]) * users[u].demand for u in range(len(users)))
        model.add_constraint(throughput <= e.capacity)

    model.minimize(model.sum(cost for cost in costs))
    model.solve()

    paths = []
    for u in range(len(users)):
        main_path = []
        protection_path = []

        for e in network.edges:
            if x[u][e].solution_value == 1:
                main_path.append(e)
            elif y[u][e].solution_value == 1:
                protection_path.append(e)

        paths.append(Path(
            main_path,
            protection_path
        ))

    return paths
