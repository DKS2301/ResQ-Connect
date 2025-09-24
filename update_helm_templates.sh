#!/bin/bash

# Update NLP Service templates
find src/nlp-service/chart/templates -name "*.yaml" -exec sed -i 's/ingest-service/nlp-service/g' {} \;

# Update Graph Service templates  
find src/graph-service/chart/templates -name "*.yaml" -exec sed -i 's/ingest-service/graph-service/g' {} \;
find src/graph-service/chart/templates -name "_helpers.tpl" -exec sed -i 's/ingest-service/graph-service/g' {} \;

# Update Realtime Service templates
find src/realtime-service/chart/templates -name "*.yaml" -exec sed -i 's/ingest-service/realtime-service/g' {} \;
find src/realtime-service/chart/templates -name "_helpers.tpl" -exec sed -i 's/ingest-service/realtime-service/g' {} \;

# Update Analytics Service templates
find src/analytics-service/chart/templates -name "*.yaml" -exec sed -i 's/ingest-service/analytics-service/g' {} \;
find src/analytics-service/chart/templates -name "_helpers.tpl" -exec sed -i 's/ingest-service/analytics-service/g' {} \;

echo "Helm templates updated successfully!"