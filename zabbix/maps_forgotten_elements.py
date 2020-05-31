#!/usr/bin/env python3
import re
from pyzabbix import ZabbixAPI


# It helps to find images that have a {HOST.IP} macros or an IP address in their map labels.
# - Those that someone planned to convert to hosts, but forgot.
def main():
    zapi = ZabbixAPI("http://zabbix")
    zapi.login("Admin", "Password")

    call = {
        "selectSelements": "extend",
        "sortfield": "name"
    }

    # Simplified regexp for IPv4 addresses
    ip_regexp = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    for sysmap in zapi.map.get(**call):
        print(f"{'*' * 30} {sysmap['name']} (sysmapid: {sysmap['sysmapid']}) {'*' * 30}")

        # Retrieving only elementtype 4, which corresponds to images on Zabbix maps
        images = [element for element in sysmap['selements'] if element['elementtype'] == '4']

        # We're looking for elements with a macros {HOST.IP} (which will not be expanded for images)
        # and/or IP addresses in their labels
        forgotten_elements = [image for image in images if
                              '{HOST.IP}' in image['label'] or ip_regexp.search(image['label'])]
        if forgotten_elements:
            print(*forgotten_elements, sep='\n')

        print(f'TOTAL: {len(forgotten_elements)}\n')


if __name__ == '__main__':
    main()
