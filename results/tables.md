
### scale (success %, mean of 10 seeds)

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 42.1 | 59.2 | 62.9 | 64.9 | 66.5 |
| AgentRoute (GNN) | 42.8 | 59.0 | 63.8 | 65.3 | 66.9 |
| Greedy semantic | 41.7 | 57.7 | 60.4 | 62.8 | 64.3 |
| Load-aware greedy | 41.5 | 57.0 | 59.4 | 61.5 | 63.5 |
| SPFR-style | 42.2 | 60.2 | 64.1 | 66.3 | 68.4 |
| Flooding | 42.2 | 61.0 | 65.4 | 66.9 | 67.1 |
| Central registry | 41.3 | 59.8 | 63.0 | 64.2 | 62.3 |
| Registry (3 replicas) | 41.5 | 59.7 | 64.0 | 64.6 | 63.8 |
| Semantic DHT | 39.6 | 55.1 | 56.0 | 55.0 | 49.6 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

scale: matching ceiling (fraction)

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| AgentRoute (GNN) | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Greedy semantic | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Load-aware greedy | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| SPFR-style | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Flooding | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Central registry | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Registry (3 replicas) | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Semantic DHT | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |
| Chord (exact) | 0.436 | 0.634 | 0.693 | 0.716 | 0.711 |

scale: precision (right / delivered)

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.691 | 0.760 | 0.768 | 0.767 | 0.779 |
| AgentRoute (GNN) | 0.698 | 0.760 | 0.775 | 0.767 | 0.779 |
| Greedy semantic | 0.684 | 0.738 | 0.746 | 0.751 | 0.764 |
| Load-aware greedy | 0.679 | 0.734 | 0.735 | 0.739 | 0.759 |
| SPFR-style | 0.693 | 0.770 | 0.776 | 0.774 | 0.799 |
| Flooding | 0.700 | 0.795 | 0.818 | 0.814 | 0.811 |
| Central registry | 0.700 | 0.794 | 0.812 | 0.820 | 0.808 |
| Registry (3 replicas) | 0.699 | 0.795 | 0.813 | 0.810 | 0.812 |
| Semantic DHT | 0.737 | 0.785 | 0.778 | 0.767 | 0.742 |
| Chord (exact) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

scale: time ms

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 19.0 | 19.7 | 20.6 | 20.1 | 18.0 |
| AgentRoute (GNN) | 20.2 | 21.2 | 21.5 | 20.8 | 18.6 |
| Greedy semantic | 18.1 | 19.4 | 20.7 | 20.0 | 17.9 |
| Load-aware greedy | 17.2 | 18.2 | 19.5 | 18.2 | 16.5 |
| SPFR-style | 17.4 | 19.3 | 21.0 | 20.0 | 19.0 |
| Flooding | 224.4 | 226.7 | 233.9 | 239.4 | 239.9 |
| Central registry | 44.6 | 50.7 | 59.9 | 71.4 | 82.8 |
| Registry (3 replicas) | 43.7 | 46.8 | 57.5 | 65.1 | 74.3 |
| Semantic DHT | 65.1 | 76.7 | 130.5 | 188.9 | 253.5 |
| Chord (exact) | - | - | - | - | - |

scale: hops

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.79 | 1.89 | 2.13 | 2.17 | 1.76 |
| AgentRoute (GNN) | 1.94 | 2.05 | 2.10 | 2.12 | 1.73 |
| Greedy semantic | 1.46 | 1.67 | 2.00 | 1.99 | 1.58 |
| Load-aware greedy | 1.48 | 1.80 | 2.18 | 2.02 | 1.67 |
| SPFR-style | 1.31 | 1.47 | 1.63 | 1.61 | 1.48 |
| Flooding | 1.78 | 2.49 | 4.11 | 5.16 | 5.51 |
| Central registry | 4.27 | 5.54 | 7.30 | 9.87 | 12.17 |
| Registry (3 replicas) | 3.81 | 4.31 | 6.40 | 8.46 | 10.55 |
| Semantic DHT | 1.78 | 2.47 | 4.13 | 5.29 | 6.30 |
| Chord (exact) | - | - | - | - | - |

scale: control kB/s

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 51 | 124 | 485 | 1442 | 4372 |
| AgentRoute (GNN) | 51 | 124 | 485 | 1442 | 4372 |
| Greedy semantic | 51 | 124 | 485 | 1442 | 4372 |
| Load-aware greedy | 51 | 124 | 485 | 1442 | 4372 |
| SPFR-style | 96 | 351 | 1757 | 5497 | 20632 |
| Flooding | 0 | 0 | 0 | 0 | 0 |
| Central registry | 3 | 10 | 43 | 195 | 887 |
| Registry (3 replicas) | 4 | 11 | 52 | 262 | 1242 |
| Semantic DHT | 5 | 19 | 134 | 637 | 2847 |
| Chord (exact) | 5 | 18 | 134 | 629 | 2933 |

scale: query kB / request

| method | 100 | 300 | 1000 | 3000 | 10000 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 3.0 | 2.0 | 1.9 | 1.7 | 1.6 |
| AgentRoute (GNN) | 3.1 | 2.1 | 1.8 | 1.7 | 1.6 |
| Greedy semantic | 2.8 | 1.8 | 1.7 | 1.6 | 1.4 |
| Load-aware greedy | 2.8 | 1.9 | 1.9 | 1.7 | 1.6 |
| SPFR-style | 2.7 | 1.8 | 1.5 | 1.4 | 1.3 |
| Flooding | 26.1 | 45.0 | 173.7 | 369.9 | 545.8 |
| Central registry | 0.7 | 1.0 | 1.2 | 1.7 | 2.2 |
| Registry (3 replicas) | 0.6 | 0.6 | 1.0 | 1.4 | 1.8 |
| Semantic DHT | 4.7 | 6.2 | 12.6 | 18.9 | 24.0 |
| Chord (exact) | 2.4 | 3.1 | 6.1 | 9.3 | 12.0 |

