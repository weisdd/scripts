#!/usr/bin/env python3

import json


def load_roles(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        roles_composite = dict()
        roles_simple = dict()
        realm = json.load(f)
        for role in realm['roles']['realm']:
            if role['composite']:
                roles_composite[role['name']] = role['composites']['realm']
            else:
                roles_simple[role['name']] = role
        return roles_composite, roles_simple


def get_roles_diff(roles1, roles2):
    return sorted(set(roles1) - set(roles2), key=str.lower)


def main():
    roles_composite_old, roles_simple_old = load_roles('realm-old.json')
    roles_composite_new, roles_simple_new = load_roles('realm-new.json')

    differences = [
        {"description": "Legacy non-composite roles (should be deleted)",
         "variables": (roles_simple_old, roles_simple_new)},
        {"description": "New non-composite roles (should be added)",
         "variables": (roles_simple_new, roles_simple_old)}
    ]

    for role in roles_composite_new.keys():
        differences.append({"description": f"Legacy roles in {role} (should be deleted)",
                            "variables": (roles_composite_old[role], roles_composite_new[role])})
        differences.append({"description": f"New roles in {role} (should be added)",
                            "variables": (roles_composite_new[role], roles_composite_old[role])})

    for pair in differences:
        print(f"\033[1m{pair['description']}:\033[0m\n{get_roles_diff(*pair['variables'])}\n")


if __name__ == '__main__':
    main()
