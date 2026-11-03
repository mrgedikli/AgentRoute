
### scale (success %, mean of 5 seeds)

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 33.2 | 46.8 | 49.7 | 51.0 | 52.6 |
| AgentRoute (GNN) | 33.8 | 46.1 | 48.9 | 49.5 | 52.2 |
| Greedy semantic | 34.0 | 47.4 | 50.6 | 50.4 | 51.6 |
| Flooding | 36.3 | 54.5 | 60.1 | 61.3 | 61.5 |
| Central registry | 34.7 | 51.2 | 55.6 | 54.6 | 55.7 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

scale: time ms

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 19.6 | 22.6 | 23.9 | 22.6 | 21.2 |
| AgentRoute (GNN) | 21.3 | 21.5 | 24.1 | 22.6 | 21.0 |
| Greedy semantic | 20.1 | 26.2 | 26.6 | 25.5 | 23.0 |
| Flooding | 20.1 | 25.0 | 35.1 | 51.6 | 52.4 |
| Central registry | 43.3 | 49.4 | 56.0 | 66.3 | 201.7 |
| Chord (exact) | - | - | - | - | - |

scale: hops

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.71 | 2.64 | 3.06 | 2.95 | 2.54 |
| AgentRoute (GNN) | 1.96 | 2.53 | 3.34 | 3.15 | 2.62 |
| Greedy semantic | 1.64 | 2.57 | 3.07 | 3.00 | 2.40 |
| Flooding | 2.02 | 2.75 | 4.12 | 5.05 | 5.25 |
| Central registry | 4.16 | 5.43 | 6.67 | 8.58 | 10.49 |
| Chord (exact) | - | - | - | - | - |

scale: messages / request

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 12 | 17 | 43 | 114 | 315 |
| AgentRoute (GNN) | 12 | 17 | 43 | 115 | 315 |
| Greedy semantic | 12 | 16 | 43 | 114 | 315 |
| Flooding | 61 | 103 | 395 | 827 | 1230 |
| Central registry | 5 | 11 | 33 | 130 | 567 |
| Chord (exact) | 15 | 40 | 242 | 1075 | 4976 |

### mobility (success %, mean of 5 seeds)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 50.2 | 50.3 | 49.7 | 49.0 | 49.6 | 48.7 |
| AgentRoute (GNN) | 50.1 | 50.2 | 48.9 | 48.9 | 49.3 | 48.7 |
| Greedy semantic | 51.6 | 51.7 | 50.6 | 50.0 | 50.5 | 49.4 |
| Flooding | 60.3 | 60.2 | 60.1 | 60.1 | 60.4 | 60.5 |
| Central registry | 56.0 | 56.0 | 55.6 | 55.6 | 55.8 | 55.8 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

mobility: time ms

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 23.4 | 23.7 | 23.9 | 23.3 | 23.4 | 24.1 |
| AgentRoute (GNN) | 24.6 | 24.1 | 24.1 | 22.9 | 23.0 | 23.1 |
| Greedy semantic | 26.7 | 26.5 | 26.6 | 26.8 | 26.4 | 25.8 |
| Flooding | 34.6 | 34.8 | 35.1 | 34.3 | 34.9 | 34.7 |
| Central registry | 55.4 | 55.6 | 56.0 | 55.2 | 55.8 | 55.3 |
| Chord (exact) | - | - | - | - | - | - |

mobility: hops

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 3.07 | 3.03 | 3.06 | 3.00 | 2.96 | 3.12 |
| AgentRoute (GNN) | 3.27 | 3.29 | 3.34 | 3.15 | 3.16 | 3.16 |
| Greedy semantic | 3.14 | 3.13 | 3.07 | 3.13 | 3.04 | 2.88 |
| Flooding | 4.08 | 4.08 | 4.12 | 4.05 | 4.08 | 4.11 |
| Central registry | 6.67 | 6.67 | 6.67 | 6.57 | 6.55 | 6.53 |
| Chord (exact) | - | - | - | - | - | - |