### mobility (success %, mean of 10 seeds)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 63.0 | 62.7 | 62.9 | 62.2 | 63.3 | 63.5 |
| AgentRoute (GNN) | 63.8 | 63.8 | 63.8 | 64.1 | 64.2 | 63.8 |
| Greedy semantic | 60.9 | 60.8 | 60.4 | 60.4 | 60.6 | 60.9 |
| Load-aware greedy | 59.6 | 59.6 | 59.4 | 59.8 | 60.3 | 60.7 |
| SPFR-style | 64.7 | 64.7 | 64.1 | 64.3 | 63.9 | 64.7 |
| Flooding | 65.0 | 65.7 | 65.4 | 64.7 | 64.1 | 65.3 |
| Central registry | 62.5 | 62.8 | 63.0 | 62.9 | 63.3 | 62.8 |
| Registry (3 replicas) | 63.7 | 63.8 | 64.0 | 63.4 | 63.6 | 63.8 |
| Semantic DHT | 56.5 | 56.6 | 56.0 | 57.4 | 56.6 | 56.1 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

mobility: matching ceiling (fraction)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| AgentRoute (GNN) | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Greedy semantic | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Load-aware greedy | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| SPFR-style | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Flooding | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Central registry | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Registry (3 replicas) | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Semantic DHT | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |
| Chord (exact) | 0.694 | 0.694 | 0.693 | 0.693 | 0.694 | 0.694 |

mobility: precision (right / delivered)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.771 | 0.770 | 0.768 | 0.767 | 0.771 | 0.777 |
| AgentRoute (GNN) | 0.771 | 0.774 | 0.775 | 0.773 | 0.776 | 0.781 |
| Greedy semantic | 0.747 | 0.749 | 0.746 | 0.751 | 0.746 | 0.754 |
| Load-aware greedy | 0.735 | 0.736 | 0.735 | 0.737 | 0.743 | 0.747 |
| SPFR-style | 0.780 | 0.779 | 0.776 | 0.780 | 0.777 | 0.784 |
| Flooding | 0.813 | 0.815 | 0.818 | 0.814 | 0.813 | 0.813 |
| Central registry | 0.811 | 0.811 | 0.812 | 0.810 | 0.817 | 0.814 |
| Registry (3 replicas) | 0.811 | 0.813 | 0.813 | 0.811 | 0.813 | 0.813 |
| Semantic DHT | 0.780 | 0.783 | 0.778 | 0.782 | 0.779 | 0.781 |
| Chord (exact) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

mobility: time ms

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 20.6 | 20.5 | 20.6 | 20.8 | 20.4 | 20.7 |
| AgentRoute (GNN) | 21.2 | 21.0 | 21.5 | 21.4 | 21.3 | 21.3 |
| Greedy semantic | 20.5 | 20.7 | 20.7 | 20.5 | 20.4 | 20.7 |
| Load-aware greedy | 19.2 | 19.2 | 19.5 | 19.4 | 19.0 | 19.2 |
| SPFR-style | 21.1 | 21.0 | 21.0 | 21.0 | 20.5 | 20.3 |
| Flooding | 233.9 | 234.3 | 233.9 | 233.8 | 233.1 | 232.9 |
| Central registry | 59.6 | 59.7 | 59.9 | 59.3 | 59.3 | 59.2 |
| Registry (3 replicas) | 56.8 | 56.9 | 57.5 | 56.9 | 55.9 | 55.6 |
| Semantic DHT | 130.6 | 130.9 | 130.5 | 130.4 | 130.8 | 129.6 |
| Chord (exact) | - | - | - | - | - | - |

mobility: hops

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.11 | 2.10 | 2.13 | 2.13 | 2.11 | 2.18 |
| AgentRoute (GNN) | 2.05 | 2.06 | 2.10 | 2.07 | 2.08 | 2.06 |
| Greedy semantic | 2.00 | 2.02 | 2.00 | 1.96 | 1.93 | 1.96 |
| Load-aware greedy | 2.17 | 2.16 | 2.18 | 2.17 | 2.14 | 2.12 |
| SPFR-style | 1.64 | 1.64 | 1.63 | 1.62 | 1.59 | 1.59 |
| Flooding | 4.13 | 4.13 | 4.11 | 4.09 | 4.05 | 4.01 |
| Central registry | 7.33 | 7.33 | 7.30 | 7.23 | 7.16 | 7.07 |
| Registry (3 replicas) | 6.40 | 6.42 | 6.40 | 6.34 | 6.28 | 6.25 |
| Semantic DHT | 4.15 | 4.14 | 4.13 | 4.12 | 4.05 | 4.04 |
| Chord (exact) | - | - | - | - | - | - |

mobility: control kB/s

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 445 | 455 | 485 | 538 | 645 | 747 |
| AgentRoute (GNN) | 445 | 455 | 485 | 538 | 645 | 747 |
| Greedy semantic | 445 | 455 | 485 | 538 | 645 | 747 |
| Load-aware greedy | 445 | 455 | 485 | 538 | 645 | 747 |
| SPFR-style | 1627 | 1657 | 1757 | 1929 | 2288 | 2638 |
| Flooding | 0 | 0 | 0 | 0 | 0 | 0 |
| Central registry | 42 | 43 | 43 | 44 | 45 | 46 |
| Registry (3 replicas) | 50 | 51 | 52 | 54 | 58 | 62 |
| Semantic DHT | 130 | 131 | 134 | 140 | 153 | 164 |
| Chord (exact) | 130 | 131 | 134 | 140 | 152 | 164 |

mobility: query kB / request

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.9 | 1.8 | 1.9 | 1.9 | 1.9 | 1.9 |
| AgentRoute (GNN) | 1.8 | 1.8 | 1.8 | 1.8 | 1.8 | 1.8 |
| Greedy semantic | 1.7 | 1.7 | 1.7 | 1.7 | 1.7 | 1.7 |
| Load-aware greedy | 1.9 | 1.8 | 1.9 | 1.8 | 1.8 | 1.8 |
| SPFR-style | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 |
| Flooding | 173.6 | 174.1 | 173.7 | 174.0 | 173.3 | 173.4 |
| Central registry | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.1 |
| Registry (3 replicas) | 1.0 | 1.0 | 1.0 | 1.0 | 0.9 | 0.9 |
| Semantic DHT | 12.6 | 12.6 | 12.6 | 12.6 | 12.6 | 12.6 |
| Chord (exact) | 6.2 | 6.2 | 6.1 | 6.1 | 6.2 | 6.2 |

