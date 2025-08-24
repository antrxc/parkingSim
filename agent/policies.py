# Baseline policies for parking lot
import random

def random_policy(free_slots):
    return random.choice(free_slots) if free_slots else None

def nearest_policy(free_slots):
    # Assume nearest is the slot with lowest column (closest to entry)
    return min(free_slots, key=lambda x: x[1]) if free_slots else None

def balanced_policy(free_slots, lot):
    """Try to balance load across rows"""
    if not free_slots:
        return None
    
    # Count cars in each row
    row_counts = {}
    for r in range(lot.rows):
        row_counts[r] = sum(1 for c in range(lot.cols) if not lot.is_free(r, c))
    
    # Find row with least cars
    min_row = min(row_counts, key=row_counts.get)
    
    # Choose slot in that row if available
    row_slots = [slot for slot in free_slots if slot[0] == min_row]
    if row_slots:
        return min(row_slots, key=lambda x: x[1])  # Nearest in that row
    
    return nearest_policy(free_slots)  # Fallback
