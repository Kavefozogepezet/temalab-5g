from solvers5g import solve
from network import Network5G
from random import randint
from matplotlib import pyplot
from icecream import ic
import json


def format_solution(solution, network):
    users = {}

    for e in solution:
        traffic = solution[e]
        if traffic.notraffic():
            continue

        u = e.ends[0]
        if not u in users:
            users[u] = {
                "position": network.node_pos(u),
                "connections": []
            }

        users[u]["connections"].append(
            {
                "target": e.ends[1],
                "main": traffic.x,
                "protection": traffic.y
            }
        )

    return {
        "ues": network.ue_count,
        "gnodes": network.g_count,
        "users": list(users.values())
    }


def main():
    ue_count  = 20
    data = []

    for gnode_capacity in range(160, 0, -1):
        net = Network5G.random_ue_distance_weight(4, gnode_capacity, 200, ue_count, 100, 1)
        try: solution = solve(net, [100] * ue_count)
        except Exception: break
        fs = format_solution(solution, net)
        fs['gnode_capacity'] = gnode_capacity
        data.append(fs)

    with open('solutions.json', 'w') as file:
        json.dump({'runs': data}, file)


if __name__ == '__main__':
    main()