### mobility_small (success %, mean of 10 seeds)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 63.0 | 63.5 | 62.8 | 63.9 | 63.8 | 63.8 |
| AgentRoute (GNN) | 63.8 | 64.3 | 63.9 | 63.9 | 64.9 | 64.2 |
| Greedy semantic | 60.9 | 60.9 | 61.2 | 60.2 | 61.9 | 60.4 |
| Load-aware greedy | 59.6 | 60.1 | 60.3 | 60.0 | 60.3 | 60.0 |
| SPFR-style | 64.7 | 64.4 | 64.2 | 64.6 | 64.6 | 65.3 |
| Flooding | 65.0 | 65.2 | 65.5 | 64.5 | 64.1 | 64.4 |
| Central registry | 62.5 | 63.0 | 62.7 | 63.6 | 63.4 | 62.3 |
| Registry (3 replicas) | 63.7 | 63.4 | 63.7 | 63.3 | 63.4 | 62.8 |
| Semantic DHT | 56.5 | 55.7 | 56.4 | 57.4 | 56.2 | 56.1 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

mobility_small: matching ceiling (fraction)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| AgentRoute (GNN) | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Greedy semantic | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Load-aware greedy | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| SPFR-style | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Flooding | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Central registry | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Registry (3 replicas) | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Semantic DHT | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |
| Chord (exact) | 0.694 | 0.693 | 0.693 | 0.695 | 0.694 | 0.694 |

mobility_small: precision (right / delivered)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.771 | 0.773 | 0.774 | 0.782 | 0.785 | 0.783 |
| AgentRoute (GNN) | 0.771 | 0.778 | 0.774 | 0.778 | 0.789 | 0.779 |
| Greedy semantic | 0.747 | 0.752 | 0.755 | 0.751 | 0.760 | 0.747 |
| Load-aware greedy | 0.735 | 0.738 | 0.742 | 0.742 | 0.743 | 0.743 |
| SPFR-style | 0.780 | 0.778 | 0.777 | 0.784 | 0.785 | 0.786 |
| Flooding | 0.813 | 0.816 | 0.815 | 0.815 | 0.812 | 0.817 |
| Central registry | 0.811 | 0.810 | 0.812 | 0.812 | 0.816 | 0.812 |
| Registry (3 replicas) | 0.811 | 0.811 | 0.812 | 0.811 | 0.815 | 0.813 |
| Semantic DHT | 0.780 | 0.778 | 0.776 | 0.787 | 0.778 | 0.774 |
| Chord (exact) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

mobility_small: time ms

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 20.6 | 20.6 | 20.5 | 20.2 | 20.5 | 20.8 |
| AgentRoute (GNN) | 21.2 | 21.6 | 21.6 | 21.5 | 21.7 | 21.9 |
| Greedy semantic | 20.5 | 20.9 | 20.5 | 20.6 | 20.6 | 20.2 |
| Load-aware greedy | 19.2 | 19.3 | 19.2 | 18.8 | 19.0 | 18.9 |
| SPFR-style | 21.1 | 20.7 | 20.7 | 20.2 | 20.0 | 20.1 |
| Flooding | 233.9 | 234.1 | 233.8 | 233.4 | 232.7 | 232.8 |
| Central registry | 59.6 | 60.3 | 59.8 | 59.2 | 58.1 | 58.0 |
| Registry (3 replicas) | 56.8 | 57.1 | 56.7 | 55.8 | 54.7 | 55.0 |
| Semantic DHT | 130.6 | 129.7 | 128.3 | 129.4 | 129.5 | 128.8 |
| Chord (exact) | - | - | - | - | - | - |

mobility_small: hops

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.11 | 2.13 | 2.12 | 2.13 | 2.15 | 2.19 |
| AgentRoute (GNN) | 2.05 | 2.08 | 2.10 | 2.04 | 2.15 | 2.21 |
| Greedy semantic | 2.00 | 2.01 | 1.90 | 1.91 | 1.98 | 1.94 |
| Load-aware greedy | 2.17 | 2.18 | 2.14 | 2.08 | 2.08 | 2.04 |
| SPFR-style | 1.64 | 1.62 | 1.60 | 1.57 | 1.58 | 1.58 |
| Flooding | 4.13 | 4.07 | 4.06 | 4.03 | 3.95 | 3.94 |
| Central registry | 7.33 | 7.29 | 7.20 | 7.07 | 6.89 | 6.93 |
| Registry (3 replicas) | 6.40 | 6.38 | 6.34 | 6.22 | 6.12 | 6.17 |
| Semantic DHT | 4.15 | 4.14 | 4.11 | 4.03 | 3.98 | 3.96 |
| Chord (exact) | - | - | - | - | - | - |

mobility_small: control kB/s

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 445 | 502 | 610 | 780 | 1079 | 1336 |
| AgentRoute (GNN) | 445 | 502 | 610 | 780 | 1079 | 1336 |
| Greedy semantic | 445 | 502 | 610 | 780 | 1079 | 1336 |
| Load-aware greedy | 445 | 502 | 610 | 780 | 1079 | 1336 |
| SPFR-style | 1627 | 1811 | 2170 | 2749 | 3805 | 4713 |
| Flooding | 0 | 0 | 0 | 0 | 0 | 0 |
| Central registry | 42 | 43 | 45 | 47 | 51 | 55 |
| Registry (3 replicas) | 50 | 53 | 57 | 64 | 76 | 87 |
| Semantic DHT | 130 | 136 | 149 | 168 | 204 | 235 |
| Chord (exact) | 130 | 136 | 148 | 167 | 202 | 232 |

mobility_small: query kB / request

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.9 | 1.9 | 1.9 | 1.9 | 1.9 | 1.9 |
| AgentRoute (GNN) | 1.8 | 1.8 | 1.8 | 1.8 | 1.9 | 1.9 |
| Greedy semantic | 1.7 | 1.7 | 1.7 | 1.7 | 1.7 | 1.7 |
| Load-aware greedy | 1.9 | 1.8 | 1.8 | 1.8 | 1.8 | 1.8 |
| SPFR-style | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 | 1.5 |
| Flooding | 173.6 | 174.0 | 174.2 | 174.2 | 174.1 | 174.1 |
| Central registry | 1.2 | 1.2 | 1.2 | 1.1 | 1.1 | 1.1 |
| Registry (3 replicas) | 1.0 | 1.0 | 1.0 | 0.9 | 0.9 | 0.9 |
| Semantic DHT | 12.6 | 12.6 | 12.5 | 12.6 | 12.5 | 12.7 |
| Chord (exact) | 6.2 | 6.2 | 6.1 | 6.2 | 6.2 | 6.2 |

