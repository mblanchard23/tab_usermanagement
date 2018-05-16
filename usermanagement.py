'''Connect to your user management system (e.g. Oracle, Salesforce) here and return group
    assignments'''

import pandas


def get_new_group_assignments():
    '''Return a DataFrame with columns group_name and
    username_upper where every row is a group assignment that needs
    to exist in Tableau, e.g.

    username_upper  | group_name
    -----------------------------
    WADE            | zz_Heat
    KAPONO          | zz_Heat
    RUSSELL         | zz_Celtics
    COUSY           | zz_Celtics
    '''

    df = pandas.DataFrame([['WADE', 'zz_Heat']
                              , ['KAPONO', 'zz_Heat']
                              , ['RUSSELL', 'zz_Celtics']
                              , ['COUSY', 'zz_Celtics']]
                          , columns=['username_upper', 'group_name']
                          )


    return df
