db-exporter-full.json: kps-exporter-full.json
	cp $< $@
	sed -i -e 's/prod-1/prod-db/g' -e 's/KPS Exporter Full/DB Exporter Full/' -e 's/rYdddlP/rYdddlPWk/' $@

kps-exporter-full.json: node-exporter-full.json dashboard.json
	jq '{ dashboard: . }' node-exporter-full.json | jq -s '.[0] * .[1]' dashboard.json - > $@

all: db-exporter-full.json kps-exporter-full.json

.PHONY: all
