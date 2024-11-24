import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns


pl_stats = pd.read_csv("PL stats after 10th nov.csv", index_col=0)
final_stats = pl_stats.copy()
pl_remaining = pd.read_csv("PL results after 10th nov (Matchday 11).csv", index_col=0)


pl_stats['goalChance'] = pl_stats['GF'] / pl_stats['Shots']
pl_stats['xGoalsPerGame'] = pl_stats['GF'] / (pl_stats['Wins'] + pl_stats['Draws'] + pl_stats['Losses'])
pl_stats['xConcededPerGame'] = pl_stats['GA'] / (pl_stats['Wins'] + pl_stats['Draws'] + pl_stats['Losses'])
pl_stats['xShotsPerGame'] = pl_stats['Shots'] / (pl_stats['Wins'] + pl_stats['Draws'] + pl_stats['Losses'])


pl_remaining.replace("", np.nan, inplace=True)
na_values = np.argwhere(pd.isna(pl_remaining.values))
remaining_matches = pd.DataFrame({
    'home': pl_remaining.index[na_values[:, 0]],
    'away': pl_remaining.columns[na_values[:, 1]]
})


def lambda_value(club, pl_stats, home):
    if(home):
        return pl_stats.loc[club, 'xGoalsPerGame']
    else:
        return pl_stats.loc[club, 'xConcededPerGame']

# Simulate a single match
def simulate_match(home, away, pl_stats):
    lambda_home = lambda_value(home, pl_stats, True)
    lambda_away = lambda_value(away, pl_stats, False)
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
    return final_stats.index[0]

np.random.seed(0)
sim_count = 10000
winners = []

for _ in range(sim_count):
    sim_final_stats = final_stats.copy()
    winners.append(simulate_season(pl_stats, pl_remaining, sim_final_stats))

win_count = pd.Series(winners).value_counts()
win_prob = win_count / sim_count

win_count_data_frame = pd.DataFrame(win_count).reset_index()
win_count_data_frame.columns = ['team','wins']

win_prob_data_frame = pd.DataFrame(win_prob).reset_index()
win_prob_data_frame.columns = ['team','wins']

win_count_data_frame.to_csv('data/winData.csv',index=False)
win_prob_data_frame.to_csv('data/winProbData.csv',index=False)


print(win_count_data_frame.to_string(index=False))
print("\n")
print(win_prob_data_frame.to_string(index=False))


sns.barplot(x='Team', y='Win_Probability', data=win_prob_data_frame)
plt.title("Win Probabilities for Teams")
plt.show()