### failure (success %, mean of 10 seeds)

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 62.9 | 62.5 | 62.5 | 62.2 | 60.2 |
| AgentRoute (GNN) | 63.8 | 63.2 | 63.6 | 62.6 | 61.3 |
| Greedy semantic | 60.4 | 60.2 | 60.5 | 60.0 | 58.9 |
| Load-aware greedy | 59.4 | 58.9 | 59.3 | 58.9 | 58.7 |
| SPFR-style | 64.1 | 63.8 | 63.5 | 62.8 | 62.5 |
| Flooding | 65.4 | 64.8 | 65.0 | 65.0 | 63.9 |
| Central registry | 63.0 | 62.2 | 57.2 | 48.0 | 50.7 |
| Registry (3 replicas) | 64.0 | 62.9 | 62.1 | 60.0 | 55.2 |
| Semantic DHT | 56.0 | 55.2 | 54.2 | 55.0 | 54.0 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

failure: matching ceiling (fraction)

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| AgentRoute (GNN) | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Greedy semantic | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Load-aware greedy | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| SPFR-style | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Flooding | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Central registry | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Registry (3 replicas) | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Semantic DHT | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |
| Chord (exact) | 0.693 | 0.691 | 0.692 | 0.695 | 0.691 |

failure: precision (right / delivered)

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.768 | 0.771 | 0.774 | 0.770 | 0.753 |
| AgentRoute (GNN) | 0.775 | 0.774 | 0.778 | 0.771 | 0.763 |
| Greedy semantic | 0.746 | 0.745 | 0.744 | 0.747 | 0.741 |
| Load-aware greedy | 0.735 | 0.732 | 0.736 | 0.734 | 0.736 |
| SPFR-style | 0.776 | 0.775 | 0.776 | 0.772 | 0.773 |
| Flooding | 0.818 | 0.814 | 0.816 | 0.814 | 0.810 |
| Central registry | 0.812 | 0.809 | 0.800 | 0.816 | 0.820 |
| Registry (3 replicas) | 0.813 | 0.810 | 0.811 | 0.810 | 0.819 |
| Semantic DHT | 0.778 | 0.776 | 0.770 | 0.794 | 0.782 |
| Chord (exact) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

failure: time ms

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 20.6 | 20.6 | 20.6 | 20.9 | 20.8 |
| AgentRoute (GNN) | 21.5 | 21.3 | 21.5 | 21.4 | 21.5 |
| Greedy semantic | 20.7 | 21.2 | 20.8 | 21.0 | 21.0 |
| Load-aware greedy | 19.5 | 19.5 | 19.4 | 20.0 | 20.6 |
| SPFR-style | 21.0 | 20.8 | 20.7 | 21.6 | 21.3 |
| Flooding | 233.9 | 234.3 | 234.1 | 233.8 | 234.4 |
| Central registry | 59.9 | 60.0 | 60.2 | 60.1 | 62.8 |
| Registry (3 replicas) | 57.5 | 57.1 | 57.5 | 59.8 | 58.2 |
| Semantic DHT | 130.5 | 130.7 | 130.7 | 132.7 | 137.5 |
| Chord (exact) | - | - | - | - | - |

failure: hops

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.13 | 2.15 | 2.08 | 2.11 | 2.13 |
| AgentRoute (GNN) | 2.10 | 2.06 | 2.09 | 2.12 | 2.12 |
| Greedy semantic | 2.00 | 2.01 | 1.96 | 2.04 | 2.01 |
| Load-aware greedy | 2.18 | 2.20 | 2.18 | 2.27 | 2.33 |
| SPFR-style | 1.63 | 1.63 | 1.63 | 1.70 | 1.69 |
| Flooding | 4.11 | 4.11 | 4.10 | 4.01 | 3.94 |
| Central registry | 7.30 | 7.31 | 7.42 | 7.40 | 7.60 |
| Registry (3 replicas) | 6.40 | 6.53 | 6.51 | 6.88 | 6.63 |
| Semantic DHT | 4.13 | 4.17 | 4.17 | 4.23 | 4.31 |
| Chord (exact) | - | - | - | - | - |

failure: control kB/s

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 485 | 569 | 551 | 505 | 464 |
| AgentRoute (GNN) | 485 | 569 | 551 | 505 | 464 |
| Greedy semantic | 485 | 569 | 551 | 505 | 464 |
| Load-aware greedy | 485 | 569 | 551 | 505 | 464 |
| SPFR-style | 1757 | 2037 | 1948 | 1743 | 1566 |
| Flooding | 0 | 0 | 0 | 0 | 0 |
| Central registry | 43 | 43 | 42 | 40 | 41 |
| Registry (3 replicas) | 52 | 49 | 49 | 46 | 46 |
| Semantic DHT | 134 | 163 | 162 | 157 | 153 |
| Chord (exact) | 134 | 163 | 161 | 153 | 154 |

failure: query kB / request

| method | 0.0 | 0.05 | 0.1 | 0.2 | 0.3 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.9 | 1.9 | 1.8 | 1.8 | 1.9 |
| AgentRoute (GNN) | 1.8 | 1.8 | 1.8 | 1.8 | 1.8 |
| Greedy semantic | 1.7 | 1.8 | 1.7 | 1.7 | 1.7 |
| Load-aware greedy | 1.9 | 1.8 | 1.8 | 1.9 | 1.9 |
| SPFR-style | 1.5 | 1.5 | 1.5 | 1.5 | 1.6 |
| Flooding | 173.7 | 161.3 | 153.7 | 128.5 | 110.9 |
| Central registry | 1.2 | 1.2 | 1.1 | 1.0 | 1.1 |
| Registry (3 replicas) | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| Semantic DHT | 12.6 | 12.4 | 12.3 | 12.0 | 12.3 |
| Chord (exact) | 6.1 | 6.0 | 6.1 | 5.8 | 6.0 |

### radius (success %, mean of 10 seeds)

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 56.7 | 62.9 | 63.3 | 62.8 | 63.4 | 62.4 |
| AgentRoute (GNN) | 54.8 | 63.8 | 62.8 | 63.7 | 62.8 | 62.5 |
| Greedy semantic | 55.8 | 60.4 | 59.8 | 59.0 | 58.4 | 58.4 |
| Load-aware greedy | 56.1 | 59.4 | 58.3 | 58.3 | 58.0 | 58.6 |

radius: matching ceiling (fraction)

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |
| AgentRoute (GNN) | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |
| Greedy semantic | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |
| Load-aware greedy | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |

