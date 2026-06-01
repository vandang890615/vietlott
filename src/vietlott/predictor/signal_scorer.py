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

class PositionalSignalScorer:
    def __init__(self, df, max_num, slots=3):
        self.df = df
        self.max_num = max_num
        self.slots = slots
        self.total_draws = len(df)

    def get_positional_signals(self):
        """Calculate signals for each slot independently."""
        # signals[slot][num-1]
        freq_matrix = np.zeros((self.slots, self.max_num))
        gap_matrix = np.zeros((self.slots, self.max_num))
        
        # Latest draws for gap calculation
        latest_draws = self.df.sort_values(by="date", ascending=False)
        
        for s in range(self.slots):
            slot_results = []
            for res in self.df['result']:
                if isinstance(res, (list, tuple)) and len(res) > s:
                    slot_results.append(res[s])
            
            if not slot_results: continue
            
            counts = Counter(slot_results)
            for num, count in counts.items():
                if 1 <= num <= self.max_num:
                    freq_matrix[s, num-1] = count / self.total_draws
                    
            for n in range(1, self.max_num + 1):
                found = False
                for i, res in enumerate(latest_draws['result']):
                    if isinstance(res, (list, tuple)) and len(res) > s and int(res[s]) == n:
                        gap_matrix[s, n-1] = i / 50.0  # Faster normalize for high frequency
                        found = True
                        break
                if not found:
                    gap_matrix[s, n-1] = 1.0
                    
        return freq_matrix, gap_matrix

def apply_signals(probs, freq, gap):
    """Refine AI probabilities with statistical signals."""
    # Logic: Favor numbers that are 'Hot' (high freq) and 'Due' (high gap)
    # Using geometric blending for more conservative scoring
    refined = np.power(probs, 0.6) * np.power(freq + 0.01, 0.3) * np.power(gap + 0.01, 0.1)
    return refined / np.sum(refined)

def apply_positional_signals(probs_matrix, freq_m, gap_m):
    """Apply positional logic to a set of probabilities (one per slot)."""
    # probs_matrix: (slots, max_num)
    refined = np.zeros_like(probs_matrix)
    for s in range(probs_matrix.shape[0]):
        refined[s] = apply_signals(probs_matrix[s], freq_m[s], gap_m[s])
    return refined
