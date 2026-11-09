### radio_compare (mean of 10 seeds, 1,000 agents)


success %

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 62.9 | 52.3 | 62.0 |
| agentroute_gnn | 63.8 | 52.5 | 63.0 |
| greedy | 60.4 | 49.8 | 59.0 |
| greedy_load | 59.4 | 49.2 | 58.5 |
| spfr | 64.1 | 52.9 | 63.6 |
| flooding | 65.4 | 49.3 | 64.0 |
| registry | 63.0 | 44.2 | 60.8 |
| registry3 | 64.0 | 43.2 | 62.1 |
| sdht | 56.0 | 47.8 | 55.4 |
| chord | 0.0 | 0.0 | 0.0 |



time ms

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 20.6 | 20.8 | 20.5 |
| agentroute_gnn | 21.5 | 21.6 | 21.5 |
| greedy | 20.7 | 21.1 | 20.6 |
| greedy_load | 19.5 | 19.7 | 19.4 |
| spfr | 21.0 | 20.8 | 20.8 |
| flooding | 233.9 | 233.6 | 233.6 |
| registry | 59.9 | 60.0 | 59.6 |
| registry3 | 57.5 | 57.3 | 56.6 |
| sdht | 130.5 | 130.3 | 129.8 |
| chord | nan | nan | nan |



hops

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 2.13 | 2.15 | 2.15 |
| agentroute_gnn | 2.1 | 2.1 | 2.09 |
| greedy | 2.0 | 2.04 | 2.01 |
| greedy_load | 2.18 | 2.25 | 2.19 |
| spfr | 1.63 | 1.64 | 1.64 |
| flooding | 4.11 | 4.06 | 4.12 |
| registry | 7.3 | 7.26 | 7.3 |
| registry3 | 6.4 | 6.42 | 6.37 |
| sdht | 4.13 | 4.13 | 4.18 |
| chord | nan | nan | nan |



messages / request

| method | constant | sionna | sionna_plus10db |
|---|---|---|---|
| agentroute | 34.6 | 34.1 | 34.5 |
| agentroute_gnn | 34.4 | 34.1 | 34.4 |
| greedy | 34.2 | 33.9 | 34.2 |
| greedy_load | 34.5 | 34.1 | 34.5 |
| spfr | 54.8 | 54.5 | 54.8 |
| flooding | 462.7 | 413.3 | 460.6 |
| registry | 33.4 | 32.5 | 33.3 |
| registry3 | 60.1 | 59.2 | 60.0 |
| sdht | 261.2 | 257.8 | 261.0 |
| chord | 241.3 | 239.7 | 241.4 |



drop reasons (% of all requests)

