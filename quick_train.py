# Quick training script for demonstration
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.dqn import DQNAgent
from agent.environment import ParkingLotEnv
from agent.policies import random_policy, nearest_policy
import numpy as np

def train_quick_demo(episodes=50):
    """Quick training demonstration"""
    print("="*50)
    print("PARKING LOT OPTIMIZER - QUICK TRAINING DEMO")
    print("="*50)
    
    env = ParkingLotEnv(rows=3, cols=5, max_cars_per_episode=15)  # Smaller for speed
    agent = DQNAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_space_size(),
        lr=0.01,  # Higher learning rate for faster demo
        epsilon=0.8,
        epsilon_decay=0.98
    )
    
    print(f"Environment: {env.rows}x{env.cols} parking lot")
    print(f"State size: {env.get_state_size()}, Action size: {env.get_action_space_size()}")
    print(f"Training for {episodes} episodes...\n")
    
    scores = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        
        while True:
            available_actions = env.get_available_actions()
            if not available_actions or env.current_car is None:
                break
                
            action = agent.choose_action(state, available_actions)
            if action is None:
                break
                
            next_state, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        # Train the agent
        agent.train()
        scores.append(total_reward)
        
        # Print progress every 10 episodes
        if episode % 10 == 0 or episode == episodes - 1:
            avg_score = np.mean(scores[-10:]) if len(scores) >= 10 else np.mean(scores)
            print(f"Episode {episode:3d}: Reward={total_reward:6.1f}, "
                  f"Avg10={avg_score:6.1f}, Epsilon={agent.epsilon:.3f}")
    
    # Save trained model
    os.makedirs('models', exist_ok=True)
    agent.save('models/dqn_quick_demo.pth')
    print(f"\nModel saved to models/dqn_quick_demo.pth")
    
    return agent, scores

def compare_policies():
    """Compare different parking policies"""
    print("\n" + "="*50)
    print("POLICY COMPARISON")
    print("="*50)
    
    env = ParkingLotEnv(rows=3, cols=5, max_cars_per_episode=15)
    episodes = 20
    
    policies = {
        'Random': lambda env, state: env.get_available_actions()[np.random.randint(len(env.get_available_actions()))] if env.get_available_actions() else None,
        'Nearest': lambda env, state: min(env.get_available_actions()) if env.get_available_actions() else None,
    }
    
    # Add trained DQN if available
    if os.path.exists('models/dqn_quick_demo.pth'):
        dqn_agent = DQNAgent(env.get_state_size(), env.get_action_space_size())
        dqn_agent.load('models/dqn_quick_demo.pth')
        dqn_agent.epsilon = 0  # No exploration during evaluation
        policies['DQN'] = lambda env, state: dqn_agent.choose_action(state, env.get_available_actions())
    
    results = {}
    
    for policy_name, policy_func in policies.items():
        print(f"\nTesting {policy_name} policy...")
        rewards = []
        occupancies = []
        success_rates = []
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            while True:
                if not env.get_available_actions() or env.current_car is None:
                    break
                
                action = policy_func(env, state)
                if action is None:
                    break
                
                next_state, reward, done, info = env.step(action)
                total_reward += reward
                state = next_state
                
                if done:
                    break
            
            rewards.append(total_reward)
            occupancies.append(info['occupancy'])
            success_rate = info['parked'] / (info['parked'] + info['failed']) if (info['parked'] + info['failed']) > 0 else 0
            success_rates.append(success_rate)
        
        results[policy_name] = {
            'avg_reward': np.mean(rewards),
            'avg_occupancy': np.mean(occupancies),
            'avg_success_rate': np.mean(success_rates)
        }
        
        print(f"  Avg Reward: {results[policy_name]['avg_reward']:.1f}")
        print(f"  Avg Occupancy: {results[policy_name]['avg_occupancy']:.1f}%")
        print(f"  Success Rate: {results[policy_name]['avg_success_rate']:.2f}")
    
    # Print comparison table
    print("\n" + "="*60)
    print("FINAL COMPARISON:")
    print("="*60)
    print(f"{'Policy':<10} {'Reward':<10} {'Occupancy':<12} {'Success Rate':<12}")
    print("-" * 60)
    
    for policy_name, metrics in results.items():
        print(f"{policy_name:<10} {metrics['avg_reward']:<10.1f} "
              f"{metrics['avg_occupancy']:<12.1f}% {metrics['avg_success_rate']:<12.2f}")
    
    return results

if __name__ == '__main__':
    # Quick training demo
    agent, scores = train_quick_demo(episodes=50)
    
    # Compare policies
    results = compare_policies()
    
    print("\n" + "="*50)
    print("TRAINING COMPLETE!")
    print("="*50)
    print("The DQN agent has been trained and compared with baseline policies.")
    print("You can now integrate the trained agent into the simulation!")
    print("\nNext steps:")
    print("1. Run the simulation: python -m sim.game")
    print("2. Add agent selection to the game UI")
    print("3. Train longer with: python train.py")