radius: precision (right / delivered)

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.795 | 0.768 | 0.770 | 0.765 | 0.770 | 0.769 |
| AgentRoute (GNN) | 0.707 | 0.775 | 0.770 | 0.776 | 0.769 | 0.764 |
| Greedy semantic | 0.706 | 0.746 | 0.745 | 0.732 | 0.727 | 0.730 |
| Load-aware greedy | 0.712 | 0.735 | 0.727 | 0.723 | 0.721 | 0.725 |

radius: time ms

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 53.9 | 20.6 | 21.4 | 21.5 | 21.9 | 22.0 |
| AgentRoute (GNN) | 20.8 | 21.5 | 22.3 | 23.0 | 23.1 | 23.0 |
| Greedy semantic | 20.5 | 20.7 | 21.5 | 21.9 | 21.7 | 21.5 |
| Load-aware greedy | 19.9 | 19.5 | 19.4 | 19.7 | 19.9 | 19.7 |

radius: hops

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 6.44 | 2.13 | 2.16 | 2.06 | 2.28 | 2.23 |
| AgentRoute (GNN) | 2.43 | 2.10 | 2.14 | 2.18 | 2.24 | 2.20 |
| Greedy semantic | 2.47 | 2.00 | 2.19 | 2.28 | 2.21 | 2.25 |
| Load-aware greedy | 2.67 | 2.18 | 2.36 | 2.49 | 2.52 | 2.45 |

radius: control kB/s

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 279 | 485 | 487 | 493 | 500 | 506 |
| AgentRoute (GNN) | 279 | 485 | 487 | 493 | 500 | 506 |
| Greedy semantic | 279 | 485 | 487 | 493 | 500 | 506 |
| Load-aware greedy | 279 | 485 | 487 | 493 | 500 | 506 |

radius: query kB / request

| method | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 3.8 | 1.9 | 1.9 | 1.8 | 1.9 | 1.9 |
| AgentRoute (GNN) | 2.0 | 1.8 | 1.9 | 1.9 | 1.9 | 1.9 |
| Greedy semantic | 2.0 | 1.7 | 1.8 | 1.8 | 1.8 | 1.8 |
| Load-aware greedy | 2.0 | 1.9 | 1.9 | 2.0 | 2.0 | 1.9 |

### load (success %, mean of 10 seeds)

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 63.2 | 62.9 | 62.0 | 61.5 | 61.0 |
| AgentRoute (GNN) | 63.9 | 63.8 | 63.0 | 62.1 | 61.3 |
| Greedy semantic | 61.3 | 60.4 | 59.3 | 58.5 | 58.6 |
| Load-aware greedy | 60.4 | 59.4 | 58.9 | 58.3 | 58.3 |
| SPFR-style | 65.6 | 64.1 | 62.7 | 62.1 | 62.6 |
| Flooding | 68.0 | 65.4 | 61.8 | 61.9 | 61.7 |
| Central registry | 66.0 | 63.0 | 57.6 | 57.4 | 56.9 |
| Registry (3 replicas) | 66.3 | 64.0 | 57.9 | 57.6 | 57.8 |
| Semantic DHT | 65.7 | 56.0 | 45.0 | 43.5 | 43.7 |
| Chord (exact) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

load: matching ceiling (fraction)

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| AgentRoute (GNN) | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Greedy semantic | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Load-aware greedy | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| SPFR-style | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Flooding | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Central registry | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Registry (3 replicas) | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Semantic DHT | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |
| Chord (exact) | 0.694 | 0.693 | 0.691 | 0.688 | 0.687 |

load: precision (right / delivered)

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.769 | 0.768 | 0.773 | 0.766 | 0.767 |
| AgentRoute (GNN) | 0.767 | 0.775 | 0.774 | 0.770 | 0.769 |
| Greedy semantic | 0.748 | 0.746 | 0.759 | 0.750 | 0.753 |
| Load-aware greedy | 0.736 | 0.735 | 0.747 | 0.740 | 0.746 |
| SPFR-style | 0.782 | 0.776 | 0.783 | 0.779 | 0.785 |
| Flooding | 0.819 | 0.818 | 0.818 | 0.817 | 0.820 |
| Central registry | 0.814 | 0.812 | 0.814 | 0.812 | 0.809 |
| Registry (3 replicas) | 0.814 | 0.813 | 0.812 | 0.810 | 0.814 |
| Semantic DHT | 0.815 | 0.778 | 0.761 | 0.743 | 0.746 |
| Chord (exact) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

load: time ms

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 18.0 | 20.6 | 21.6 | 23.9 | 31.1 |
| AgentRoute (GNN) | 19.3 | 21.5 | 22.3 | 25.0 | 32.0 |
| Greedy semantic | 17.1 | 20.7 | 22.1 | 24.0 | 30.7 |
| Load-aware greedy | 16.7 | 19.5 | 20.3 | 22.6 | 30.2 |
| SPFR-style | 17.8 | 21.0 | 21.8 | 23.6 | 30.0 |
| Flooding | 228.3 | 233.9 | 235.4 | 238.9 | 250.8 |
| Central registry | 49.0 | 59.9 | 63.1 | 71.3 | 95.5 |
| Registry (3 replicas) | 46.2 | 57.5 | 59.6 | 66.9 | 89.1 |
| Semantic DHT | 93.7 | 130.5 | 138.1 | 159.9 | 233.4 |
| Chord (exact) | - | - | - | - | - |

load: hops

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.10 | 2.13 | 2.08 | 2.06 | 1.95 |
| AgentRoute (GNN) | 2.10 | 2.10 | 2.06 | 2.06 | 1.97 |
| Greedy semantic | 1.96 | 2.00 | 1.93 | 1.90 | 1.88 |
| Load-aware greedy | 2.20 | 2.18 | 2.06 | 2.08 | 2.07 |
| SPFR-style | 1.65 | 1.63 | 1.60 | 1.60 | 1.60 |
| Flooding | 4.16 | 4.11 | 4.02 | 3.99 | 4.03 |
| Central registry | 7.19 | 7.30 | 7.20 | 7.20 | 7.22 |
| Registry (3 replicas) | 6.30 | 6.40 | 6.32 | 6.32 | 6.33 |
| Semantic DHT | 4.14 | 4.13 | 4.09 | 4.03 | 4.03 |
| Chord (exact) | - | - | - | - | - |

