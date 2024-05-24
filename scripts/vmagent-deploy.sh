#! /usr/bin/env bash

set -euo pipefail

ENV="${1}"
TARGET_REGIONS_FILE="${2}"

REPO_DIR="$(cd "$(dirname "$0")/.."; pwd)"
cd $REPO_DIR

# will replace our existing dashboards
DASHBOARD_UID=G7Z9GzMGz
DASHBOARD_FILE=vmagent-dashboard.json

# account for disparity in our monitoring env name and the prefix in project names
if [[ $ENV == "staging" ]]; then
    MONITORING_ENV=dev
else
    MONITORING_ENV="${ENV}"
fi

pushd prometheus

for region in $(cat "${TARGET_REGIONS_FILE}"); do
    echo "Processing ${region}"
    echo "https://monitoring-federated-${region}-${MONITORING_ENV}.supabase.xyz/grafana/api/dashboards/uid/${DASHBOARD_UID}"
    curl -XDELETE "https://monitoring-federated-${region}-${MONITORING_ENV}.supabase.xyz/grafana/api/dashboards/uid/${DASHBOARD_UID}" \
         -H 'X-WEBAUTH-USER: automated-user@supabase.io' \
         -H 'Content-Type: application/json' \
         -H "CF-Access-Client-Id: ${GRAFANA_UPLOADER_CF_ID}" \
         -H "CF-Access-Client-Secret: ${GRAFANA_UPLOADER_CF_SECRET}" || true
    curl -sf -XPOST "https://monitoring-federated-${region}-${MONITORING_ENV}.supabase.xyz/grafana/api/dashboards/db" \
         -H 'X-WEBAUTH-USER: automated-user@supabase.io' \
         -H 'Content-Type: application/json' \
         --data-binary "@${DASHBOARD_FILE}" \
         -H "CF-Access-Client-Id: ${GRAFANA_UPLOADER_CF_ID}" \
         -H "CF-Access-Client-Secret: ${GRAFANA_UPLOADER_CF_SECRET}"
done

popd

echo "Complete deployment of the vmagent dashboard to all ${ENV} regions"