mobility: messages / request

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 28 | 31 | 43 | 65 | 107 | 149 |
| AgentRoute (GNN) | 28 | 31 | 43 | 65 | 107 | 149 |
| Greedy semantic | 28 | 31 | 43 | 64 | 107 | 149 |
| Flooding | 396 | 396 | 395 | 396 | 396 | 396 |
| Central registry | 32 | 32 | 33 | 34 | 36 | 39 |
| Chord (exact) | 235 | 237 | 242 | 252 | 273 | 292 |

### failure (success %, mean of 5 seeds)

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 49.7 | 48.8 | 49.5 | 48.3 | 47.4 |
| AgentRoute (GNN) | 48.9 | 48.4 | 47.9 | 48.3 | 47.3 |
| Greedy semantic | 50.6 | 50.7 | 51.2 | 49.7 | 49.4 |
| Flooding | 60.1 | 60.3 | 60.4 | 59.8 | 59.8 |
| Central registry | 55.6 | 54.9 | 55.7 | 39.0 | 47.4 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

failure: time ms

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 23.9 | 23.0 | 23.5 | 23.9 | 23.0 |
| AgentRoute (GNN) | 24.1 | 23.8 | 23.5 | 24.0 | 23.3 |
| Greedy semantic | 26.6 | 26.8 | 27.0 | 26.8 | 26.5 |
| Flooding | 35.1 | 35.8 | 35.8 | 35.9 | 36.5 |
| Central registry | 56.0 | 55.9 | 55.9 | 55.0 | 57.2 |
| Chord (exact) | - | - | - | - | - |

failure: hops

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 3.06 | 2.93 | 3.13 | 3.00 | 2.88 |
| AgentRoute (GNN) | 3.34 | 3.15 | 3.21 | 3.19 | 2.97 |
| Greedy semantic | 3.07 | 2.98 | 3.06 | 2.94 | 2.81 |
| Flooding | 4.12 | 4.08 | 4.14 | 4.11 | 4.04 |
| Central registry | 6.67 | 6.64 | 6.64 | 6.64 | 6.85 |
| Chord (exact) | - | - | - | - | - |

failure: messages / request

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 43 | 46 | 46 | 52 | 59 |
| AgentRoute (GNN) | 43 | 46 | 46 | 52 | 59 |
| Greedy semantic | 43 | 45 | 45 | 52 | 58 |
| Flooding | 395 | 368 | 348 | 295 | 265 |
| Central registry | 33 | 33 | 33 | 26 | 32 |
| Chord (exact) | 242 | 298 | 292 | 291 | 290 |

### radius (success %, mean of 5 seeds)

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 46.8 | 50.1 | 49.7 | 48.1 | 48.4 | 47.8 |
| AgentRoute (GNN) | 39.2 | 49.7 | 48.9 | 48.7 | 48.3 | 47.8 |
| Greedy semantic | 48.2 | 49.6 | 50.6 | 50.1 | 49.7 | 50.5 |

radius: time ms

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 20.5 | 22.8 | 23.9 | 22.5 | 22.7 | 22.7 |
| AgentRoute (GNN) | 21.6 | 22.4 | 24.1 | 24.7 | 25.5 | 25.5 |
| Greedy semantic | 21.6 | 25.5 | 26.6 | 26.8 | 26.9 | 27.2 |

radius: hops

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 3.41 | 2.79 | 3.06 | 3.34 | 3.54 | 3.63 |
| AgentRoute (GNN) | 2.73 | 3.00 | 3.34 | 3.29 | 3.34 | 3.27 |
| Greedy semantic | 2.88 | 2.75 | 3.07 | 3.07 | 3.19 | 3.24 |

