# Main training loop for parking lot RL agent
from sim.parking_lot import ParkingLot
from sim.car import Car
from sim.metrics import Metrics
from agent.q_learning import QLearningAgent
from agent.policies import random_policy, nearest_policy
import random

EPISODES = 100
CARS_PER_DAY = 30
ROWS, COLS = 5, 10

for policy_name in ['random', 'nearest', 'q_learning']:
    print(f'Policy: {policy_name}')
    rewards = []
    for ep in range(EPISODES):
        lot = ParkingLot(ROWS, COLS)
        metrics = Metrics()
        agent = QLearningAgent(ROWS*COLS) if policy_name == 'q_learning' else None
        cars = []
        time = 0
        for _ in range(CARS_PER_DAY):
            car = Car.random_car(time)
            free_slots = lot.get_free_slots()
            if not free_slots:
                metrics.record_fail()
                continue
            if policy_name == 'random':
                slot = random_policy(free_slots)
            elif policy_name == 'nearest':
                slot = nearest_policy(free_slots)
            else:
                state = tuple([tuple(row) for row in lot.grid])
                slot_idx = agent.choose_action(state, list(range(len(free_slots))))
                slot = free_slots[slot_idx]
            lot.occupy(*slot)
            car.slot = slot
            metrics.record_park(car.wait_time)
            # Simulate car leaving after duration
            leave_time = time + car.parking_duration
            cars.append((leave_time, slot))
            time += random.expovariate(1/3)
            # Free slots for cars whose duration is over
            for leave, s in list(cars):
                if leave <= time:
                    lot.free(*s)
                    cars.remove((leave, s))
        rewards.append(metrics.rewards)
    print(f'Avg reward: {sum(rewards)/len(rewards):.2f}')