load: control kB/s

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 485 | 485 | 485 | 485 | 485 |
| AgentRoute (GNN) | 485 | 485 | 485 | 485 | 485 |
| Greedy semantic | 485 | 485 | 485 | 485 | 485 |
| Load-aware greedy | 485 | 485 | 485 | 485 | 485 |
| SPFR-style | 1757 | 1757 | 1757 | 1757 | 1757 |
| Flooding | 0 | 0 | 0 | 0 | 0 |
| Central registry | 43 | 43 | 43 | 43 | 43 |
| Registry (3 replicas) | 52 | 52 | 52 | 52 | 52 |
| Semantic DHT | 134 | 134 | 134 | 134 | 134 |
| Chord (exact) | 134 | 134 | 134 | 134 | 134 |

load: query kB / request

| method | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.9 | 1.9 | 1.9 | 1.8 | 1.6 |
| AgentRoute (GNN) | 1.8 | 1.8 | 1.8 | 1.8 | 1.7 |
| Greedy semantic | 1.8 | 1.7 | 1.6 | 1.7 | 1.6 |
| Load-aware greedy | 1.9 | 1.9 | 1.8 | 1.8 | 1.8 |
| SPFR-style | 1.6 | 1.5 | 1.5 | 1.5 | 1.5 |
| Flooding | 176.5 | 173.7 | 170.1 | 170.5 | 169.3 |
| Central registry | 1.2 | 1.2 | 1.1 | 1.1 | 1.1 |
| Registry (3 replicas) | 1.0 | 1.0 | 0.9 | 0.9 | 0.9 |
| Semantic DHT | 13.5 | 12.6 | 11.3 | 11.1 | 11.2 |
| Chord (exact) | 6.6 | 6.1 | 5.6 | 5.5 | 5.5 |

### rate (success %, mean of 10 seeds)

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 63.0 | 63.2 | 62.9 | 63.0 | 62.5 | 62.5 |
| Greedy semantic | 59.8 | 61.8 | 60.4 | 59.9 | 60.1 | 60.6 |
| Load-aware greedy | 59.9 | 59.8 | 59.4 | 59.2 | 59.2 | 59.7 |
| SPFR-style | 64.5 | 65.1 | 64.1 | 64.1 | 63.8 | 64.2 |
| Flooding | 64.9 | 66.9 | 65.4 | 65.1 | 64.6 | 64.7 |
| Central registry | 63.3 | 64.4 | 63.0 | 62.4 | 62.1 | 62.4 |
| Registry (3 replicas) | 64.8 | 64.6 | 64.0 | 62.7 | 62.6 | 62.7 |
| Semantic DHT | 56.1 | 57.6 | 56.0 | 56.3 | 55.7 | 55.6 |

rate: matching ceiling (fraction)

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| Greedy semantic | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| Load-aware greedy | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| SPFR-style | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| Flooding | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| Central registry | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| Registry (3 replicas) | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |
| Semantic DHT | 0.699 | 0.708 | 0.693 | 0.688 | 0.684 | 0.686 |

rate: precision (right / delivered)

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.777 | 0.775 | 0.768 | 0.773 | 0.770 | 0.772 |
| Greedy semantic | 0.749 | 0.763 | 0.746 | 0.747 | 0.749 | 0.753 |
| Load-aware greedy | 0.749 | 0.745 | 0.735 | 0.739 | 0.741 | 0.746 |
| SPFR-style | 0.781 | 0.786 | 0.776 | 0.780 | 0.780 | 0.785 |
| Flooding | 0.827 | 0.832 | 0.818 | 0.818 | 0.814 | 0.816 |
| Central registry | 0.824 | 0.822 | 0.812 | 0.812 | 0.810 | 0.812 |
| Registry (3 replicas) | 0.813 | 0.822 | 0.813 | 0.810 | 0.809 | 0.811 |
| Semantic DHT | 0.808 | 0.798 | 0.778 | 0.777 | 0.775 | 0.777 |

rate: time ms

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 21.0 | 20.4 | 20.6 | 20.5 | 20.5 | 20.3 |
| Greedy semantic | 21.7 | 19.8 | 20.7 | 20.5 | 20.4 | 20.5 |
| Load-aware greedy | 20.3 | 19.1 | 19.5 | 18.9 | 19.0 | 19.0 |
| SPFR-style | 20.8 | 20.5 | 21.0 | 20.8 | 20.7 | 20.7 |
| Flooding | 233.1 | 234.3 | 233.9 | 233.7 | 233.7 | 233.7 |
| Central registry | 60.8 | 58.7 | 59.9 | 59.5 | 59.8 | 59.9 |
| Registry (3 replicas) | 55.4 | 55.9 | 57.5 | 56.3 | 56.4 | 56.7 |
| Semantic DHT | 127.1 | 124.4 | 130.5 | 129.6 | 130.1 | 130.4 |

rate: hops

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.20 | 2.14 | 2.13 | 2.12 | 2.12 | 2.10 |
| Greedy semantic | 2.12 | 1.89 | 2.00 | 1.92 | 1.94 | 1.94 |
| Load-aware greedy | 2.19 | 2.24 | 2.18 | 2.07 | 2.11 | 2.10 |
| SPFR-style | 1.66 | 1.65 | 1.63 | 1.61 | 1.62 | 1.61 |
| Flooding | 3.98 | 4.08 | 4.11 | 4.04 | 4.04 | 4.04 |
| Central registry | 6.97 | 7.13 | 7.30 | 7.26 | 7.24 | 7.23 |
| Registry (3 replicas) | 6.03 | 6.23 | 6.40 | 6.35 | 6.33 | 6.32 |
| Semantic DHT | 3.92 | 4.09 | 4.13 | 4.09 | 4.07 | 4.07 |

rate: control kB/s

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 485 | 485 | 485 | 485 | 485 | 485 |
| Greedy semantic | 485 | 485 | 485 | 485 | 485 | 485 |
| Load-aware greedy | 485 | 485 | 485 | 485 | 485 | 485 |
| SPFR-style | 1757 | 1757 | 1757 | 1757 | 1757 | 1757 |
| Flooding | 0 | 0 | 0 | 0 | 0 | 0 |
| Central registry | 43 | 43 | 43 | 43 | 43 | 43 |
| Registry (3 replicas) | 52 | 52 | 52 | 52 | 52 | 52 |
| Semantic DHT | 134 | 134 | 134 | 134 | 134 | 134 |

rate: query kB / request

