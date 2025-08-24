# Training script for parking lot RL agent
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.dqn import DQNAgent
from agent.environment import ParkingLotEnv
from agent.policies import random_policy, nearest_policy
import numpy as np
import matplotlib.pyplot as plt
import torch

def train_dqn_agent(episodes=1000, update_target_freq=100, save_freq=200):
    """Train DQN agent on parking lot environment"""
    env = ParkingLotEnv()
    agent = DQNAgent(
        state_size=env.get_state_size(),
        action_size=env.get_action_space_size(),
        lr=0.001,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01
    )
    
    scores = []
    occupancies = []
    success_rates = []
    
    print("Starting DQN training...")
    print(f"State size: {env.get_state_size()}, Action size: {env.get_action_space_size()}")
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            available_actions = env.get_available_actions()
            if not available_actions:
                # No available slots, end episode
                break
                
            action = agent.choose_action(state, available_actions)
            if action is None:
                break
                
            next_state, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
                
        # Train the agent
        agent.train()
        
        # Update target network periodically
        if episode % update_target_freq == 0:
            agent.update_target_network()
            
        # Save model periodically
        if episode % save_freq == 0 and episode > 0:
            agent.save(f'models/dqn_parking_episode_{episode}.pth')
            
        # Record metrics
        scores.append(total_reward)
        occupancies.append(info['occupancy'])
        success_rate = info['parked'] / (info['parked'] + info['failed']) if (info['parked'] + info['failed']) > 0 else 0
        success_rates.append(success_rate)
        
        # Print progress
        if episode % 100 == 0:
            avg_score = np.mean(scores[-100:]) if len(scores) >= 100 else np.mean(scores)
            avg_occupancy = np.mean(occupancies[-100:]) if len(occupancies) >= 100 else np.mean(occupancies)
            avg_success = np.mean(success_rates[-100:]) if len(success_rates) >= 100 else np.mean(success_rates)
            print(f"Episode {episode}/{episodes}")
            print(f"  Avg Score: {avg_score:.2f}")
            print(f"  Avg Occupancy: {avg_occupancy:.1f}%")
            print(f"  Avg Success Rate: {avg_success:.2f}")
            print(f"  Epsilon: {agent.epsilon:.3f}")
            print()
    
    # Save final model
    os.makedirs('models', exist_ok=True)
    agent.save('models/dqn_parking_final.pth')
    
    return agent, scores, occupancies, success_rates

def evaluate_policies(episodes=100):
    """Compare different policies"""
    env = ParkingLotEnv()
    
    policies = {
        'Random': random_policy,
        'Nearest': nearest_policy,
        'DQN': None  # Will load trained model
    }
    
    results = {}
    
    # Load trained DQN model if exists
    if os.path.exists('models/dqn_parking_final.pth'):
        dqn_agent = DQNAgent(env.get_state_size(), env.get_action_space_size())
        dqn_agent.load('models/dqn_parking_final.pth')
        dqn_agent.epsilon = 0  # No exploration during evaluation
        policies['DQN'] = dqn_agent
    else:
        print("No trained DQN model found. Skipping DQN evaluation.")
        del policies['DQN']
    
    for policy_name, policy in policies.items():
        print(f"Evaluating {policy_name} policy...")
        
        total_rewards = []
        occupancies = []
        success_rates = []
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            
            while True:
                free_slots = env.lot.get_free_slots()
                if not free_slots:
                    break
                    
                if env.current_car is None:
                    break
                
                if policy_name == 'Random':
                    slot = policy(free_slots)
                elif policy_name == 'Nearest':
                    slot = policy(free_slots)
                elif policy_name == 'DQN':
                    available_actions = env.get_available_actions()
                    if available_actions:
                        action = policy.choose_action(state, available_actions)
                        slot = (action // env.cols, action % env.cols)
                    else:
                        break
                
                if slot and slot in free_slots:
                    action = slot[0] * env.cols + slot[1]
                    next_state, reward, done, info = env.step(action)
                    total_reward += reward
                    state = next_state
                    
                    if done:
                        break
                else:
                    break
            
            total_rewards.append(total_reward)
            occupancies.append(info['occupancy'])
            success_rate = info['parked'] / (info['parked'] + info['failed']) if (info['parked'] + info['failed']) > 0 else 0
            success_rates.append(success_rate)
        
        results[policy_name] = {
            'avg_reward': np.mean(total_rewards),
            'avg_occupancy': np.mean(occupancies),
            'avg_success_rate': np.mean(success_rates)
        }
        
        print(f"  Avg Reward: {results[policy_name]['avg_reward']:.2f}")
        print(f"  Avg Occupancy: {results[policy_name]['avg_occupancy']:.1f}%")
        print(f"  Avg Success Rate: {results[policy_name]['avg_success_rate']:.2f}")
        print()
    
    return results

if __name__ == '__main__':
    # Train DQN agent
    print("="*50)
    print("TRAINING DQN AGENT")
    print("="*50)
    
    agent, scores, occupancies, success_rates = train_dqn_agent(episodes=500)
    
    # Plot training progress
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(scores)
    plt.title('Training Scores')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    
    plt.subplot(1, 3, 2)
    plt.plot(occupancies)
    plt.title('Occupancy Rate')
    plt.xlabel('Episode')
    plt.ylabel('Occupancy %')
    
    plt.subplot(1, 3, 3)
    plt.plot(success_rates)
    plt.title('Success Rate')
    plt.xlabel('Episode')
    plt.ylabel('Success Rate')
    
    plt.tight_layout()
    plt.savefig('training_progress.png')
    plt.show()
    
    # Evaluate policies
    print("="*50)
    print("EVALUATING POLICIES")
    print("="*50)
    
    results = evaluate_policies()
    
    # Print comparison
    print("POLICY COMPARISON:")
    print("-" * 60)
    for policy, metrics in results.items():
        print(f"{policy:>10}: Reward={metrics['avg_reward']:6.2f}, "
              f"Occupancy={metrics['avg_occupancy']:5.1f}%, "
              f"Success={metrics['avg_success_rate']:5.2f}")
