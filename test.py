import pulp
import random

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
    # if i == 'ΒΙΓΙΑΡΕΜΑΛ' or i == 'ΜΠΥΡΑΚΛΗΣ':
         E[(i)] = 1
    # else:
        # E[(i)] = 0

# PROBLEM SET UP

timetable = pulp.LpProblem("Weekly timetable", pulp.LpMaximize)

# DECISION VARIABLES

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


# OBJECTIVE FUNCTION
# timetable += \
#             (40/8) * pulp.lpSum(x[(i,j,d)] for i in T for j in T if i!=j for d in D) \
#         + (40/48)  * pulp.lpSum((x[(i,j,d)] for j in T if j!=i) * (P[(i, p, d)] % (P[(i, p, d)]-1) for p in range(1,7)) for i in T for d in D) \
#         + (20/480) * pulp.lpSum((x[(i,j,d)] for j in T if j!=i) * (P[(i, p, d)] for p in range(1,7)) for i in T for d in D) \
#         , "obj"

timetable += \
             (40 / 10) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j for d in D) \
        #  +   (40 / 60) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
        #   +   (20 / 600) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j for d in D  for p in range(1,7) if P[(i, p, d)] ) \

        # +  (20 / 480) * pulp.lpSum(P[(i, p, d)] for i in T for d in D for j in T if j!=i and x[(i,j,d)] == 1 for p in range(1,7)) \

# CONSTRAINTS

# 1) A team can play:
#    a) up to once per week if they are not behind in games played
#    b) up to twice per week if they are behind in games played

for i in T:
    timetable += pulp.lpSum(x[(i,j,d)] for j in T if j!=i for d in D) <= 1 + (E[(i)] and 1)

# 2) A team can only play once vs another team per week

for i in T:
    for j in T:
        if i != j:
                timetable += pulp.lpSum(x[(i,j,d)] for d in D) <= 1


# 3) A team (that is behind in games played) can not play two consecutive days

for i in T:
     for k in range(len(D)-1):
        timetable += (pulp.lpSum(x[(i,j,D[k])] for j in T if j!=i) + pulp.lpSum(x[(i,j,D[k+1])] for j in T if j!=i) <= 1)

# 4) Max 1 game per day can be played

for d in D:
    timetable += pulp.lpSum(x[(i,j,d)] for i in T for j in T if j!=i) <= 2

# 5) A team can play when at least 4 of their players are available

for i in T:
    for d in D:
        timetable += pulp.lpSum(x[(i,j,d)] for j in T if j!=i) * pulp.lpSum(P[(i, p, d)] % (P[(i, p, d)]-1) for p in range(1,7)) >= 4 * pulp.lpSum(x[(i,j,d)] for j in T if j!=i)

# 6) Home and away games are the same

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

#PLAYERS ABLE TO PLAY

totalSum = 0
for match in x:
    if x[match].varValue == 1:
        # print(match[0],match[2])
        Sum =0
        for p in range(1,7):
            Sum += P[(match[0], p, match[2])] and 1
        totalSum += Sum
        print(f"{match[0]}-{match[2]}-{Sum}")
print(totalSum)

# result = pulp.lpSum(1 for match in x if x[match].varValue == 1 for p in range(1,7) if P[(match[0], p, match[2])] and 1)
# print(result)

# HOW MUCH IT FITS THE PLAYERS

totalSum = 0
for match in x:
    if x[match].varValue == 1:
        # print(match[0],match[2])
        Sum =0
        for p in range(1,7):
            Sum += P[(match[0], p, match[2])]
        totalSum += Sum
        print(f"{match[0]}-{match[2]}-{Sum}")
print(totalSum)