import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


pl_stats = pd.read_csv("PL stats after 10th nov.csv", index_col=0)
final_stats = pl_stats.copy()
pl_remaining = pd.read_csv("PL results after 10th nov (Matchday 11).csv", index_col=0)


pl_stats['goalChance'] = pl_stats['GF'] / pl_stats['Shots']
pl_stats['xGoalsPerGame'] = pl_stats['GF'] / (pl_stats['Wins'] + pl_stats['Draws'] + pl_stats['Losses'])
pl_stats['xConcededPerGame'] = pl_stats['GA'] / (pl_stats['Wins'] + pl_stats['Draws'] + pl_stats['Losses'])
pl_stats['xHomeGoalsPerGame'] = pl_stats['homeGoals'] / pl_stats['homeGames']
pl_stats['xAwayGoalsPerGame'] = pl_stats['awayGoals'] / pl_stats['awayGames']
pl_stats['xHomeConcededPerGame'] = pl_stats['homeConceded'] / pl_stats['homeGames']
pl_stats['xAwayConcededPerGame'] = pl_stats['awayConceded'] / pl_stats['awayGames']
average_home_conceded = pl_stats['xHomeConcededPerGame'].mean()
average_away_conceded = pl_stats['xAwayConcededPerGame'].mean()


pl_remaining.replace("", np.nan, inplace=True)
na_values = np.argwhere(pd.isna(pl_remaining.values))
remaining_matches = pd.DataFrame({
    'home': pl_remaining.index[na_values[:, 0]],
    'away': pl_remaining.columns[na_values[:, 1]]
})


def lambda_value(club, pl_stats, home, opposition):
    if(home):
        return pl_stats.loc[club, 'xHomeGoalsPerGame'] * (pl_stats.loc[opposition, 'xAwayConcededPerGame'] / average_away_conceded)
    else:
        return pl_stats.loc[club, 'xAwayGoalsPerGame'] * (pl_stats.loc[opposition, 'xHomeConcededPerGame'] / average_home_conceded)

# Simulate a single match
def simulate_match(home, away, pl_stats):
    lambda_home = lambda_value(home, pl_stats, True, away)
    lambda_away = lambda_value(away, pl_stats, False, home)
    home_goals = np.random.poisson(lambda_home)
    away_goals = np.random.poisson(lambda_away)
    
    if home_goals > away_goals:
        return home, away, home_goals, away_goals, 3, 0
    elif home_goals < away_goals:
        return home, away, home_goals, away_goals, 0, 3
    else:
        return home, away, home_goals, away_goals, 1, 1

def simulate_season(pl_stats, pl_remaining, final_stats):
    remaining_matches = pd.DataFrame({
        'home': pl_remaining.index[np.argwhere(pd.isna(pl_remaining.values))[:, 0]],
        'away': pl_remaining.columns[np.argwhere(pd.isna(pl_remaining.values))[:, 1]]
    })

    for _, row in remaining_matches.iterrows():
        home, away = row['home'], row['away']
        result = simulate_match(home, away, pl_stats)
        home_goals, away_goals = int(result[2]), int(result[3])
        home_points, away_points = int(result[4]), int(result[5])

        final_stats.loc[home, 'GF'] += home_goals
        final_stats.loc[away, 'GF'] += away_goals
        final_stats.loc[home, 'GA'] += away_goals
        final_stats.loc[away, 'GA'] += home_goals

        if home_points == 3:
            final_stats.loc[home, 'Points'] += 3
            final_stats.loc[home, 'Wins'] += 1
            final_stats.loc[away, 'Losses'] += 1
        elif away_points == 3:
            final_stats.loc[away, 'Points'] += 3
            final_stats.loc[away, 'Wins'] += 1
            final_stats.loc[home, 'Losses'] += 1
        else:
            final_stats.loc[home, 'Points'] += 1
            final_stats.loc[away, 'Points'] += 1
            final_stats.loc[home, 'Draws'] += 1
            final_stats.loc[away, 'Draws'] += 1

    final_stats = final_stats.sort_values('Points', ascending=False)
    return final_stats

np.random.seed(0)
sim_count = 1000
winners = []

for _ in range(sim_count):
    sim_final_stats = pl_stats.copy()
    sim_final_stats = simulate_season(pl_stats, pl_remaining, sim_final_stats)
    for team in final_stats.index:
        final_stats.loc[team, 'Points'] += sim_final_stats.loc[team, 'Points']
    winners.append(sim_final_stats.index[0])

win_count = pd.Series(winners).value_counts()
win_prob = win_count / sim_count

total_points = final_stats[["Points"]]
average_points = total_points / sim_count

win_count_data_frame = pd.DataFrame(win_count).reset_index()
win_count_data_frame.columns = ['team','wins']

win_prob_data_frame = pd.DataFrame(win_prob).reset_index()
win_prob_data_frame.columns = ['team','wins']

average_points_data_frame = pd.DataFrame(average_points).reset_index()
average_points_data_frame.columns = ['team','average_points']
average_points_data_frame = average_points_data_frame.sort_values(by='average_points', ascending=False)

win_count_data_frame.to_csv('data/winData.csv',index=False)
win_prob_data_frame.to_csv('data/winProbData.csv',index=False)
average_points_data_frame.to_csv('data/averagePointsData.csv',index=False)

print(win_count_data_frame.to_string(index=False))
print("\n")
print(win_prob_data_frame.to_string(index=False))
print("\n")
print(average_points_data_frame.to_string(index=False))

sns.set_style("whitegrid")
sns.set_palette("ch:s=.25,rot=-.25")
sns.barplot(x='team', y='wins', data=win_count_data_frame, errorbar=None, width=0.7)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.title("Win Simulations for Teams", fontsize=16)
plt.xlabel("Teams", fontsize=12)
plt.ylabel("Simulated Win Numbers", fontsize=12)
plt.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("wins.png")
plt.show()