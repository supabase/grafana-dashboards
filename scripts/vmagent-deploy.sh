#! /usr/bin/env bash

set -euo pipefail

ENV="${1}"
TARGET_REGIONS_FILE="${2}"

# will replace our existing dashboards
DASHBOARD_UID=G7Z9GzMGz
DASHBOARD_FILE="./prometheus/vmagent-dashboard.json"

# account for disparity in our monitoring env name and the prefix in project names
if [[ $ENV == "staging" ]]; then
    MONITORING_ENV=dev
else
    MONITORING_ENV="${ENV}"
fi

for region in $(cat "${TARGET_REGIONS_FILE}"); do
    echo ""
    echo "Processing for region: ${region}"
    echo "Current path is: $(pwd)"
    echo "https://monitoring-federated-${region}-${MONITORING_ENV}.supabase.xyz/grafana/api/dashboards/uid/${DASHBOARD_UID}"
    echo "Deleting previous vmagent dashboard"
    echo "-----------------------------------"
    curl -s -XDELETE "https://monitoring-federated-${region}-${MONITORING_ENV}.supabase.xyz/grafana/api/dashboards/uid/${DASHBOARD_UID}" \
         -H 'X-WEBAUTH-USER: automated-user@supabase.io' \
         -H 'Content-Type: application/json' \
         -H "CF-Access-Client-Id: ${GRAFANA_UPLOADER_CF_ID}" \
         -H "CF-Access-Client-Secret: ${GRAFANA_UPLOADER_CF_SECRET}" || true
    echo ""
    echo "Creating new vmgent dashboard"
    echo "-----------------------------"
    curl -sf -XPOST "https://monitoring-federated-${region}-${MONITORING_ENV}.supabase.xyz/grafana/api/dashboards/db" \
         -H 'X-WEBAUTH-USER: automated-user@supabase.io' \
         -H 'Content-Type: application/json' \
         --data-binary "@${DASHBOARD_FILE}" \
         -H "CF-Access-Client-Id: ${GRAFANA_UPLOADER_CF_ID}" \
         -H "CF-Access-Client-Secret: ${GRAFANA_UPLOADER_CF_SECRET}"
done

echo "Complete deployment of the vmagent dashboard to all ${ENV} regions"

