from solvers import *
from network import *
from matplotlib import pyplot as plot

def plot_users(network, users, paths, idx_list):
    colors = plot.rcParams['axes.prop_cycle'].by_key()['color']

    for u in idx_list:
        network.plot()
        network.plot_nodes([users[u].source, users[u].destination], colors[4])
        network.plot_path(paths[u].main, colors[0], 4)
        network.plot_path(paths[u].protection, colors[1], 4)
        plot.savefig('./network/diagrams/' + f'user{u}_with_protection', bbox_inches='tight')
        plot.cla()

def main():
    network = Network.random(3, 3)
    users = [
        User(0, 8, 0.5, 0),
        User(2, 6, 0.5, 0),
        User(7, 1, 0.5, 0)
    ]
    
    paths = solve_multiple_user_with_protection(network, users)
    plot_users(network, users, paths, [0, 1, 2])

if __name__ == '__main__':
    main()
