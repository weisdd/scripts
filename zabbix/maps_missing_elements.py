#!/usr/bin/env python3
from pyzabbix import ZabbixAPI


# It helps to find hosts that haven't been added to any of the maps.
def main():
    zapi = ZabbixAPI("http://zabbix")
    zapi.login("Admin", "Password")

    call = {
        "selectSelements": "extend",
    }

    # Here we'll store hosts that are added to at least one map.
    sysmap_hosts = []

    for sysmap in zapi.map.get(**call):
        # Retrieving only elementtype 0, which corresponds to hosts on Zabbix maps.
        sysmap_hosts.extend([element for element in sysmap['selements'] if element['elementtype'] == '0'])

    # Here we'll store a unique set of sysmap hosts, might be useful should we decide to play with sets.
    # As far as I'm concerned, it should always be one hostid per Zabbix host, so it should be a safe assumption.
    sysmap_hosts_ids = {host['elements'][0]['hostid'] for host in sysmap_hosts}

    call = {
        "sortfield": "host"
    }

    # It's time to find what we've missed. :)
    missing_hosts = [host for host in zapi.host.get(**call) if host['hostid'] not in sysmap_hosts_ids]
    for missing_host in missing_hosts:
        print(f"{missing_host['hostid']}: {missing_host['host']}")
    print(f"TOTAL: {len(missing_hosts)}")


if __name__ == '__main__':
    main()
