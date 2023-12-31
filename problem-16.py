import pulp
import random
import timeit
import warnings
warnings.filterwarnings('ignore')

# SETS

T = [
    'ΑΝΩΝΥΜΟΙ',
    'ΑΡΜΑΔΑ',
    'ΒΙΓΙΑΡΕΜΑΛ',
    'ΓΙΟΥΒΕΤΣΙ',
    'ΘΛΙΒΕΡΠΟΥΛ',
    'ΙΠΠΟΚΡΑΤΕΙΟ',
    'ΚΟΥΒΑΔΟΡΟΙ',
    'ΜΗN ΨHNECE',
    'ΜΠΑΡΤΣΕΛΙΩΜΑ',
    'ΜΠΡΙΖΑΔΕΣ',
    'ΜΠΥΡΑΚΛΗΣ',
    'ΠΑΛΑΙΜΑΧΟΙ',
    'ΠΑΛΤΕΙΡΟΣ',
    'ΡΕAΛ MANTPI',
    'ΧΑΒΑΛΕΝΘΙΑ',
    'ΨΥΣΤΕΣ'
]

D = [
    'Monday    19:00',
    'Monday    21:00',
    'Tuesday   19:00',
    'Tuesday   21:00',
    'Wednesday 19:00',
    'Wednesday 21:00', 
    'Thursday  19:00',
    'Thursday  21:00',
    'Friday    19:00',
    'Friday    21:00'
]

# matches that have already been played

M = [] 

# create teams' need for extra matches and initialize to 0

E = pulp.LpVariable.dicts("E", [(i) for i in T], cat= pulp.LpInteger)

for i in T:
    E[(i)] = 0

# create players' availability

P = pulp.LpVariable.dicts("P", [(i, p, d) for i in T for p in range(1,7) for d in D], cat= pulp.LpInteger)

# for every week of the tournament

