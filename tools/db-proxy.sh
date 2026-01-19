#!/bin/bash

# Cloud SQL Proxy connection script

case "$1" in
  staging)
    echo "Starting proxy for STAGING on port 5435..."
    cloud-sql-proxy coach-ai-vocabulary:asia-east1:coach-vocab-db --port=5435
    ;;
  prod)
    echo "Starting proxy for PRODUCTION on port 5436..."
    cloud-sql-proxy coach-ai-vocabulary:asia-east1:coach-vocab-db-prod --port=5436
    ;;
  *)
    echo "Usage: ./db-proxy.sh [staging|prod]"
    exit 1
    ;;
esac
