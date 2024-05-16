# Grafana Dashboards

## Pulling in upstream changes

- Grab an updated [upstream copy](https://github.com/rfmoz/grafana-dashboards/blob/master/prometheus/node-exporter-full.json) of the dashboard
- Save it to `prometheus/upstream-dashboard.json`
- Make a PR and GHA should build and deploy it to staging, after making our modifications to it
- A manual workflow action is provided to further deploy it to prod

## Modifications

We add a number of panels that are useful for our use-case.
The changes needed are captured in `prometheus/process.py` which can be executed to produce the output spec that gets deployed.