|  | drop_ttl | drop_queue | drop_link | drop_node_down | drop_no_route | drop_wrong_agent | drop_handover | drop_not_found | drop_stale_location | drop_registry_queue |
|---|---|---|---|---|---|---|---|---|---|---|
| ('constant', 'agentroute') | 15.3 | 1.1 | 1.7 | 0.0 | 0.0 | 19.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'agentroute_gnn') | 14.0 | 1.2 | 2.5 | 0.0 | 0.0 | 18.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'chord') | 0.0 | 11.3 | 6.6 | 0.0 | 0.0 | 0.0 | 0.0 | 82.1 | 0.0 | 0.0 |
| ('constant', 'flooding') | 0.0 | 2.7 | 1.4 | 0.0 | 0.0 | 14.6 | 0.0 | 15.9 | 0.0 | 0.0 |
| ('constant', 'greedy') | 13.8 | 3.4 | 1.9 | 0.0 | 0.0 | 20.6 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'greedy_load') | 15.8 | 1.6 | 1.8 | 0.0 | 0.0 | 21.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('constant', 'registry') | 0.0 | 5.1 | 3.0 | 0.0 | 0.0 | 14.6 | 0.0 | 14.2 | 0.0 | 0.0 |
| ('constant', 'registry3') | 0.0 | 4.5 | 2.3 | 0.0 | 0.0 | 14.7 | 0.0 | 14.5 | 0.0 | 0.0 |
| ('constant', 'sdht') | 0.0 | 2.3 | 1.3 | 0.0 | 0.0 | 16.0 | 0.0 | 24.3 | 0.0 | 0.0 |
| ('constant', 'spfr') | 12.9 | 2.7 | 1.7 | 0.0 | 0.0 | 18.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'agentroute') | 13.7 | 0.7 | 17.7 | 0.0 | 0.0 | 15.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'agentroute_gnn') | 13.3 | 1.0 | 18.1 | 0.0 | 0.0 | 15.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'chord') | 0.0 | 10.3 | 16.5 | 0.0 | 0.0 | 0.0 | 0.0 | 73.2 | 0.0 | 0.0 |
| ('sionna', 'flooding') | 0.0 | 2.3 | 22.6 | 0.0 | 0.0 | 11.1 | 0.0 | 14.7 | 0.0 | 0.0 |
| ('sionna', 'greedy') | 13.2 | 2.3 | 17.6 | 0.0 | 0.0 | 17.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'greedy_load') | 14.1 | 1.3 | 17.2 | 0.0 | 0.0 | 18.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna', 'registry') | 0.0 | 4.4 | 28.3 | 0.0 | 0.0 | 10.0 | 0.0 | 13.1 | 0.0 | 0.0 |
| ('sionna', 'registry3') | 0.0 | 3.8 | 29.1 | 0.0 | 0.0 | 10.5 | 0.0 | 13.3 | 0.0 | 0.0 |
| ('sionna', 'sdht') | 0.0 | 2.0 | 15.8 | 0.0 | 0.0 | 13.5 | 0.0 | 20.9 | 0.0 | 0.0 |
| ('sionna', 'spfr') | 11.9 | 2.5 | 17.5 | 0.0 | 0.0 | 15.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'agentroute') | 15.3 | 1.1 | 2.9 | 0.0 | 0.0 | 18.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'agentroute_gnn') | 14.2 | 1.6 | 3.2 | 0.0 | 0.0 | 18.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'chord') | 0.0 | 10.6 | 7.2 | 0.0 | 0.0 | 0.0 | 0.0 | 82.3 | 0.0 | 0.0 |
| ('sionna_plus10db', 'flooding') | 0.0 | 2.4 | 3.6 | 0.0 | 0.0 | 14.4 | 0.0 | 15.6 | 0.0 | 0.0 |
| ('sionna_plus10db', 'greedy') | 14.1 | 2.9 | 3.6 | 0.0 | 0.0 | 20.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'greedy_load') | 15.5 | 1.3 | 3.5 | 0.0 | 0.0 | 21.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| ('sionna_plus10db', 'registry') | 0.0 | 5.5 | 5.1 | 0.0 | 0.0 | 14.1 | 0.0 | 14.3 | 0.0 | 0.0 |
| ('sionna_plus10db', 'registry3') | 0.0 | 4.8 | 4.1 | 0.0 | 0.0 | 14.6 | 0.0 | 14.3 | 0.0 | 0.0 |
| ('sionna_plus10db', 'sdht') | 0.0 | 2.2 | 2.7 | 0.0 | 0.0 | 16.1 | 0.0 | 23.6 | 0.0 | 0.0 |
| ('sionna_plus10db', 'spfr') | 12.9 | 2.2 | 3.0 | 0.0 | 0.0 | 18.3 | 0.0 | 0.0 | 0.0 | 0.0 |



### radio_mobility (success %, Sionna radio)

| method | 0.0 | 2.0 | 5.0 | 10.0 | 20.0 | 30.0 |
|---|---|---|---|---|---|---|
| agentroute | 52.8 | 53.5 | 52.3 | 53.1 | 52.8 | 52.4 |
| agentroute_gnn | 52.0 | 53.1 | 52.5 | 52.9 | 53.4 | 52.6 |
| greedy | 50.2 | 50.6 | 49.8 | 51.4 | 51.4 | 50.2 |
| greedy_load | 48.9 | 49.9 | 49.2 | 48.6 | 49.7 | 50.5 |
| spfr | 53.9 | 53.3 | 52.9 | 51.8 | 53.6 | 53.5 |
| flooding | 50.4 | 48.9 | 49.3 | 50.3 | 50.4 | 47.8 |
| registry | 44.4 | 43.0 | 44.2 | 43.4 | 44.3 | 42.9 |
| registry3 | 44.0 | 44.2 | 43.2 | 43.9 | 43.7 | 42.7 |
| sdht | 47.5 | 47.5 | 47.8 | 47.0 | 45.8 | 47.2 |
| chord | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

