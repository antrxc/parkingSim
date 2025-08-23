# Q-learning agent for parking lot
import random

class QLearningAgent:
    def __init__(self, n_slots, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q = {}  # state-action values
        self.n_slots = n_slots
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_q(self, state, action):
        return self.q.get((state, action), 0.0)

    def choose_action(self, state, available_actions):
        if random.random() < self.epsilon:
            return random.choice(available_actions)
        qs = [self.get_q(state, a) for a in available_actions]
        max_q = max(qs)
        best = [a for a, q in zip(available_actions, qs) if q == max_q]
        return random.choice(best)

    def update(self, state, action, reward, next_state, next_actions):
        max_next = max([self.get_q(next_state, a) for a in next_actions], default=0)
        old = self.get_q(state, action)
        self.q[(state, action)] = old + self.alpha * (reward + self.gamma * max_next - old)