| method | 1.0 | 3.0 | 10.0 | 30.0 | 100.0 | 300.0 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.9 | 1.9 | 1.9 | 1.9 | 1.9 | 1.9 |
| Greedy semantic | 1.8 | 1.7 | 1.7 | 1.7 | 1.8 | 1.8 |
| Load-aware greedy | 2.0 | 1.9 | 1.9 | 1.9 | 1.9 | 1.9 |
| SPFR-style | 1.6 | 1.5 | 1.5 | 1.6 | 1.6 | 1.6 |
| Flooding | 173.7 | 174.0 | 173.7 | 173.5 | 173.5 | 173.8 |
| Central registry | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 |
| Registry (3 replicas) | 0.9 | 0.9 | 1.0 | 1.0 | 1.0 | 1.0 |
| Semantic DHT | 12.2 | 12.3 | 12.6 | 12.5 | 12.6 | 12.5 |

### tau (success %, mean of 10 seeds)

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 63.8 | 63.7 | 62.9 | 61.4 | 53.1 | 41.9 |
| Greedy semantic | 61.3 | 61.3 | 60.4 | 58.9 | 51.3 | 39.5 |
| Load-aware greedy | 59.0 | 58.8 | 59.4 | 56.7 | 50.2 | 39.1 |
| SPFR-style | 67.2 | 65.9 | 64.1 | 62.1 | 54.1 | 41.8 |
| Flooding | 69.4 | 66.9 | 65.4 | 61.6 | 52.8 | 40.6 |
| Central registry | 67.1 | 65.2 | 63.0 | 59.9 | 51.2 | 40.0 |

tau: matching ceiling (fraction)

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.744 | 0.717 | 0.693 | 0.656 | 0.563 | 0.435 |
| Greedy semantic | 0.744 | 0.717 | 0.693 | 0.656 | 0.563 | 0.435 |
| Load-aware greedy | 0.744 | 0.717 | 0.693 | 0.656 | 0.563 | 0.435 |
| SPFR-style | 0.744 | 0.717 | 0.693 | 0.656 | 0.563 | 0.435 |
| Flooding | 0.744 | 0.717 | 0.693 | 0.656 | 0.563 | 0.435 |
| Central registry | 0.744 | 0.717 | 0.693 | 0.656 | 0.563 | 0.435 |

tau: precision (right / delivered)

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.690 | 0.714 | 0.768 | 0.817 | 0.841 | 0.905 |
| Greedy semantic | 0.659 | 0.687 | 0.746 | 0.800 | 0.844 | 0.900 |
| Load-aware greedy | 0.635 | 0.665 | 0.735 | 0.785 | 0.843 | 0.900 |
| SPFR-style | 0.718 | 0.732 | 0.776 | 0.821 | 0.844 | 0.904 |
| Flooding | 0.772 | 0.767 | 0.818 | 0.843 | 0.853 | 0.903 |
| Central registry | 0.769 | 0.768 | 0.812 | 0.843 | 0.855 | 0.905 |

tau: time ms

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 19.2 | 19.9 | 20.6 | 21.8 | 22.8 | 25.0 |
| Greedy semantic | 19.0 | 20.3 | 20.7 | 22.4 | 24.1 | 26.0 |
| Load-aware greedy | 17.4 | 18.7 | 19.5 | 20.4 | 22.0 | 23.9 |
| SPFR-style | 20.7 | 20.7 | 21.0 | 21.7 | 22.6 | 23.1 |
| Flooding | 234.0 | 233.9 | 233.9 | 234.1 | 234.5 | 234.1 |
| Central registry | 60.1 | 60.1 | 59.9 | 60.2 | 59.9 | 60.1 |

tau: hops

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.88 | 2.01 | 2.13 | 2.34 | 2.50 | 2.89 |
| Greedy semantic | 1.63 | 1.85 | 2.00 | 2.31 | 2.60 | 2.91 |
| Load-aware greedy | 1.66 | 1.96 | 2.18 | 2.43 | 2.79 | 3.13 |
| SPFR-style | 1.57 | 1.60 | 1.63 | 1.76 | 1.86 | 1.95 |
| Flooding | 4.11 | 4.12 | 4.11 | 4.14 | 4.12 | 4.11 |
| Central registry | 7.25 | 7.25 | 7.30 | 7.34 | 7.33 | 7.27 |

tau: control kB/s

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 485 | 485 | 485 | 485 | 485 | 485 |
| Greedy semantic | 485 | 485 | 485 | 485 | 485 | 485 |
| Load-aware greedy | 485 | 485 | 485 | 485 | 485 | 485 |
| SPFR-style | 1757 | 1757 | 1757 | 1757 | 1757 | 1757 |
| Flooding | 0 | 0 | 0 | 0 | 0 | 0 |
| Central registry | 43 | 43 | 43 | 43 | 43 | 43 |

tau: query kB / request

| method | 0.25 | 0.3 | 0.355 | 0.4 | 0.45 | 0.5 |
|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 1.1 | 1.4 | 1.9 | 2.3 | 3.0 | 4.1 |
| Greedy semantic | 0.9 | 1.2 | 1.7 | 2.3 | 3.1 | 4.0 |
| Load-aware greedy | 1.0 | 1.3 | 1.9 | 2.4 | 3.2 | 4.2 |
| SPFR-style | 0.8 | 1.1 | 1.5 | 2.0 | 2.7 | 3.6 |
| Flooding | 176.9 | 175.5 | 173.7 | 172.6 | 171.9 | 170.9 |
| Central registry | 1.2 | 1.2 | 1.2 | 1.2 | 1.1 | 1.1 |

### ablation_summary (success %, mean of 10 seeds)

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 66.3 | 64.7 | 59.2 | 66.2 | 60.6 | 62.9 | 57.5 | 44.6 |
| Greedy semantic | 64.1 | 62.1 | 56.8 | 63.6 | 58.4 | 60.4 | 56.7 | 51.0 |
| Load-aware greedy | 63.4 | 61.4 | 57.2 | 63.1 | 57.3 | 59.4 | 55.9 | 50.1 |

ablation_summary: matching ceiling (fraction)

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |
| Greedy semantic | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |
| Load-aware greedy | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |

ablation_summary: precision (right / delivered)

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 0.800 | 0.790 | 0.730 | 0.802 | 0.746 | 0.768 | 0.756 | 0.651 |
| Greedy semantic | 0.783 | 0.764 | 0.713 | 0.778 | 0.725 | 0.746 | 0.717 | 0.668 |
| Load-aware greedy | 0.774 | 0.755 | 0.719 | 0.768 | 0.718 | 0.735 | 0.706 | 0.664 |

