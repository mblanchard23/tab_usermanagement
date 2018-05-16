import sys
from tabapi import tableau_credentials, get_pg_conn, qdf
from usermanagement import get_new_group_assignments


def run_checks():
    # Tableau Server connection
    # Postgres connection

    pg_conn = get_pg_conn()
    if pg_conn.status == 1:
        print('Connection to Postgres... OK')

    creds = tableau_credentials()
    if creds.authenticated:
        print('Connection to Tableau Server OK, logged in as %s' % creds.username)
    c = pg_conn.cursor()
    c.execute("SELECT count(distinct(name)) from _users")
    number_of_users = c.fetchone()[0]
    c.execute("SELECt count(distinct(name)) from _groups where name like 'zz_%'")
    number_of_groups = c.fetchone()[0]
    pg_conn.rollback()
    print('%d users found' % number_of_users)
    print('%d groups found' % number_of_groups)
    df = get_new_group_assignments()

    if not df.empty:
        print('New group assignments found')
    if len(df.columns==2):
        print('Group assignment shape OK')
    if 'username_upper' in df.columns and 'group_name' in df.columns:
        print('Group assignment headers OK')
    else:
        print('Table columns incorrect, make sure "username_upper" and "group_name" is used')