## Approach
# Simple approach: Weighed average of past data, taking the last 'x' data points
# for each user, scaling each by an appropriate amount. Simple algorithm seemed
# to accurately capture easily discernable patterns.

# Andrew Apollonsky
import requests
from collections import deque
import numpy as np

host = 'http://order-rate-project.elasticbeanstalk.com'

game = requests.post("%s/games" % host,
                     json={}
).json()

game_id = game["id"]
customer_ids = game["customer_ids"]
n_turns = game["n_turns"]

print("Game id: %d" % game_id)
n_turns_elapsed = 0

# Weigh further-past points less and less. 
n_store_points = 20  # Maximum number of data points to store
forgetting_factor = .95  # Higher number weighs older data more heavily
forgetting_weights = [forgetting_factor ** x for x in range(n_store_points)]
forgetting_weights.reverse()

# Queue used for fast removal of the oldest stored data
cumulative_array = deque()

# Predict 0 first turn
prediction = dict(zip(customer_ids, [0] * len(customer_ids)))
while (n_turns_elapsed < n_turns):
    n_turns_elapsed += 1

    # Send prediction
    turn = requests.post("%s/games/%d/next_turn" % (host, game_id),
                         json={"prediction": prediction}
    ).json()

    new_row = list(turn["actual"].values())
    cumulative_array.append(new_row)
    # If more turns elapsed than maximum stored data length, remove a row.
    if n_turns_elapsed > n_store_points:
        cumulative_array.popleft()

    # Weighed average of past several data points, with more recent values
    # being more heavily weighed
    prediction_values = np.average(np.array(cumulative_array),
                axis=0, weights=forgetting_weights[0:len(cumulative_array)])

    # Simple: Predict the average of past 10 tries
    prediction = dict(zip(turn["actual"].keys(), prediction_values))
    print("Turns elapsed: %d, current score excluding turn 1: %f" %
          (n_turns_elapsed, turn['total_score_excluding_first']))


completed_game = requests.get("%s/games/%d" % (host, game_id)).json()

print("Scores (lower numbers better):")
print("Total, excluding turn 1:    %f" % completed_game['total_score_excluding_first'])
print("Total, excluding turns 1-5: %f" % completed_game['total_score_excluding_first_5'])

print("Score trend (excluding turn 1):")
print(completed_game['scores'][1:])
