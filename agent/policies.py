# Baseline policies for parking lot
import random

def random_policy(free_slots):
    return random.choice(free_slots) if free_slots else None

def nearest_policy(free_slots):
    # Assume nearest is the slot with lowest column (closest to entry)
    return min(free_slots, key=lambda x: x[1]) if free_slots else None