ablation_summary: time ms

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 26.1 | 22.3 | 20.3 | 24.9 | 20.3 | 20.6 | 25.0 | 23.7 |
| Greedy semantic | 23.3 | 21.7 | 20.9 | 22.7 | 20.4 | 20.7 | 24.2 | 27.2 |
| Load-aware greedy | 19.9 | 19.4 | 19.5 | 19.3 | 19.2 | 19.5 | 20.7 | 20.7 |

ablation_summary: hops

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.62 | 2.29 | 2.27 | 2.48 | 2.19 | 2.13 | 3.06 | 3.63 |
| Greedy semantic | 1.98 | 2.01 | 2.22 | 2.07 | 2.07 | 2.00 | 2.46 | 3.11 |
| Load-aware greedy | 1.86 | 1.99 | 2.52 | 1.95 | 2.33 | 2.18 | 2.44 | 3.39 |

ablation_summary: control kB/s

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 1757 | 672 | 344 | 1020 | 390 | 485 | 205 | 34 |
| Greedy semantic | 1757 | 672 | 344 | 1020 | 390 | 485 | 205 | 34 |
| Load-aware greedy | 1757 | 672 | 344 | 1020 | 390 | 485 | 205 | 34 |

ablation_summary: query kB / request

| method | exact | k=16 | k=2 | k=32 | k=4 | k=8 | k=8, no tier | mean |
|---|---|---|---|---|---|---|---|---|
| AgentRoute (DQN) | 2.0 | 1.9 | 2.0 | 1.9 | 1.9 | 1.9 | 2.5 | 3.0 |
| Greedy semantic | 1.7 | 1.7 | 1.8 | 1.7 | 1.8 | 1.7 | 2.0 | 2.3 |
| Load-aware greedy | 1.7 | 1.8 | 2.0 | 1.7 | 1.9 | 1.9 | 2.1 | 2.5 |

### ablation_header (success %, mean of 10 seeds)

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 51.1 | 62.7 | 62.9 |
| Greedy semantic | 49.7 | 60.8 | 60.4 |
| Load-aware greedy | 48.5 | 59.4 | 59.4 |

ablation_header: matching ceiling (fraction)

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 0.557 | 0.692 | 0.693 |
| Greedy semantic | 0.557 | 0.692 | 0.693 |
| Load-aware greedy | 0.557 | 0.692 | 0.693 |

ablation_header: precision (right / delivered)

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 0.835 | 0.769 | 0.768 |
| Greedy semantic | 0.823 | 0.750 | 0.746 |
| Load-aware greedy | 0.818 | 0.735 | 0.735 |

ablation_header: time ms

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 23.8 | 20.6 | 20.6 |
| Greedy semantic | 24.2 | 20.8 | 20.7 |
| Load-aware greedy | 22.2 | 19.5 | 19.5 |

ablation_header: hops

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 2.80 | 2.12 | 2.13 |
| Greedy semantic | 2.72 | 2.04 | 2.00 |
| Load-aware greedy | 3.05 | 2.19 | 2.18 |

ablation_header: control kB/s

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 485 | 485 | 485 |
| Greedy semantic | 485 | 485 | 485 |
| Load-aware greedy | 485 | 485 | 485 |

ablation_header: query kB / request

| method | binary | float32 | int8 |
|---|---|---|---|
| AgentRoute (DQN) | 0.7 | 6.9 | 1.9 |
| Greedy semantic | 0.6 | 6.4 | 1.7 |
| Load-aware greedy | 0.7 | 6.9 | 1.9 |

### ablation_accept (success %, mean of 10 seeds)

| method | best_known | first |
|---|---|---|
| Greedy semantic | 60.4 | 56.3 |
| Load-aware greedy | 59.4 | 55.5 |

ablation_accept: matching ceiling (fraction)

| method | best_known | first |
|---|---|---|
| Greedy semantic | 0.693 | 0.693 |
| Load-aware greedy | 0.693 | 0.693 |

ablation_accept: precision (right / delivered)

| method | best_known | first |
|---|---|---|
| Greedy semantic | 0.746 | 0.698 |
| Load-aware greedy | 0.735 | 0.688 |

ablation_accept: time ms

| method | best_known | first |
|---|---|---|
| Greedy semantic | 20.7 | 20.7 |
| Load-aware greedy | 19.5 | 19.1 |

ablation_accept: hops

| method | best_known | first |
|---|---|---|
| Greedy semantic | 2.00 | 1.92 |
| Load-aware greedy | 2.18 | 2.09 |

ablation_accept: control kB/s

| method | best_known | first |
|---|---|---|
| Greedy semantic | 485 | 485 |
| Load-aware greedy | 485 | 485 |

ablation_accept: query kB / request

| method | best_known | first |
|---|---|---|
| Greedy semantic | 1.7 | 1.7 |
| Load-aware greedy | 1.9 | 1.8 |

### ablation_threshold (success %, mean of 10 seeds)

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 60.5 | 60.5 | 60.4 | 60.4 | 60.2 |

ablation_threshold: matching ceiling (fraction)

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |

ablation_threshold: precision (right / delivered)

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 0.746 | 0.745 | 0.746 | 0.746 | 0.747 |

ablation_threshold: time ms

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 21.0 | 21.0 | 20.7 | 20.9 | 20.8 |

ablation_threshold: hops

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 2.02 | 2.02 | 2.00 | 2.02 | 2.00 |

ablation_threshold: control kB/s

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 529 | 502 | 485 | 477 | 475 |

ablation_threshold: query kB / request

| method | 0.0 | 0.001 | 0.01 | 0.05 | 0.2 |
|---|---|---|---|---|---|
| Greedy semantic | 1.7 | 1.7 | 1.7 | 1.7 | 1.7 |

### ablation_window (success %, mean of 10 seeds)

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 35.9 | 63.4 | 65.8 | 65.4 | 65.3 | 64.7 |

ablation_window: matching ceiling (fraction)

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 | 0.693 |

ablation_window: precision (right / delivered)

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 0.675 | 0.810 | 0.818 | 0.818 | 0.819 | 0.818 |

ablation_window: time ms

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 38.4 | 78.8 | 133.6 | 233.9 | 534.3 | 1034.0 |

ablation_window: hops

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 8.38 | 8.67 | 5.20 | 4.11 | 4.10 | 4.10 |

ablation_window: control kB/s

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 0 | 0 | 0 | 0 | 0 | 0 |

ablation_window: query kB / request

| method | 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|
| Flooding | 173.6 | 173.9 | 174.1 | 173.7 | 173.6 | 173.3 |
