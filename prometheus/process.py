#! /usr/bin/env python3

import json
from pathlib import Path

DASHBOARD_UID = 'rYdddlXXX'


# so 3 retries here results in (3 * max_attempts) attempts overall
def get_upstream_spec():
    return Path('temp-dashboard-new.json').read_text()


def remove_unused_selectors(spec, env):
    return spec.replace(r'instance=\"$node\",job=\"$job\"', f'Name=\\"{env}-db-$project\\"')


# - wrap in outer model


def update_input_vars(spec):
    """
    updates input variables and returns a json object
    """
    parsed = json.loads(spec)
    tpl_list = parsed['templating']['list']
    processed_list = []
    for var in tpl_list:
        if var['name'] == 'job':
            # remove the 'job' variable as we don't use it
            continue
        if var['name'] == 'node':
            var.update({
                'name': 'project',
                'label': 'Project Ref',
                'query': {
                    'query': 'label_values(node_uname_info, project)',
                    'refId': 'Prometheus-project-ref-Variable-Query'
                },
                'definition': 'label_values(node_uname_info, project)'
            })
        processed_list.append(var)
    parsed['templating']['list'] = processed_list
    return parsed


def find_disk_space_panel(parsed_spec):
    all_panels = parsed_spec["panels"]
    for index, item in enumerate(all_panels):
        if item["title"] == "Disk Space Used Basic":
            break
    else:
        raise ValueError("Did not find Disk Space panel")
    return index


def add_ebs_balance(parsed_spec, env, disk_panel_index):
    disk_panel = parsed_spec["panels"][disk_panel_index]
    disk_panel["title"] = "Disk Space Used, EBS IO Balance"
    disk_panel["targets"].append({
        "datasource": {
            "type": "prometheus",
            "uid": "${datasource}"
        },
        "expr": "".join(['min(aws_ec2_ebsbyte_balance_percent_minimum{Name=\"',
                         env,
                         '-db-$project\"}, aws_ec2_ebsiobalance_percent_minimum{Name=\"',
                         env,
                         '-db-$project\"})']),
        "intervalFactor": 1,
        "legendFormat": "EBS Balance",
        "refId": "ebs",
        "step": 240
    })
    disk_panel["fieldConfig"]["overrides"].append({
        "matcher": {
            "id": "byName",
            "options": "EBS Balance"
        },
        "properties": [
            {
                "id": "custom.fillOpacity",
                "value": 0
            }
        ]
    })
    parsed_spec["panels"][disk_panel_index] = disk_panel
    return parsed_spec


def add_additional_panels(parsed_spec, env, disk_panel_index):
    panels = Path('additional_pg_panels.json').read_text()
    panels = panels.replace("ENV_PLACEHOLDER", env)
    parsed_panels = json.loads(panels)
    insertion_index = disk_panel_index + 1
    for panel in reversed(parsed_panels):
        parsed_spec["panels"].insert(insertion_index, panel)
    # adjust y-position for all panels following the inserted panels
    # the adjustment amount depends on the height of the added panels
    for _, panel in enumerate(parsed_spec["panels"][(insertion_index + len(parsed_panels)):]):
        panel["gridPos"]["y"] += 34
    return parsed_spec


def wrap_dashboard_spec(parsed_spec):
    parsed_spec['uid'] = DASHBOARD_UID
    final_object = {
        'overwrite': True,
        'inputs': [
            {
                'name': 'DS_PROMETHEUS',
                'type': 'datasource',
                'pluginId': 'prometheus',
                'value': 'Prometheus'
            }
        ],
        'folderId': 0,
        'dashboard': parsed_spec
    }
    return final_object


def write_out_dashboard(parsed_spec):
    with open('temp-dashboard-testing.json', 'w') as fl:
        json.dump(parsed_spec, fl, indent=2)
    print("All done writing out new dashboard")


if __name__ == '__main__':
    env = 'staging'
    upstream_dashboard = get_upstream_spec()
    spec = remove_unused_selectors(upstream_dashboard, env)
    spec = update_input_vars(spec)
    disk_panel_index = find_disk_space_panel(spec)
    spec = add_ebs_balance(spec, env, disk_panel_index)
    spec = add_additional_panels(spec, env, disk_panel_index)
    spec = wrap_dashboard_spec(spec)
    write_out_dashboard(spec)
