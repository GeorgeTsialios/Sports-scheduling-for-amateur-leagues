import pulp
import random
import timeit
import warnings
warnings.filterwarnings('ignore')

# SETS

T = [
    'ΑΡΜΑΔΑ',
    'ΒΙΓΙΑΡΕΜΑΛ',
    'ΓΙΟΥΒΕΤΣΙ',
    'ΘΛΙΒΕΡΠΟΥΛ',
    'ΙΠΠΟΚΡΑΤΕΙΟ',
    'ΚΟΥΒΑΔΟΡΟΙ',
    'ΜΗN ΨHNECE',
    'ΜΠΑΡΤΣΕΛΙΩΜΑ',
    'ΜΠΥΡΑΚΛΗΣ',
    'ΠΑΛΑΙΜΑΧΟΙ',
    'ΡΕAΛ MANTPI',
    'ΧΑΒΑΛΕΝΘΙΑ'
]

D = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
]

M = [] # matches that have already been played

# create teams' need for extra matches

E = pulp.LpVariable.dicts("E", [(i) for i in T], cat= pulp.LpInteger)

for i in T:
    E[(i)] = 0

# for every week of the tournament

for w in range(1, 13):

    random.seed(w+40)

    # create players' availability

    P = pulp.LpVariable.dicts("P", [(i, p, d) for i in T for p in range(1,7) for d in D], cat= pulp.LpInteger)


    for i in T:
        for p in range(1,7):
            for d in D:
                P[(i, p, d)] = random.choice([ 0, 4, 7, 10])

    # print players' availability

    # for i in T:
    #     print(f"\n\n{i}", end=" ")
    #     for p in range(1,7):
    #         print(f"\n\nPlayer {p}")
    #         for d in D:
    #             print(f"{d}: {P[(i, p, d)]}" ,end=" ")
    # print('\n')

    # write players' availability to file

    # with open('availability-12.txt', 'a') as f:
    #     f.write(f"----------------------------------- WEEK {w} -----------------------------------\n\n")
    #     for i in T:
    #         f.write(f"{i}")
    #         for p in range(1,7):
    #             f.write(f"\n\nPlayer {p}")
    #             f.write(' \n')
    #             for d in range(len(D)):
    #                 if d != len(D) - 1:
    #                     f.write(f"{D[d]}: {P[(i, p, D[d])]}, ")
    #                 else:
    #                     f.write(f"{D[d]}: {P[(i, p, D[d])]}")
    #         f.write('\n\n')
    
    # print teams' need for extra matches

    # for i in T:
    #     print(f"\n\n{i}: {E[(i)]}")

    # The teams that need extra matches

    teamsDouble = [i for i in T if E[(i)]]

    # Number of teams that need extra matches

    numberTeamsDouble = len(teamsDouble)

    # Problem Setup

    timetable = pulp.LpProblem("Weekly timetable", pulp.LpMaximize)

    # Decision Variables

    x = pulp.LpVariable.dicts("x", [(i, j, d) for i in T for j in T if i != j and [i,j] not in M for d in D], cat= pulp.LpBinary)

    # Objective Function

    if (w == 12):
        maxMatches = 0
        for i in T:
            if (E[(i)]<3):
                maxMatches += E[(i)]
            else:
                maxMatches += 2

        timetable += \
                    (50 / min(14, maxMatches)) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D) \
                +   (30 / min(84, maxMatches * 6)) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (20 / min(840, maxMatches * 60)) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] ) 

    elif (numberTeamsDouble >=2):
        timetable += \
                    (50 / 14) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D) \
                +   (30 / 84) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (10 / 840) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] ) \
                +   (10 / min(14, 2 * numberTeamsDouble)) * pulp.lpSum(x[(i, j, d)] * (E[(i)] and 1) for i in T for j in T if i != j and [i,j] not in M for d in D)
    else:
        timetable += \
                    (50 / 12) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D) \
                +   (30 / 72) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (20 / 720) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] )

    # Constraints

    # 1) A team can play:
    #    a) up to once per week if they are not behind in matches played
    #    b) up to twice per week if they are behind in matches played

    for i in T:
        timetable += pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in M for d in D) <= 1 + (E[(i)] and 1)

    # 2) A team can only play once vs another team per week

    for i in T:
        for j in T:
            if i != j and [i,j] not in M:
                    timetable += pulp.lpSum(x[(i,j,d)] for d in D) <= 1

   # 3) A team (that is behind in matches played) can not play two consecutive days

    for i in T:
        for k in range(len(D)-1):
            timetable += (pulp.lpSum(x[(i,j,D[k])] for j in T if i != j and [i,j] not in M) + pulp.lpSum(x[(i,j,D[k+1])] for j in T if i != j and [i,j] not in M) <= 1)

    # 4) Max 1 match per day can be played

    for d in D:
        timetable += pulp.lpSum(x[(i,j,d)] for i in T for j in T if i != j and [i,j] not in M) <= 2

    # 5) A team can play when at least 5 of its players are available

    for i in T:
        for d in D:
            timetable += pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in M) * pulp.lpSum(P[(i, p, d)] % (P[(i, p, d)]-1) for p in range(1,7)) >= 5 * pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in M)

    # 6) Home and away matches are the same

    for i in T:
        for j in T:
            if i !=j and [i,j] not in M:
                for d in D:
                    timetable += x[(i,j,d)] == x[(j,i,d)]

    # Solution

    tStart = timeit.default_timer()
    timetable.solve(pulp.PULP_CBC_CMD(msg=False))
    tEnd = timeit.default_timer()
    print(f"\n--------------- WEEK {w} ---------------")
    print(f"\nProblem solved in: {(tEnd-tStart):5.3f} seconds")

    # Status of the solved lp

    print("Status:", pulp.LpStatus[timetable.status])

    # Value of the objective function

    print(f"Z = {pulp.value(timetable.objective):5.2f}")

    # Weekly schedule

    print("\n\t       Schedule")

    if (w == 12):
        # Number of matches left to be played and which ones
        matchesLeft = []
        print(f"\nMatches left to be played: {maxMatches/2:1.0f} (", end="")
        for i in T:
            for j in T:
                if i != j and [i,j] not in M and [j,i] not in matchesLeft:
                    matchesLeft.append([i,j])
        for i in range(len(matchesLeft)):
            if i != len(matchesLeft)-1:
                print(f"{matchesLeft[i][0]} - {matchesLeft[i][1]}", end= ", ")
            else:
                print(f"{matchesLeft[i][0]} - {matchesLeft[i][1]})")

    else:
        # Number of teams able to play twice this week and which ones

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

    print("\nDay\t     - Home \t    - Away")
    weeklyMatches = []
    for match in x:
        if x[match].varValue == 1:
            weeklyMatches.append(match)

    # Add the weekly matches to the list of matches played

    for match in weeklyMatches:
        M.append([match[0], match[1]])

    # Sort the matches by day
    
    weeklyMatches.sort(key=lambda x: D.index(x[2]))

    # The singleMatches list contains the weekly matches just once (without the reverse match)

    singleMatches = []
    for index in range(len(weeklyMatches)-1):
        if index % 2 == 0:
            singleMatches.append(weeklyMatches[index])

    # Print the weekly schedule by day (if there are no matches on a day, print the day anyway)

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

    # Teams not playing this week

    teamsNotPlaying = T.copy()
    for i in singleMatches:
        if i[0] in teamsNotPlaying:
            teamsNotPlaying.remove(i[0])
        if i[1] in teamsNotPlaying:
            teamsNotPlaying.remove(i[1])

    if (w != 12):
        # Print the number of teams not playing this week and which ones

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

    # Players availability

    print("\n\t       Availability")

    # Sort first by team name, then by day

    def custom_sort(item):
        team_name = item[0]
        day = item[2]
        return (team_name, D.index(day))

    # Sort the weeklyMatches list using the custom sorting function
    weeklyMatches = sorted(weeklyMatches, key=custom_sort)

    # Number of players available for each team on its matchday

    print("\nTeam \t     - Matchday     - Players available")
    totalSum = 0
    for match in weeklyMatches:
        teamSum = 0
        for p in range(1,7):
            teamSum += P[(match[0], p, match[2])] and 1
        totalSum += teamSum
        print(f"{match[0]:12} - {match[2]:12} - {teamSum:1d}")

    if (w == 12):
        maxAvailablePlayers = min(84, maxMatches * 6)
    elif (numberTeamsDouble >= 2):
        maxAvailablePlayers = 84
    else:
        maxAvailablePlayers = 72
    print(f"Total number of available players: {totalSum} (max {maxAvailablePlayers})")

    # Amount of players' availability for each team on its matchday

    print("\nTeam \t     - Matchday     - Sum of players' availability")
    totalSum = 0
    for match in weeklyMatches:
        teamSum =0
        for p in range(1,7):
            teamSum += P[(match[0], p, match[2])]
        totalSum += teamSum
        print(f"{match[0]:12} - {match[2]:12} - {teamSum:2d}")

    if (w == 12):
        maxPlayersAvailability = min(840, maxMatches * 60)
    elif (numberTeamsDouble >= 2):
        maxPlayersAvailability = 840
    else:
        maxPlayersAvailability = 720
    print(f"Total sum of players' availability: {totalSum} (max {maxPlayersAvailability})\n")

    # Update the teams' need for extra matches

    teamsBehindWeeklyMatches = 0
    for i in T:
        teamWeeklyMatches = sum(1 for match in weeklyMatches if match[0] == i)
        if E[(i)] > 0:
            teamsBehindWeeklyMatches += teamWeeklyMatches
        if teamWeeklyMatches == 0:
            E[(i)] += 1
        elif teamWeeklyMatches == 2:
            E[(i)] -= 1

    # Games Played Difference 

    if w != 12 and numberTeamsDouble >= 2:
        print("\t       Games Played Difference\n")
        print(f"Teams behind in matches played, play {teamsBehindWeeklyMatches:1.0f} times (max {min(14,2 * numberTeamsDouble)})\n")

    # Print the matches played by each team

    print("\t       Matches played")

    print("\nTeam \t     - Opponents")
    for i in T:
        opponents = []
        for match in M:
            if match[0] == i:
                opponents.append(match[1])
        # opponents.sort()              Without alphabetical order, we can the see the order of the matches played
        print(f"{i:12} - ", end="")
        for j in opponents:
            if j != opponents[-1]:
                print(f"{j}", end=", ")
            else:
                print(f"{j}", end="")
        print("")
    print("")

    if w < 12:
        if len(M) == 132:        # in case that all matches are played by the 11th week, the program ends
            print("Tournament finished. All matches played!\n")
            break
        else:                               # if the tournament has not finished yet, ask for permission to continue to next week
            cont = input("Continue? (y/n): ")
            if cont == "y" or cont == "Y" or cont == "yes" or cont == "Yes" or cont == "YES":
                continue
            else:
                break
    else:   # Code for the 12th week, program ends right after
        if len(M) == 132:        # in case that all matches are played by the 12th week
            print("Tournament finished. All matches played!\n")
        else:                               # in case that not all matches are played, despite having the extra 12th week
            print(f"Tournament finished. {((132-len(M))/2):1.0f} {'matches' if (132-len(M))/2 > 1 else 'match'} not played!\n")