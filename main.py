import math
import os
import random
from itertools import product
from mip import *
import matplotlib.pyplot as plt
import pandas as pd


# =================
''' PARAMETERS '''
# =================

p = []
file = input('Define the name of your input file: ')
if os.path.exists(file):
    print(f"File '{file}' loaded succesfully!")
    with open(file, 'r', encoding = 'utf-8') as f:
        for i, line in enumerate(f):
            if i == 0:
                values = line.split()

                # Number of jobs
                n = int(values[0])

                # Number of machines
                m = int(values[1])

            else:
                values = line.split()

                # Processing time of job j in machine i (p ij)
                l = []
                for j in range(len(values)):
                    l.append(int(values[j]))
                p.append(l)

else:
    print(f"Error: File '{file}' doesn't exist.")
    exit()

# Big number
M = 0
max_p_t = 0
for row in p:
    for element in row:
        M += element
        max_p_t = max(max_p_t, element)


# Shift length
T = max_p_t * random.choice([2, 3, 4, 5])

# Maximal number of shifts
S = max(1, math.ceil(M/T))

print(f"Big number created: {M}\n"
      f"Shift length created: {T}\n"
      f"Maximal number of shifts created: {S}\n")

mod = Model("Permutation flowshop scheduling") # sense = MINIMIZE

# =================
''' VARIABLES '''
# =================

# Complection time of job in machine i in position l (E il)
E = [[mod.add_var(name="E({},{})".format(i, l), var_type = INTEGER)
                               for l in range(n)]
                              for i in range(m)]

# If job j is scheduled in position l (Z jl)
Z = [[mod.add_var(name="Z({},{})".format(j, l), var_type=BINARY)
        for l in range(n)]
       for j in range(n)]

# If job in position l is scheduled in the shift s in machine i (gamma ils)
gamma = [[[mod.add_var(name="gamma({},{},{})".format(i, l, s), var_type=BINARY)
          for s in range(S)]
         for l in range(n)]
        for i in range(m)]

# =================
''' MODEL '''
# =================

# Objective function
mod.objective = minimize(E[m - 1][n - 1])

# Each job assigned to one position
for j in range(n):
    mod += xsum(Z[j][l] for l in range(n)) == 1

# Each position assigned to one job
for l in range(n):
    mod += xsum(Z[j][l] for j in range(n)) == 1

# For each machine two consecutive jobs don't overlap their processes
for (i, l) in product (range(m), range(n - 1)):
    mod += E[i][l] + xsum(p[i][j] * Z[j][l + 1] for j in range(n)) <= E[i][l + 1]

# Operations of a job in two consecutive machines do not overlap
for (i, l) in product (range(m - 1), range(n)):
    mod += E[i][l] + xsum(p[i + 1][j] * Z[j][l] for j in range(n)) <= E[i + 1][l]

# Complection time of the job scheduled in the first position in the first machine
mod += E[0][0] >= xsum(p[0][j] * Z[j][0] for j in range(n))

# Each operation that starts in a shift finishes in the same
for (i, l, s) in product (range(m), range(n), range(S)):
    mod += E[i][l] - (s + 1) * T <= M * (1 - gamma[i][l][s])

    mod += E[i][l] - xsum(p[i][j] * Z[j][l] for j in range(n)) + M * (1 - gamma[i][l][s]) >= T * s

# Each operation scheduled in one shift
for (i, l) in product (range(m), range(n)):
    mod += xsum(gamma[i][l][s] for s in range(S)) == 1

# =================
''' OPTIMIZATION '''
# =================

mod.emphasis = SearchEmphasis.FEASIBILITY
mod.max_gap = 0.00
status = mod.optimize(max_seconds=300)

complection_time_dict = {}
complection_time_list = []
scheduling = []
shifts_n_machines = []

if status == OptimizationStatus.OPTIMAL:
    print('\nOptimal solution cost {} found'.format(mod.objective_value))

elif status == OptimizationStatus.FEASIBLE:
    print('\nSol.cost {} found, best possible: {}'.format(mod.objective_value, mod.objective_bound))

elif status == OptimizationStatus.NO_SOLUTION_FOUND:
    print('\nNo feasible solution found, lower bound is: {}'.format(mod.objective_bound))

if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    print('\nSolution:')
    for v in mod.vars:
        if abs(v.x) > 1e-6: # only printing non-zeros
            print('{} : {}'.format(v.name, v.x))

            if v.name[0] == 'E':
                complection_time_dict[v.name] = v.x
                complection_time_list.append(v.name)
            elif v.name[0] == 'Z':
                scheduling.append(v.name)
            else:
                shifts_n_machines.append(v.name)

    print(complection_time_dict)
    print(scheduling)
    print(shifts_n_machines)

# =================
''' GANTT CHART '''
# =================

if mod.num_solutions:

    gantt_data = []
    assignements = {}
    for l in range(n):
        for j in range(n):
            if Z[j][l].x == 1.0:
                assignements[l] = j

    for i in range(m):
        for l in range(n):
            job_idx = assignements[l]
            end = E[i][l].x
            duration = p[i][job_idx]
            start = end - duration

            gantt_data.append({
                "Machine": f"M{i + 1}",
                "Start": start,
                "End": end,
                "Duration": duration,
                "Job": f"J{job_idx + 1}"
            })

    df = pd.DataFrame(gantt_data)
    fig, ax = plt.subplots(figsize=(15, 6))
    cmap = plt.get_cmap('tab20')
    job_colors = {f"J{j+1}": cmap(j) for j in range(n)}

    for i, row in df.iterrows():
        ax.barh(y=row["Machine"],
                width=row["Duration"],
                left=row["Start"],
                color=job_colors[row["Job"]],
                edgecolor='black',
                alpha=0.8)

        ax.text(x=row["Start"] + row["Duration"] / 2,
                y=row["Machine"],
                s=row["Job"],
                va='center', ha='center', color='black', fontweight='bold')

    max_time = int(df["End"].max())
    ax.set_xticks(range(0, max_time + 10, 10))
    ax.set_xlabel('Time')
    ax.set_ylabel('Machines')
    ax.set_title('Flowshop Scheduling Gantt Chart')
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    for s in range(S + 1):
        shift_position = s * T
        if shift_position < max_time:
            ax.axvline(x=shift_position,
                       color='red',
                       linestyle='-',
                       linewidth=2.5,
                       alpha=0.8,
                       zorder=0)

    for m_id in df["Machine"].unique():
        m_df = df[df["Machine"] == m_id].sort_values("Start")

        for i in range(len(m_df) - 1):
            actual_end = m_df.iloc[i]["End"]
            next_start = m_df.iloc[i + 1]["Start"]
            duration_gap = next_start - actual_end

            if duration_gap > 1e-3:
                ax.barh(y=m_id,
                        width=duration_gap,
                        left=actual_end,
                        color='#FFF59D',
                        hatch='///',
                        edgecolor='#FBC02D',
                        alpha=0.6,
                        zorder=2)

                if duration_gap > 50:
                    ax.text(x=actual_end + duration_gap / 2,
                            y=m_id,
                            s="Maintenance",
                            va='center', ha='center',
                            color='#7F6000',
                            fontsize=7,
                            fontweight='bold',
                            fontstyle='italic')

    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()

else:
    print('No solution found')