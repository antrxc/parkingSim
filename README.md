# Parking Lot Optimizer

A simulation and reinforcement learning environment for optimizing parking lot slot assignment, built with Pygame and Python.

## Features
- Visual 2D parking lot simulation (Pygame)
- Animated cars that follow roads and park in slots
- Multiple slot assignment policies (random, nearest, RL agent)
- Real-time metrics: occupancy, wait time, reward, etc.
- Modular code for easy extension (multi-floor, car sizes, premium slots)

## Getting Started

### Requirements
- Python 3.8+
- pygame

### Setup
1. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install pygame
   ```

### Run the Simulation
From the project root:
```bash
python -m sim.game
```

### Project Structure
- `sim/` — Simulation logic, visualization, and metrics
- `agent/` — RL agent and baseline policies
- `train.py` — Training and evaluation script

## Roadmap
- [x] Animated parking lot with moving cars
- [x] Baseline policies (random, nearest)
- [ ] RL agent integration (Q-learning, DQN)
- [ ] Streamlit dashboard for performance
- [ ] Multi-floor, car sizes, premium slots

## License
MIT
