# Zabbix

A few examples of how pyzabbix can make your life much easier.

Note: there's no exception handling in the scripts as they were mainly built for educational purposes.

## maps_forgotten_elements.py

It helps to find images that have a {HOST.IP} macros or an IP address in their map labels. - Those that someone planned to convert to hosts, but forgot.

## maps_missing_elements.py

It helps to find hosts that haven't been added to any of the maps.

## usergroups_assign_permissions.py

In simple environments, you normally don't have complex access policies. Thus, giving view or edit access for all hostgroups (except for templates) to a particular usergroup is fine. That's where the script comes to help.
