# June 2022

## 05-June -> 12-June 2022

Load balancing.

1. upstream directive + proxy_pass
2. default weighted round robin.
3. Methods of load balancing
   1. hash
   2. ip_hash
   3. least_conn
   4. least_time (nginx+)
   5. random (nginx+)

loadbalancing backend server should be

1. idempotent [No internal state]
2. All server connect to same db [Prefereably DB Cluser Setup]
3. If not same db. Use Stick sessions in LB to maintain request to go to same server within session.
4. Looks like we need to design server thinking in terms of LB
5. you cannot take server and stick to LB and make horizontal scaling.
