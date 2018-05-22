import datetime, pandas
from tabapi import tableau_credentials, add_to_usergroup, remove_from_usergroup, get_ts_users, get_ts_groups, \
    get_group_users
from settings import help_text
from usermanagement import get_new_group_assignments

creds = tableau_credentials()
tableau_users = get_ts_users()
tableau_groups = get_ts_groups()
existing_group_users = None
new_group_assignments = None


def help():
    print(help_text)


def add_user_to_group(username, group_name):
    return add_to_usergroup(username=username
                            , group_name=group_name
                            , tableau_groups=tableau_groups
                            , tableau_users=tableau_users
                            , credentials=creds)


def remove_user_from_group(username, group_name):
    return remove_from_usergroup(username=username
                                 , group_name=group_name
                                 , tableau_groups=tableau_groups
                                 , tableau_users=tableau_users
                                 , credentials=creds)


def update_group_assigments(existing_group_users=None, new_group_assignments=None, groups=tableau_groups,
                            users=tableau_users):
    '''Combines list of existing group assignments with an updated list and iteratively creates the assignments
    that are missing'''
    if existing_group_users is None:
        existing_group_users = get_group_users()

    if new_group_assignments is None:
        new_group_assignments = get_new_group_assignments()

    """Filters out any users that exist in your HR environment but not in Tableau"""

    user_exists = new_group_assignments.username_upper.apply(
        lambda x: True if x in users.name.values.tolist() else False)

    """Joins the existing list of Group Users to the fresh assignments"""

    merged = pandas.merge(new_group_assignments[user_exists], existing_group_users, how='outer',
                          left_on=['group_name', 'username_upper']
                          , right_on=['group_name', 'username_upper']
                          , suffixes=('_x', '_y'))

    merged['username_upper_x'] = merged.username_x.apply(lambda x: x.upper() if pandas.notnull(x) else None)
    merged['username_upper_y'] = merged.username_y.apply(lambda x: x.upper() if pandas.notnull(x) else None)

    relationships_to_add = pandas.isnull(merged.username_upper_y)
    relationships_to_remove = pandas.isnull(merged.username_upper_x)

    a = datetime.datetime.now()

    merged['username'] = merged.apply(
        lambda x: x['username_upper_x'] if pandas.notnull(x['username_upper_x']) else x['username_upper_y'], axis=1)

    '''Add new group assignements new_group_assignments'''
    print('\nTotal assigments to create: %d\n' % merged[pandas.isnull(merged.username_y)].__len__())
    outcomes = []
    add_counter = 0
    for u in merged[relationships_to_add][['username', 'group_name']].to_dict(orient='records'):
        add_counter += 1
        outcomes.append(add_user_to_group(**u))
        if add_counter % 200 == 0:
            print('Record number: %d' % add_counter)
            print('Runtime: %d' % (datetime.datetime.now() - a).total_seconds())

    rem_counter = 0
    for u in merged[relationships_to_remove][['username', 'group_name']].to_dict(orient='records'):
        rem_counter += 1
        outcomes.append(remove_user_from_group(**u))
        if rem_counter % 200 == 0:
            print('Record number: %d' % add_counter)
            print('Runtime: %d' % (datetime.datetime.now() - a).total_seconds())

    b = datetime.datetime.now()

    '''TODO: Need to subtract users who've assignemnts have been deleted'''
    total_runtime = (b - a).total_seconds()
    print('Total runtime: %d seconds' % total_runtime)

    '''TODO: Logging
        Log of groups we attempt to create that do not exist on server
        Log of users added / removed
        Runtimes'''

    return {'log': {'total_runtime': total_runtime
        , 'job_start': a.strftime('%Y-%m-%d %H:%M:%S')
        , 'job_end': b.strftime('%Y-%m-%d %H:%M:%S')
        , 'users_added': add_counter
        , 'users_removed': rem_counter
        , 'outcomes': outcomes
                    }
            }
