#!/bin/bash

# Script to update all retail store references to ResQConnect

echo "Updating retail store references to ResQConnect..."

# Update Go files in request-service
find /data30/deepak/Projects/Microservice/ResQConnect/src/request-service -name "*.go" -exec sed -i 's/retail-store-catalog/resqconnect-request-service/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect/src/request-service -name "*.go" -exec sed -i 's/retail_store_catalog/resqconnect_request_service/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect/src/request-service -name "*.go" -exec sed -i 's/catalog/request/g' {} \;

# Update Java files in matching-service
find /data30/deepak/Projects/Microservice/ResQConnect/src/matching-service -name "*.java" -exec sed -i 's/com\.amazon\.sample\.orders/com.resqconnect.matching/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect/src/matching-service -name "*.java" -exec sed -i 's/orders/matching/g' {} \;

# Update Java files in volunteer-service
find /data30/deepak/Projects/Microservice/ResQConnect/src/volunteer-service -name "*.java" -exec sed -i 's/com\.amazon\.sample\.carts/com.resqconnect.volunteer/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect/src/volunteer-service -name "*.java" -exec sed -i 's/carts/volunteers/g' {} \;

# Update Java files in coordinator-ui
find /data30/deepak/Projects/Microservice/ResQConnect/src/coordinator-ui -name "*.java" -exec sed -i 's/com\.amazon\.sample\.ui/com.resqconnect.ui/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect/src/coordinator-ui -name "*.java" -exec sed -i 's/retail-store/resqconnect/g' {} \;

# Update application.yml files
find /data30/deepak/Projects/Microservice/ResQConnect -name "application.yml" -exec sed -i 's/retail-store/resqconnect/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect -name "application.yml" -exec sed -i 's/orders/matching/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect -name "application.yml" -exec sed -i 's/catalog/request/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect -name "application.yml" -exec sed -i 's/carts/volunteers/g' {} \;

# Update JSON metadata files
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.json" -exec sed -i 's/retail-store/resqconnect/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.json" -exec sed -i 's/orders/matching/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.json" -exec sed -i 's/catalog/request/g' {} \;
find /data30/deepak/Projects/Microservice/ResQConnect -name "*.json" -exec sed -i 's/carts/volunteers/g' {} \;

# Update Istio gateway and virtual service files
find /data30/deepak/Projects/Microservice/ResQConnect -name "istio-*.yml" -exec sed -i 's/retail-store/resqconnect/g' {} \;

echo "Completed updating retail store references!"