for w in range(1, 17):

    random.seed(w+10)

    for i in T:
        for p in range(1,7):
            for d in D:
                P[(i, p, d)] = random.choice([0, 4, 7, 10])

    # print players' availability

    # for i in T:
    #     print(f"\n\n{i}", end=" ")
    #     for p in range(1,7):
    #         print(f"\n\nPlayer {p}")
    #         for d in D:
    #             print(f"{d}: {P[(i, p, d)]}" ,end=" ")
    # print('\n')

    # write players' availability to file

    # with open('availability-16.txt', 'a') as f:
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

    if (w == 16):
        maxMatches = 0
        for i in T:
            if (E[(i)]<3):
                maxMatches += E[(i)]
            else:
                maxMatches += 2

        timetable += \
                    (50 / min(20, maxMatches)) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D) \
                +   (30 / min(120, maxMatches * 6)) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (20 / min(1200, maxMatches * 60)) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in M for d in D for p in range(1,7)) 

    elif (numberTeamsDouble >=2):
        timetable += \
                    (50 / (20 if numberTeamsDouble >=4 else 18)) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D) \
                +   (30 / (120 if numberTeamsDouble >=4 else 108)) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (10 / (1200 if numberTeamsDouble >=4 else 1080)) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in M for d in D for p in range(1,7)) \
                +   (10 / min(20, 2 * numberTeamsDouble)) * pulp.lpSum(x[(i, j, d)] * (E[(i)] and 1) for i in T for j in T if i != j and [i,j] not in M for d in D)
    else:
        timetable += \
                    (50 / 16) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D) \
                +   (30 / 96) * pulp.lpSum(x[(i, j, d)] for i in T for j in T if i != j and [i,j] not in M for d in D  for p in range(1,7) if P[(i, p, d)] and 1) \
                +   (20 / 960) * pulp.lpSum(x[(i, j, d)] * P[(i, p, d)] for i in T for j in T if i != j and [i,j] not in M for d in D for p in range(1,7))

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
        for k in range(len(D)-2):
            if k % 2 == 0:
                timetable += (pulp.lpSum(x[(i,j,D[k])] for j in T if i != j and [i,j] not in M) + pulp.lpSum(x[(i,j,D[k+1])] for j in T if i != j and [i,j] not in M) + pulp.lpSum(x[(i,j,D[k+2])] for j in T if i != j and [i,j] not in M) + pulp.lpSum(x[(i,j,D[k+3])] for j in T if i != j and [i,j] not in M) <= 1)
            else:
                timetable += (pulp.lpSum(x[(i,j,D[k])] for j in T if i != j and [i,j] not in M) + pulp.lpSum(x[(i,j,D[k+1])] for j in T if i != j and [i,j] not in M) + pulp.lpSum(x[(i,j,D[k+2])] for j in T if i != j and [i,j] not in M) <= 1)

    # 4) Home and away matches are the same

    for i in T:
        for j in T:
            if i != j and [i,j] not in M:
                for d in D:
                    timetable += x[(i,j,d)] == x[(j,i,d)]

    # 5) Max 1 match per time slot can be played

    for d in D:
        timetable += pulp.lpSum(x[(i,j,d)] for i in T for j in T if i != j and [i,j] not in M) <= 2

    # 6) A team can play when at least 5 of its players are available

    for i in T:
        for d in D:
            timetable += pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in M) * pulp.lpSum(P[(i, p, d)] and 1 for p in range(1,7)) >= 5 * pulp.lpSum(x[(i,j,d)] for j in T if i != j and [i,j] not in M)

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

    print("\n \t\t  Schedule")

    if (w == 16):
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

    print("\nDay\t\t- Home \t\t  - Away")
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
            print(f"{singleMatches[i][2]:15} - {singleMatches[i][0]:15} - {singleMatches[i][1]:15}")
        else:   
            print(f"{day}")

    # Teams not playing this week

    teamsNotPlaying = T.copy()
    for i in singleMatches:
        if i[0] in teamsNotPlaying:
            teamsNotPlaying.remove(i[0])
        if i[1] in teamsNotPlaying:
            teamsNotPlaying.remove(i[1])

    if (w != 16):
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

    print("\n\t\t  Availability")

    # Sort first by team name, then by day

    def custom_sort(item):
        team_name = item[0]
        day = item[2]
        return (team_name, D.index(day))

    # Sort the weeklyMatches list using the custom sorting function
    weeklyMatches = sorted(weeklyMatches, key=custom_sort)

    # Number of players available for each team on its matchday

    print("\nTeam \t\t- Matchday\t  - Players available")
    totalSum = 0
    for match in weeklyMatches:
        teamSum = 0
        for p in range(1,7):
            teamSum += P[(match[0], p, match[2])] and 1
        totalSum += teamSum
        print(f"{match[0]:15} - {match[2]:15} - {teamSum:1d}")

    if (w == 16):
        maxAvailablePlayers = min(120, maxMatches * 6)
    elif (numberTeamsDouble >= 4):
        maxAvailablePlayers = 120
    elif (numberTeamsDouble >= 2):
        maxAvailablePlayers = 108
    else:
        maxAvailablePlayers = 96
    print(f"Total number of available players: {totalSum} (max {maxAvailablePlayers})")

    # Amount of players' preference for each team on its matchday

    print("\nTeam \t\t- Matchday\t  - Sum of players' preference")
    totalSum = 0
    for match in weeklyMatches:
        teamSum =0
        for p in range(1,7):
            teamSum += P[(match[0], p, match[2])]
        totalSum += teamSum
        print(f"{match[0]:15} - {match[2]:15} - {teamSum:2d}")

    if (w == 16):
        maxPlayersPreference = min(1200, maxMatches * 60)
    elif (numberTeamsDouble >= 4):
        maxPlayersPreference = 1200
    elif (numberTeamsDouble >= 2):
        maxPlayersPreference = 1080
    else:
        maxPlayersPreference = 960
    print(f"Total sum of players' preference: {totalSum} (max {maxPlayersPreference})\n")

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

    if w != 16 and numberTeamsDouble >= 2:
        print("\t\t  Games Played Difference\n")
        print(f"Teams behind in matches played, play {teamsBehindWeeklyMatches:1.0f} times (max {min(20,2 * numberTeamsDouble)})\n")

    # Print the matches played by each team

    print("\t\t  Matches played")

    print("\nTeam \t\t- Opponents")
    for i in T:
        opponents = []
        for match in M:
            if match[0] == i:
                opponents.append(match[1])
        # opponents.sort()              Without alphabetical order, we can the see the order of the matches played
        print(f"{i:15} - ", end="")
        for j in opponents:
            if j != opponents[-1]:
                print(f"{j}", end=", ")
            else:
                print(f"{j}", end="")
        print("")
    print("")

    if w < 16:
        if len(M) == 240:        # in case that all matches are played by the 15th week, the program ends
            print("Tournament finished. All matches played!\n")
            break
        else:                    # if the tournament has not finished yet, ask for permission to continue to next week
            cont = input("Continue? (y/n): ")
            if cont == "y" or cont == "Y" or cont == "yes" or cont == "Yes" or cont == "YES":
                continue
            else:
                break
    else:   # Code for the 16th week, program ends right after
        if len(M) == 240:        # in case that all matches are played by the 16th week
            print("Tournament finished. All matches played!\n")
        else:                    # in case that not all matches are played, despite having the extra 16th week
            print(f"Tournament finished. {((240-len(M))/2):1.0f} {'matches' if (240-len(M))/2 > 1 else 'match'} not played!\n")