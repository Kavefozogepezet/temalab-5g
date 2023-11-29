from dataclasses import dataclass
from network import Network5G
from docplex.mp.model import Model
from icecream import ic


@dataclass
class EdgeData:
    x: int
    y: int

    def __repr__(self) -> str:
        return f'(x={self.x}, y={self.y})'

    def notraffic(self):
        return self.x == 0 and self.y == 0


def __get_solution(x, y):
    solution = {}
    for e in x:
        data = EdgeData(x[e].solution_value, y[e].solution_value)
        solution[e] = data
    return solution


def solve(network: Network5G, demands: [int], prot = 0.5):
    model = Model('network5g')

    E = (
        [ [ e for e in network.edges if e.ends[0] == u ] for u in network.ues ]
        + [ [ e for e in network.edges if e.ends[1] == g ] for g in network.gnodes ]
    )

    Eg = dict( (e.ends[0], e) for e in network.edges if e.ends[0] in network.gnodes )
    
    keys = [ e for e in network.edges if e.ends[0] in network.ues ]
    
    x = model.integer_var_dict(keys=keys, name='x')
    y = model.integer_var_dict(keys=keys, name='y')

    # bandwidth used on gNodeB->GW edges
    xg = dict( ( g, model.sum(x[e] for e in E[g]) ) for g in network.gnodes )
    yg = dict( ( g, model.sum(y[e] for e in E[g]) ) for g in network.gnodes )

    for u in network.ues:
        # user bandwidth demand is fullfilled
        model.add_constraint(
            model.sum( x[e] for e in E[u] ) == demands[u]
        )

        for ep in E[u]:
            # user demand still fullfilled if any one UE->GW tunnel is offline
            model.add_constraint(
                model.sum( x[e] + y[e] for e in E[u] if e != ep ) >= demands[u]
            )

            # capacity of UE->gNodeB edges are not exceeded
            model.add_constraint(
                model.sum( x[ep] + y[ep] <= ep.capacity )
            )

    for g in network.gnodes:
        model.add_constraint(
            xg[g] + yg[g] <= Eg[g].capacity
        )

    # cost of UE->gNodeB edges
    ugsum = model.sum(
        (x[e] + y[e] * prot) * e.cost for u in network.ues for e in E[u]
    )

    # cost of gNodeB->GW edges
    ggwsum = model.sum(
        (xg[g] + yg[g] * prot) * Eg[g].cost for g in network.gnodes
    )

    # minimize cost of all traffic
    model.minimize(ugsum + ggwsum)

    model.solve()
    return __get_solution(x, y)
