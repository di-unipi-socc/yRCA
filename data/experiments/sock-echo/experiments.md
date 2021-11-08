# Chaos Echo-based experiments

Measure accuracy (amount of returned solutions/explanations) and time performances of three different levels of instrumentation
1. no instrumentation (ids not logged by neither client nor server)
2. instrumented invocations (ids logged only by invokers)
3. instrumented interactions (ids logged by invokers and invokees)

## Howto
Generate logs to be processed by versions 1-3 (same logs, different information considered).
1. varying MBs of logs (higher load per second, higher amount of logs) -> just one service failing, always "shipping" failing
    1. increasing end user load (fixed invoke probability)
        - 1 (1), 10 (0.1), 20 (0.05), 30 (0.033), 40 (0.025), 50 (0.02), 60 (0.0167), 70 (0.0143), 80 (0.0125), 90 (0.0111), 100 (0.01) -> rate (period between requests) 
    2. increasing invoke probability (fixed user load) -> 10 r/s
        - 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
2. varying failing services (small amount of logs, to enable manually checking them)
    1. varying length of failure cascade
        - 1 (edgerouter-frontend), 2 (edgerouter-frontend-orders), 3 (edgerouter-frontend-orders-shipping), 4 (edgerouter-frontend-orders-shipping-rabbitmq)
    2. varying failure probability
        -  1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100