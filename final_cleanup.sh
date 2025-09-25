#!/bin/bash

# Final cleanup of remaining retail references
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.yaml" -o -name "*.yml" | xargs sed -i 's/retail-store-ui/resqconnect-coordinator-ui/g'
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.yaml" -o -name "*.yml" | xargs sed -i 's/retail-store-catalog/resqconnect-request-service/g'
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.yaml" -o -name "*.yml" | xargs sed -i 's/retail-store-cart/resqconnect-volunteer-service/g'
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.yaml" -o -name "*.yml" | xargs sed -i 's/retail-store-checkout/resqconnect-notification-service/g'
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.yaml" -o -name "*.yml" | xargs sed -i 's/retail-store-orders/resqconnect-matching-service/g'

echo "Final cleanup completed!"
