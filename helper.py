def plot(scores, mean_scores):
    with open('training_log.csv', 'w') as f:
        f.write('game,score,mean_score\n')
        for i, (s, m) in enumerate(zip(scores, mean_scores)):
            f.write(f'{i+1},{s},{m:.2f}\n')