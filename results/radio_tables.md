### radio_compare (mean of 5 seeds, 1,000 agents)


success %

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 49.7 | 39.0 | 48.1 |
| agentroute_gnn | 49.0 | 39.8 | 48.1 |
| greedy | 50.6 | 42.1 | 49.6 |
| flooding | 60.1 | 54.0 | 59.5 |
| registry | 55.6 | 38.5 | 54.0 |
| chord | 0.0 | 0.0 | 0.0 |



time ms

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 23.9 | 22.9 | 23.5 |
| agentroute_gnn | 24.1 | 23.8 | 23.9 |
| greedy | 26.6 | 26.4 | 26.2 |
| flooding | 35.9 | 35.7 | 36.1 |
| registry | 56.0 | 55.5 | 56.1 |
| chord | nan | nan | nan |



hops

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 3.06 | 2.94 | 3.07 |
| agentroute_gnn | 3.34 | 3.26 | 3.33 |
| greedy | 3.07 | 3.04 | 2.99 |
| flooding | 3.95 | 3.91 | 3.94 |
| registry | 6.67 | 6.71 | 6.66 |
| chord | nan | nan | nan |



messages / request

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 43.3 | 42.5 | 43.1 |
| agentroute_gnn | 43.5 | 42.8 | 43.4 |
| greedy | 42.8 | 42.2 | 42.8 |
| flooding | 395.3 | 357.0 | 391.9 |
| registry | 32.9 | 32.1 | 32.8 |
| chord | 242.2 | 240.7 | 242.1 |



drop reasons (% of all requests)

|  | drop_ttl | drop_queue | drop_link | drop_node_down | drop_no_route | drop_wrong_agent | drop_handover | drop_not_found | drop_stale_location | drop_registry_queue |
|---|---|---|---|---|---|---|---|---|---|---|
| ('constant', 'agentroute') | 33.0 | 0.4 | 2.5 | 0.0 | 0.0 | 14.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'agentroute_gnn') | 32.5 | 0.9 | 2.8 | 0.0 | 0.0 | 14.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'chord') | 0.0 | 11.6 | 6.1 | 0.0 | 0.0 | 0.0 | 0.0 | 82.2 | 0.0 | 0.0 |
| ('constant', 'flooding') | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 10.6 | 0.0 | 29.1 | 0.0 | 0.0 |
| ('constant', 'greedy') | 28.3 | 4.4 | 1.9 | 0.0 | 0.0 | 14.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'registry') | 0.0 | 4.0 | 2.7 | 0.0 | 0.0 | 10.2 | 0.0 | 27.5 | 0.0 | 0.0 |
| ('sionna', 'agentroute') | 29.1 | 1.0 | 19.4 | 0.0 | 0.0 | 11.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'agentroute_gnn') | 29.8 | 0.7 | 17.8 | 0.0 | 0.0 | 11.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'chord') | 0.0 | 11.2 | 14.3 | 0.0 | 0.0 | 0.0 | 0.0 | 74.6 | 0.0 | 0.0 |
| ('sionna', 'flooding') | 0.0 | 0.0 | 10.1 | 0.0 | 0.0 | 9.5 | 0.0 | 26.5 | 0.0 | 0.0 |
| ('sionna', 'greedy') | 24.9 | 4.2 | 16.5 | 0.0 | 0.0 | 12.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'registry') | 0.0 | 3.9 | 25.6 | 0.0 | 0.0 | 7.3 | 0.0 | 24.7 | 0.0 | 0.0 |
| ('sionna_plus10db', 'agentroute') | 31.8 | 1.2 | 4.8 | 0.0 | 0.0 | 14.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'agentroute_gnn') | 32.0 | 1.3 | 4.2 | 0.0 | 0.0 | 14.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'chord') | 0.0 | 13.1 | 5.7 | 0.0 | 0.0 | 0.0 | 0.0 | 81.3 | 0.0 | 0.0 |
| ('sionna_plus10db', 'flooding') | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 10.5 | 0.0 | 28.9 | 0.0 | 0.0 |
| ('sionna_plus10db', 'greedy') | 27.8 | 4.0 | 3.2 | 0.0 | 0.0 | 15.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'registry') | 0.0 | 4.5 | 4.9 | 0.0 | 0.0 | 9.2 | 0.0 | 27.4 | 0.0 | 0.0 |



### radio_mobility (success %, Sionna radio)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| agentroute | 40.9 | 39.2 | 39.0 | 39.9 | 40.0 | 39.2 |
| agentroute_gnn | 41.1 | 41.9 | 39.8 | 39.7 | 39.5 | 39.4 |
| greedy | 41.9 | 41.4 | 42.1 | 42.2 | 42.1 | 40.1 |
| flooding | 55.3 | 54.5 | 54.0 | 54.7 | 54.5 | 55.1 |
| registry | 37.8 | 38.7 | 38.5 | 38.6 | 38.6 | 40.4 |
| chord | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

