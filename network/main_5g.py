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

        users[u]["connections"].append([
                e.ends[1],
                traffic.x,
                traffic.y
            ])

    return list(users.values())


def main():
    subrun_count = 100
    ue_count  = 20
    data = []
    gnode_max_capacity = 160

    try:
        for gnode_capacity in range(gnode_max_capacity, 0, -1):
            print(f'Starting calculations for gnode capacity: {gnode_capacity} ...')

            solutions = []

            for _ in range(subrun_count):
                net = Network5G.random_ue_distance_weight(4, gnode_capacity, 200, ue_count, 100, 1)
                solution = solve(net, [100] * ue_count)
                solutions.append(format_solution(solution, net))

            subdata = {
                'gnode_capacity': gnode_capacity,
                'solutions': solutions
            }

            data.append(subdata)
    except Exception:
        pass

    print('Completed.')

    json_data = {
        'ues': ue_count,
        'gnodes': 16,
        'runs': data
    }

    with open('network/solutions_many_ue.json', 'w') as file:
        json.dump(json_data, file)


if __name__ == '__main__':
    main()