radius: messages / request

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 30 | 38 | 43 | 45 | 46 | 46 |
| AgentRoute (GNN) | 31 | 38 | 43 | 46 | 46 | 46 |
| Greedy semantic | 29 | 38 | 43 | 45 | 45 | 45 |

### load (success %, mean of 5 seeds)

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 48.2 | 49.7 | 48.3 | 47.3 | 43.7 |
| AgentRoute (GNN) | 48.2 | 48.9 | 47.6 | 47.6 | 45.4 |
| Greedy semantic | 51.3 | 50.6 | 47.4 | 47.0 | 47.4 |
| Flooding | 60.0 | 60.1 | 58.5 | 58.6 | 58.6 |
| Central registry | 57.7 | 55.6 | 51.1 | 50.6 | 50.8 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

load: time ms

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 21.8 | 23.9 | 24.3 | 27.9 | 41.6 |
| AgentRoute (GNN) | 22.4 | 24.1 | 26.3 | 30.0 | 41.2 |
| Greedy semantic | 23.0 | 26.6 | 27.2 | 30.4 | 40.3 |
| Flooding | 30.7 | 35.1 | 37.0 | 40.2 | 49.3 |
| Central registry | 46.6 | 56.0 | 58.8 | 66.1 | 89.1 |
| Chord (exact) | - | - | - | - | - |

load: hops

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 3.37 | 3.06 | 3.15 | 3.27 | 2.92 |
| AgentRoute (GNN) | 3.52 | 3.34 | 3.20 | 3.16 | 2.89 |
| Greedy semantic | 3.40 | 3.07 | 2.86 | 2.85 | 2.91 |
| Flooding | 3.99 | 4.12 | 4.08 | 4.10 | 4.14 |
| Central registry | 6.53 | 6.67 | 6.57 | 6.58 | 6.60 |
| Chord (exact) | - | - | - | - | - |

load: messages / request

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 80 | 43 | 25 | 19 | 15 |
| AgentRoute (GNN) | 80 | 43 | 25 | 19 | 15 |
| Greedy semantic | 80 | 43 | 24 | 18 | 15 |
| Flooding | 403 | 395 | 390 | 387 | 386 |
| Central registry | 60 | 33 | 19 | 14 | 12 |
| Chord (exact) | 472 | 242 | 124 | 89 | 70 |

### ablation_summary (success %, mean of 5 seeds)

| method | exact | k=2 | k=4 | k=8 | mean |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 54.7 | 47.2 | 49.7 | 50.9 | 47.9 |
| Greedy semantic | 55.6 | 48.8 | 50.6 | 52.4 | 48.6 |

ablation_summary: time ms

| method | exact | k=2 | k=4 | k=8 | mean |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 21.7 | 22.2 | 23.9 | 23.2 | 21.5 |
| Greedy semantic | 20.5 | 26.0 | 26.6 | 24.6 | 26.7 |

ablation_summary: hops

| method | exact | k=2 | k=4 | k=8 | mean |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.97 | 3.23 | 3.06 | 2.50 | 3.38 |
| Greedy semantic | 1.73 | 2.97 | 3.07 | 2.63 | 3.11 |

ablation_summary: messages / request

| method | exact | k=2 | k=4 | k=8 | mean |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 42 | 44 | 43 | 43 | 44 |
| Greedy semantic | 41 | 43 | 43 | 42 | 43 |

### ablation_header (success %, mean of 5 seeds)

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 25.0 | 49.7 | 50.0 |
| Greedy semantic | 25.1 | 50.6 | 50.8 |

ablation_header: time ms

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 24.0 | 23.9 | 23.5 |
| Greedy semantic | 27.7 | 26.6 | 26.5 |

ablation_header: hops

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 3.44 | 3.06 | 3.07 |
| Greedy semantic | 3.15 | 3.07 | 3.09 |

ablation_header: messages / request

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 48 | 43 | 43 |
| Greedy semantic | 47 | 43 | 43 |
