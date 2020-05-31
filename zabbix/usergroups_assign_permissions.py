#!/usr/bin/env python3
from pyzabbix import ZabbixAPI


# In simple environments, you normally don't have complex access policies. Thus, giving view or edit access for all
# hostgroups (except for templates) to a particular usergroup is fine. That's where the script comes to help.
def main():
    zapi = ZabbixAPI("http://zabbix")
    zapi.login("Admin", "Password")

    # Case-insensitive filter for hostgroups, lets to filter out templates.
    exclude_filter = {'search': {'name': 'template'}, 'excludeSearch': True}

    # Get a list of filtered hostgroup ids (needed to build a rights array).
    hostgroups = [hostgroup['groupid'] for hostgroup in zapi.hostgroup.get(**exclude_filter)]

    # Since we'd rather use usergroup' names instead of their ids, we need to build the respective dict.
    usergroups_mapped = {group['name']: group['usrgrpid'] for group in zapi.usergroup.get()}

    # https://www.zabbix.com/documentation/current/manual/api/reference/usergroup/object#permission
    usergroups_to_update = [{'name': 'VIEW', 'permission': '2'},
                            {'name': 'VIEW&EDIT', 'permission': '3'}]

    for usergroup in usergroups_to_update:
        rights = [{'permission': usergroup['permission'], 'id': id} for id in hostgroups]
        call = {
            'usrgrpid': usergroups_mapped[usergroup['name']],
            'rights': rights
        }
        zapi.usergroup.update(**call)


if __name__ == '__main__':
    main()
