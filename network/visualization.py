from matplotlib import pyplot as plot
import numpy as np
import json


def get_data_from_solution(subruns):
    main_count = 0
    both_count = 0
    prot_count = 0

    main_total = 0
    prot_total = 0

    sub_count = 0

    for sub in subruns['solutions']:
        sub_count += 1
        for u in sub:
            for uc in u['connections']:
                main_total += uc[1]
                prot_total += uc[2]

                if uc[1] == 0.0: prot_count += 1
                if uc[2] == 0.0: main_count += 1
                else: both_count += 1

    return main_count / sub_count, both_count / sub_count,\
        prot_count / sub_count, main_total / sub_count, prot_total / sub_count


def get_connection_counts(solution):
    conn_counts = []
    conn_count_max = 0
    conn_count_min = 1000000

    for u in solution:
        conn_count = len(u['connections'])
        conn_count_max = max(conn_count_max, conn_count)
        conn_count_min = min(conn_count_min, conn_count)
        conn_counts.append(conn_count)

    return conn_counts, conn_count_min, conn_count_max


def get_connection_distribution_data(conn_counts):
    distribution = [0] * (max(conn_counts) + 1)
    for conn_count in conn_counts:
        distribution[conn_count] += 1

    return distribution


def save_diagram(title: str):
    plot.savefig('./network/diagrams/' + title.lower().replace(' ', '_'))
    plot.cla()
    plot.delaxes()


def set_diagram_labels(title: str, xlabel: str, ylabel: str):
    plot.xlabel(xlabel)
    plot.ylabel(ylabel)
    plot.title(title)


def set_diagram_limits(ymin = None, ymax = None, top_margin = 0.1):
    yminn, ymaxn = plot.ylim()
    ymin = ymin or yminn
    ymax = ymax or ymaxn
    if top_margin:
        ymax = ymax + (ymax - ymin) * top_margin

    plot.ylim(ymin, ymax)


def make_diagram(title: str, xlabel, ylabel, datarange, xticks, bars = None, names = None):
    set_diagram_labels(title, xlabel, ylabel)
    plot.xticks(datarange, xticks, rotation=60)
    if names:
        plot.legend(bars, names)
    plot.tight_layout()


def make_bar_diagram(title: str, xlabel, ylabel, datarange, xticks, *datapairs):
    prev = [0] * len(datarange); bars = []
    legend = isinstance(datapairs[0], tuple)
    names = [] if legend else None

    for pair in datapairs:
        name = None; data = None
        if legend: (name, data) = pair
        else: data = pair

        bar = plot.bar(datarange, data, bottom=prev)
        bars.append(bar)
        if legend: names.append(name)
        prev = [ p + d for p, d in zip(prev, data)]

    make_diagram(title, xlabel, ylabel, datarange, xticks, bars, names)


def connection_count_and_total_traffic(solutions):
    mcs = []; bcs = []; pcs = []; mts = []; pts = []

    for s in solutions['runs']:
        mc, bc, pc, mt, pt = get_data_from_solution(s)
        mcs.append(mc)
        bcs.append(bc)
        pcs.append(pc)
        mts.append(mt)
        pts.append(pt)

    sol_range = range(len(solutions['runs']))
    capacities = [ s['gnode_capacity'] for s in solutions['runs'] ]

    make_bar_diagram(
        'Number of connections',
        'Capacity of gNodeB to gateway connections',
        'Total number of connections',
        sol_range,
        capacities,
        ('main', mcs),
        ('both', bcs),
        ('protection', pcs)
    )
    set_diagram_limits()
    save_diagram('Number of connections')

    make_bar_diagram(
        'Traffic of connections',
        'Capacity of gNodeB to gateway connections',
        'Total traffic',
        sol_range,
        capacities,
        ('main', mts),
        ('protection', pts)
    )
    set_diagram_limits(ymin=mts[0] * 7 // 8)
    save_diagram('Traffic of connections')


def extend_list(thelist, length):
    return thelist + [0] * max(0, length - len(thelist))


def connection_count_distribution(solutions):
    ccdmin = 1000000; ccdmax = 0
    ccds = []; ccs = []

    sol_range = range(len(solutions['runs']))
    capacities = [ s['gnode_capacity'] for s in solutions['runs'] ]

    for subs in solutions['runs']:
        thecc = [];
        for s in subs['solutions']:
            cc, ccdmini, ccdmaxi = get_connection_counts(s)
            thecc += cc
            ccdmin = min(ccdmin, ccdmini)
            ccdmax = max(ccdmax, ccdmaxi)

        ccd = get_connection_distribution_data(thecc)
        ccs.append(thecc)
        ccds.append(ccd)

    ccrange = range(ccdmin, ccdmax + 1, 3)
    datapairs = []

    for cc in ccrange:
        data = []
        for i, ccd in enumerate(ccds):
            num = 0
            for j in range(cc, cc + 3):
                num += 0 if j >= len(ccds[i]) else ccds[i][j]

            data.append(num)
        
        datapairs.append((f'{cc}-{cc+2}', data))

    last = len(ccds) - 1
    specifics = [0, last * 3 // 4, last * 7 // 8, last * 15 // 16]
    specifics = [22, 23, 24, 25]
    for i, s in enumerate(specifics):
        subruns = len(solutions['runs'][0]['solutions'])
        ccd = extend_list(ccds[s], ccdmax + 1)[ccdmin:]
        ccd = np.array(ccd) / subruns

        plot.subplot(2, 2, i + 1)
        make_bar_diagram(
            f'Distribution at capacity {capacities[s]}',
            'Number of connections',
            'Number of UE',
            range(ccdmin, ccdmax + 1),
            [f'{i}' for i in range(ccdmin, ccdmax + 1)],
            ccd
        )
        set_diagram_limits(top_margin=0.2)

    plot.subplots_adjust(wspace=0.3)
    save_diagram('Specific Distribution on Low Capacity')
    plot.subplot(1, 1, 1)
    for i, s in enumerate(specifics):
        plot.subplot(2, 2, i + 1)
        plot.delaxes()

    colors = plot.rcParams['axes.prop_cycle'].by_key()['color']
    plot.boxplot(
        ccs, patch_artist=True,
        boxprops=dict(facecolor=colors[1], linewidth=0),
        medianprops=dict(color="black", linewidth=2),
        flierprops=dict(marker='.',))
    make_diagram(
        'UE Connection Distribution',
        'Capacity of gNodeB to gateway connections',
        'Number of connections per UE',
        sol_range, capacities)
    save_diagram('UE Connection Distribution')


def main():
    solutions = None
    with open('network/solutions_many_ue.json', 'r') as file:
        solutions = json.load(file)

    connection_count_and_total_traffic(solutions)
    connection_count_distribution(solutions)


if __name__ == '__main__':
    main()