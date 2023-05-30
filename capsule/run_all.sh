#!/bin/bash

C='\033[0;32m'
NC='\033[0m'

echo -e "${C}EXAMPLES OF FAILURE EXPLANATIONS COMPUTED BY yRCA${NC}"

# Example 1: Orders failing
echo ""
echo -e "${C}==> EXAMPLE 1: FAILURE INJECTED ON SERVICE 'orders'${NC}"
echo -e "${C}(src: https://github.com/di-unipi-socc/yRCA/tree/main/data/examples/sock-echo/orders-fail)${NC}"
echo ""
echo -e "${C}* Case 1.1: Failure directly observed on 'orders'${NC}"
python yrca.py data/examples/sock-echo/orders-fail/event-orders.log data/examples/sock-echo/orders-fail/all.log data/templates/chaos-echo.yml
echo ""
echo -e "${C}* Case 1.2: Failure observed on 'frontend'${NC}"
python yrca.py data/examples/sock-echo/orders-fail/event-frontend.log data/examples/sock-echo/orders-fail/all.log data/templates/chaos-echo.yml
echo ""
echo -e "${C}* Case 1.3: Failure observed on 'edgeRouter'${NC}"
python yrca.py data/examples/sock-echo/orders-fail/event-edgeRouter.log data/examples/sock-echo/orders-fail/all.log data/templates/chaos-echo.yml

# Example 2: Shipping failing
echo ""
echo -e "${C}==> EXAMPLE 2: FAILURE INJECTED ON SERVICE 'shipping'${NC}"
echo -e "${C}(src: https://github.com/di-unipi-socc/yRCA/tree/main/data/examples/sock-echo/shipping-fail)${NC}"
echo ""
echo -e "${C}* Case 2.1: Failure observed on 'edgeRouter'${NC}"
python yrca.py data/examples/sock-echo/shipping-fail/event-edgeRouter.log data/examples/sock-echo/shipping-fail/all.log data/templates/chaos-echo.yml

# Example 3: Users and Shipping both failing
echo ""
echo -e "${C}==> EXAMPLE 3: FAILURE INJECTED ON BOTH 'users' and 'shipping'${NC}"
echo -e "${C}(src: https://github.com/di-unipi-socc/yRCA/tree/main/data/examples/sock-echo/users-shipping-fail)${NC}"
echo ""
echo -e "${C}* Case 3.1: Failure observed on 'edgeRouter'${NC}"
python yrca.py data/examples/sock-echo/users-shipping-fail/event.log data/examples/sock-echo/users-shipping-fail/all.log data/templates/chaos-echo.yml

# Example 4: Timeout cascade
echo ""
echo -e "${C}==> EXAMPLE 4: SERVICE 'shipping' MADE UNREACHABLE${NC}"
echo -e "${C}(src: https://github.com/di-unipi-socc/yRCA/blob/main/data/examples/sock-echo/timeout-cascade)${NC}"
echo ""
echo -e "${C}* Case 4.1: Timeout expiring on 'edgeRouter'${NC}"
python yrca.py data/examples/sock-echo/timeout-cascade/event.log data/examples/sock-echo/timeout-cascade/all.log data/templates/chaos-echo.yml

