# Keycloak

## realm_diff.py

### General information

As updating a keycloak realm might be sometimes challenging (especially, when there are plenty of changes in existing composite roles, and you cannot afford to simply replace the latter due to possibility of pre-existing configuration drift), it's better to let the script tell you which simple roles have been added or deleted, and what change in composite roles it led to.

Note: to make the script simpler, many of the pre-checks that you might have expected to see are missing.

### How to use it

1. Export the old realm to a file named realm-old.json
2. Import the new realm (choose "Skip" for duplicates) and then export the resulting realm to a file named "realm-new.json".
3. Run the script:

```bash
$ chmod +x realm_diff.py && ./realm_diff.py
```
