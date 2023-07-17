import pulp
import random

# print(2 and 1)

random.seed(1)

# SETS

T = [
    'ΒΙΓΙΑΡΕΜΑΛ',
    'MHN ΨHNECE',
    'ΘΛΙΒΕΡΠΟΥΛ',
    'ΧΑΒΑΛΕΝΘΙΑ',
    'ΜΠΥΡΑΚΛΗΣ',
    'JUVETSI',
    'ΜΠΑΡΤΣΕΛΙΩΜΑ',
    'PEAΛ MANTPI'
]

D = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday'
]

P = pulp.LpVariable.dicts("P", [(i, p, d) for i in T for p in range(1,7) for d in D], cat= pulp.LpInteger)


for i in T:
    for p in range(1,7):
        for d in D:
            P[(i, p, d)] = random.choice([0, 4, 7, 10])


# for i in T:
#     print(f"\n\n{i}", end=" ")
#     for p in range(1,7):
#         print(f"\n\nPlayer {p}")
#         for d in D:
#             print(f"{d}: {P[(i, p, d)]}" ,end=" ")
# print('\n')

E = pulp.LpVariable.dicts("E", [(i) for i in T], cat= pulp.LpInteger)

for i in T:
    if i == 'ΒΙΓΙΑΡΕΜΑΛ' or i=='ΜΠΥΡΑΚΛΗΣ':
        E[(i)] = 1
    else:
        E[(i)] = 0

# PROBLEM SET UP

timetable = pulp.LpProblem("Weekly timetable", pulp.LpMaximize)

# Variables

x = pulp.LpVariable.dicts("x", [(i, j, d) for i in T for j in T if i!=j for d in D], cat= pulp.LpBinary)

# for i in T:
#     for j in T:
#         for d in D:
#             if i == j:
#                 del x[(i, j, d)]

# for i in T:
#     for j in T:
#         if i != j:
#             for d in D:
#                 x[(i, j, d)] = 0

# print(x)


# Objective function
# timetable += \
#             (40/8) * pulp.lpSum(x[(i,j,d)] for i in T for j in T if i!=j for d in D) \
#         + (40/48)  * pulp.lpSum((x[(i,j,d)] for j in T if j!=i) * (P[(i, p, d)] % (P[(i, p, d)]-1) for p in range(1,7)) for i in T for d in D) \
#         + (20/480) * pulp.lpSum((x[(i,j,d)] for j in T if j!=i) * (P[(i, p, d)] for p in range(1,7)) for i in T for d in D) \
#         , "obj"

timetable += \
            (40 / 10) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j for d in D) \
    ,"obj"
        # +   (40 / 48) * pulp.lpSum(P[(i, p, d)] % (P[(i, p, d)]-1) for i in T for d in D for j in T if j!=i and x[(i,j,d)] == 1 for p in range(1,7)) \
        # +  (20 / 480) * pulp.lpSum(P[(i, p, d)] for i in T for d in D for j in T if j!=i and x[(i,j,d)] == 1 for p in range(1,7)) \

# Constraints

for i in T:
    timetable += pulp.lpSum(x[(i,j,d)] for j in T if j!=i for d in D) <= 1 + (E[(i)] and 1)

# for i in T:
#     for j in T:
#         if i != j:
#                 timetable += pulp.lpSum(x[(i,j,d)] for d in D) <= 1, f"c2.{i}.{j}"

for i in T:
     for k in range(len(D)-1):
        timetable += (pulp.lpSum(x[(i,j,D[k])] for j in T if j!=i) + pulp.lpSum(x[(i,j,D[k+1])] for j in T if j!=i) <= 1)

for d in D:
    timetable += pulp.lpSum(x[(i,j,d)] for i in T for j in T if j!=i) <= 2

for i in T:
    for d in D:
        timetable += pulp.lpSum(x[(i,j,d)] for j in T if j!=i) * pulp.lpSum(P[(i, p, d)] % (P[(i, p, d)]-1) for p in range(1,7)) >= 4 * pulp.lpSum(x[(i,j,d)] for j in T if j!=i)

for i in T:
    for j in T:
        if i!=j:
            for d in D:
                timetable += x[(i,j,d)] == x[(j,i,d)]

# SOLUTION

timetable.solve(pulp.PULP_CBC_CMD(msg=False))

# Print the status of the solved LP
print("Status:", pulp.LpStatus[timetable.status])

# Print the value of the objective
print("Z =", pulp.value(timetable.objective))

# Print the value of the variables at the optimum
# for v in timetable.variables():
#     if v.varValue == 1:
#         print(f'{v.name} = {v.varValue:5.2f}')
# print(x)
weeklyMatches = []
for match in x:
    if x[match].varValue == 1:
        weeklyMatches.append(match)

weeklyMatches.sort(key=lambda x: D.index(x[2]))
for match in weeklyMatches:
    print(match)
