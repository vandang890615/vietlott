import numpy as np
import pandas as pd
from collections import Counter

class SignalScorer:
    def __init__(self, df, max_num):
        self.df = df
        self.max_num = max_num
        self.total_draws = len(df)
        
    def get_signals(self):
        """Calculate statistical signals for each number."""
        results = []
        for r in self.df['result']:
            results.extend(r)
            
        counts = Counter(results)
        
        # 1. Frequency Score (Normalized 0-1)
        freq_scores = np.zeros(self.max_num)
        for num, count in counts.items():
            if 1 <= num <= self.max_num:
                freq_scores[num-1] = count / self.total_draws
        
        # 2. Gap Score (How long since last appeared)
        gap_scores = np.zeros(self.max_num)
        latest_draws = self.df.sort_values(by="date", ascending=False)
        
        for n in range(1, self.max_num + 1):
            found = False
            for i, res in enumerate(latest_draws['result']):
                if n in res:
                    gap_scores[n-1] = i / 100 # Normalized scale
                    found = True
                    break
            if not found:
                gap_scores[n-1] = 1.0 # Max gap
                
        # 3. Combine signals into a bias vector
        # Formula: 0.7 * AI_Prob + 0.2 * Freq + 0.1 * Gap
        return freq_scores, gap_scores

def apply_signals(probs, freq, gap):
    """Refine AI probabilities with statistical signals."""
    # Logic: Favor numbers that are 'Hot' (high freq) and 'Due' (high gap)
    refined = probs * 0.7 + freq * 0.2 + gap * 0.1
    return refined / np.sum(refined)
