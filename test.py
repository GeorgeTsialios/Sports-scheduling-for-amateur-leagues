from operator import indexOf
import pulp
import random
import timeit


# SETS

T = [
    'ΒΙΓΙΑΡΕΜΑΛ',
    'ΜΗN ΨHNECE',
    'ΘΛΙΒΕΡΠΟΥΛ',
    'ΧΑΒΑΛΕΝΘΙΑ',
    'ΜΠΥΡΑΚΛΗΣ',
    'ΓΙΟΥΒΕΤΣΙ',
    'ΜΠΑΡΤΣΕΛΙΩΜΑ',
    'ΡΕAΛ MANTPI'
]

D = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday'
]

matchesPlayed = []

for w in range(1, 9):

    random.seed(1)

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
        #         E[(i)] = 1
        # elif i == 'ΜΠΑΡΤΣΕΛΙΩΜΑ' or i == 'ΡΕAΛ MANTPI':
        #         E[(i)] = 2
        # else:
                E[(i)] = 0

    numberTeamsDouble = sum(E[(i)] and 1 for i in T)
    teamsDouble = [i for i in T if E[(i)]]

    # PROBLEM SET UP

    timetable = pulp.LpProblem("Weekly timetable", pulp.LpMaximize)

    # DECISION VARIABLES

    x = pulp.LpVariable.dicts("x", [(i, j, d) for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D], cat= pulp.LpBinary)

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

    if (sum(E.values())>=2):
        timetable += \
                    (40 / 10) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D) \
                +   (40 / 60) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (10 / 600) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D  for p in range(1,7) if P[(i, p, d)] ) \
                +   (10 / min(10, 2 * numberTeamsDouble)) * pulp.lpSum(x[(i, j, d)] * (E[(i)] and 1) for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D)
    else:
        timetable += \
                        (40 / 8) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D) \
                    +   (40 / 48) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                    +   (20 / 480) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D  for p in range(1,7) if P[(i, p, d)] ) \

    # CONSTRAINTS

    # 1) A team can play:
    #    a) up to once per week if they are not behind in games played
    #    b) up to twice per week if they are behind in games played

    for i in T:
        timetable += pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in matchesPlayed for d in D) <= 1 + (E[(i)] and 1)

    # 2) A team can only play once vs another team per week

    for i in T:
        for j in T:
            if i != j and [i,j] not in matchesPlayed:
                    timetable += pulp.lpSum(x[(i,j,d)] for d in D) <= 1


    # 3) A team (that is behind in games played) can not play two consecutive days

    for i in T:
        for k in range(len(D)-1):
            timetable += (pulp.lpSum(x[(i,j,D[k])] for j in T if i != j and [i,j] not in matchesPlayed) + pulp.lpSum(x[(i,j,D[k+1])] for j in T if i != j and [i,j] not in matchesPlayed) <= 1)

    # 4) Max 1 game per day can be played

    for d in D:
        timetable += pulp.lpSum(x[(i,j,d)] for i in T for j in T if i != j and [i,j] not in matchesPlayed) <= 2

    # 5) A team can play when at least 4 of their players are available

    for i in T:
        for d in D:
            timetable += pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in matchesPlayed) * pulp.lpSum(P[(i, p, d)] % (P[(i, p, d)]-1) for p in range(1,7)) >= 4 * pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in matchesPlayed)

    # 6) Home and away games are the same

    for i in T:
        for j in T:
            if i !=j and [i,j] not in matchesPlayed:
                for d in D:
                    timetable += x[(i,j,d)] == x[(j,i,d)]

    # SOLUTION

    tStart = timeit.default_timer()
    timetable.solve(pulp.PULP_CBC_CMD(msg=False))
    tEnd = timeit.default_timer()
    print(f"\n---------------WEEK {w}---------------")
    print(f"\nProblem solved in: {(tEnd-tStart):5.3f} seconds")

    # STATUS OF THE SOLVED LP

    print("Status:", pulp.LpStatus[timetable.status])

    # VALUE OF THE OBJECTIVE FUNCTION

    print(f"Z = {pulp.value(timetable.objective):5.2f}")

    print("\n\t       Schedule")

    print(f"\nTeams able to play twice this week: {numberTeamsDouble}", end=" ")
    if numberTeamsDouble > 0:
        print("(", end= "")
        for i in range(len(teamsDouble)):
            if i != len(teamsDouble)-1:
                print(f"{teamsDouble[i]}", end= ", ")
            else:
                print(f"{teamsDouble[i]}", end="")
        print(")")
    else:
        print("")
    # WEEKLY SCHEDULE

    print("\nDay \t     - Home \t    - Away")
    weeklyMatches = []
    for match in x:
        if x[match].varValue == 1:
            weeklyMatches.append(match)
    for match in weeklyMatches:
        matchesPlayed.append([match[0], match[1]])

    weeklyMatches.sort(key=lambda x: D.index(x[2]))
    singleMatches = []
    for index in range(len(weeklyMatches)-1):
        if index % 2 == 0:
            singleMatches.append(weeklyMatches[index])
    for day in D:
        counter = 0
        for i in range(len(singleMatches)):
            if singleMatches[i][2] == day:
                counter+=1
                break
        if counter:
            print(f"{singleMatches[i][2]:12} - {singleMatches[i][0]:12} - {singleMatches[i][1]:12}")
        else:   
            print(f"{day}")

    # TEAMS NOT PLAYING THIS WEEK
    teamsNotPlaying = T.copy()
    for i in singleMatches:
        if i[0] in teamsNotPlaying:
            teamsNotPlaying.remove(i[0])
        if i[1] in teamsNotPlaying:
            teamsNotPlaying.remove(i[1])
    print(f"\nTeams not playing this week: {len(teamsNotPlaying)}", end=" ")
    if len(teamsNotPlaying) > 0:
        print("(", end= "")
        for i in range(len(teamsNotPlaying)):
            if i != len(teamsNotPlaying)-1:
                print(f"{teamsNotPlaying[i]}", end= ", ")
            else:
                print(f"{teamsNotPlaying[i]})")
    else:
        print("")

    #PLAYERS ABLE TO PLAY

    print("\n\t       Availability")

    # Sort first by team name, then by day
    def custom_sort(item):
        team_name = item[0]
        day = item[2]
        return (team_name, D.index(day))

    # Sort the weeklyMatches list using the custom sorting function
    weeklyMatches = sorted(weeklyMatches, key=custom_sort)

    print("\nTeam \t     - Matchday     - Players available:")
    totalSum = 0
    for match in weeklyMatches:
        Sum =0
        for p in range(1,7):
            Sum += P[(match[0], p, match[2])] and 1
        totalSum += Sum
        print(f"{match[0]:12} - {match[2]:12} - {Sum:1d}")
    print(f"Total number of available players: {totalSum} (max {60 if numberTeamsDouble >= 2 else 48})")

    # HOW MUCH IT FITS THE PLAYERS
    print("\nTeam \t     - Matchday     - Sum of players' availability:")
    totalSum = 0
    for match in weeklyMatches:
        Sum =0
        for p in range(1,7):
            Sum += P[(match[0], p, match[2])]
        totalSum += Sum
        print(f"{match[0]:12} - {match[2]:12} - {Sum:2d}")
    print(f"Total sum of players' availability: {totalSum} (max {600 if numberTeamsDouble >= 2 else 480})\n")

    # GPDI
    if numberTeamsDouble > 0:
        print("\t       GPDI\n")
        print(f"Teams behind in games played, play {(sum(x[(i, j, d)].varValue * (E[(i)] and 1) for i in T for j in T if i != j and [i,j] not in matchesPlayed for d in D)):1.0f} times (max {min(10,2 * numberTeamsDouble)})\n")

    # print(matchesPlayed)
    # if ['ΡΕAΛ MANTPI', 'ΜΠΥΡΑΚΛΗΣ'] in matchesPlayed:
    #     print('true')

    if w < 8:
        if len(matchesPlayed) == 56:
            print("Tournament finished. All matches played!\n")
            break
        else:
            cont = input("Continue? (y/n): ")
            if cont == "y" or cont == "Y" or cont == "yes" or cont == "Yes" or cont == "YES":
                continue
            else:
                break
    else:
        if len(matchesPlayed) == 56:
            print("Tournament finished. All matches played!\n")
        else:
            print(f"Tournament finished. {56-len(matchesPlayed)} matches not played!\n")