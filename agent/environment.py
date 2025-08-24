# Environment wrapper for parking lot RL training
import numpy as np
from sim.parking_lot import ParkingLot
from sim.car import Car
from sim.metrics import Metrics
import random

class ParkingLotEnv:
    def __init__(self, rows=5, cols=10, max_cars_per_episode=50):
        self.rows = rows
        self.cols = cols
        self.max_cars_per_episode = max_cars_per_episode
        self.reset()
        
    def reset(self):
        """Reset the environment for a new episode"""
        self.lot = ParkingLot(self.rows, self.cols)
        self.metrics = Metrics()
        self.cars = []
        self.time = 0
        self.cars_processed = 0
        self.current_car = None
        self._spawn_next_car()
        return self.get_state()
        
    def get_state(self):
        """Get current state representation"""
        # Flatten parking lot grid
        lot_state = np.array(self.lot.grid).flatten()
        
        # Add additional features
        occupancy = self.lot.occupancy_percent() / 100.0
        cars_waiting = 1 if self.current_car else 0
        time_normalized = (self.time % 100) / 100.0  # Normalize time
        
        # Combine all features
        state = np.concatenate([
            lot_state,
            [occupancy, cars_waiting, time_normalized]
        ])
        
        return state
        
    def get_action_space_size(self):
        """Get the number of possible actions (parking slots)"""
        return self.rows * self.cols
        
    def get_state_size(self):
        """Get the size of the state vector"""
        return self.rows * self.cols + 3  # grid + additional features
        
    def _spawn_next_car(self):
        """Spawn the next car"""
        if self.cars_processed < self.max_cars_per_episode:
            self.current_car = Car.random_car(self.time, mean_duration=random.randint(5, 20))
            self.cars_processed += 1
        else:
            self.current_car = None
            
    def step(self, action):
        """Take an action in the environment"""
        if self.current_car is None:
            return self.get_state(), 0, True, {}
            
        reward = 0
        done = False
        
        # Convert action to row, col
        row = action // self.cols
        col = action % self.cols
        
        # Check if action is valid (slot is free)
        if self.lot.is_free(row, col):
            # Park the car
            self.lot.occupy(row, col)
            self.current_car.slot = (row, col)
            self.cars.append({
                'car': self.current_car,
                'leave_time': self.time + self.current_car.parking_duration
            })
            
            # Calculate reward
            reward = self._calculate_reward(row, col)
            self.metrics.record_park(0)  # No wait time in training
            
        else:
            # Invalid action (slot occupied)
            reward = -10  # Heavy penalty for invalid action
            self.metrics.record_fail()
            
        # Update time and remove cars that should leave
        self.time += 1
        self._update_cars()
        
        # Spawn next car
        self._spawn_next_car()
        
        # Check if episode is done
        if self.cars_processed >= self.max_cars_per_episode:
            done = True
            
        info = {
            'occupancy': self.lot.occupancy_percent(),
            'parked': self.metrics.parked,
            'failed': self.metrics.failed,
            'total_reward': self.metrics.rewards
        }
        
        return self.get_state(), reward, done, info
        
    def _calculate_reward(self, row, col):
        """Calculate reward for parking a car at given position"""
        base_reward = 10  # Base reward for successful parking
        
        # Distance from entrance (prefer closer spots)
        distance_penalty = col * 0.5
        
        # Load balancing (prefer less crowded rows)
        row_occupancy = sum(1 for c in range(self.cols) if not self.lot.is_free(row, c))
        balance_bonus = (self.cols - row_occupancy) * 0.5
        
        # Efficiency bonus (prefer filling rows completely)
        if row_occupancy == self.cols - 1:  # This parking completes the row
            balance_bonus += 5
            
        total_reward = base_reward - distance_penalty + balance_bonus
        return total_reward
        
    def _update_cars(self):
        """Update cars and remove those whose time is up"""
        cars_to_remove = []
        for car_data in self.cars:
            if car_data['leave_time'] <= self.time:
                # Free the parking slot
                if car_data['car'].slot:
                    self.lot.free(*car_data['car'].slot)
                cars_to_remove.append(car_data)
                
        for car_data in cars_to_remove:
            self.cars.remove(car_data)
            
    def get_available_actions(self):
        """Get list of available actions (free parking slots)"""
        actions = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.lot.is_free(row, col):
                    actions.append(row * self.cols + col)
        return actions
        
    def render(self):
        """Print current state for debugging"""
        print(f"Time: {self.time}, Cars processed: {self.cars_processed}")
        print(f"Occupancy: {self.lot.occupancy_percent():.1f}%")
        print("Parking lot:")
        for row in self.lot.grid:
            print(''.join(['■' if slot else '□' for slot in row]))
        print()
