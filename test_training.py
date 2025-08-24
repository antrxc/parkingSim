# Simple training script to test the system
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.dqn import DQNAgent
from agent.environment import ParkingLotEnv

def quick_test():
    """Quick test of the training system"""
    print("Initializing environment...")
    env = ParkingLotEnv(rows=3, cols=5, max_cars_per_episode=20)  # Smaller for testing
    
    print("Initializing DQN agent...")
    agent = DQNAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_space_size(),
        lr=0.001,
        epsilon=0.5  # Start with some exploration
    )
    
    print(f"State size: {env.get_state_size()}")
    print(f"Action size: {env.get_action_space_size()}")
    print()
    
    print("Running test episodes...")
    for episode in range(10):
        state = env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            available_actions = env.get_available_actions()
            if not available_actions or env.current_car is None:
                break
                
            action = agent.choose_action(state, available_actions)
            if action is None:
                break
                
            next_state, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1
            
            state = next_state
            
            if done:
                break
        
        print(f"Episode {episode + 1}: Reward={total_reward:.1f}, Steps={steps}, "
              f"Occupancy={info['occupancy']:.1f}%, Success Rate={info['parked']/(info['parked']+info['failed']):.2f}")
    
    print("\nTest completed successfully!")
    print("You can now run full training with: python train.py")

if __name__ == '__main__':
    quick_test()
