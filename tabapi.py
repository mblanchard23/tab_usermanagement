"""Helpers for the Tableau REST API and getting Tableau Server info from Tableau's Postgres DB"""

import sys, requests, json, psycopg2, pandas, datetime
import settings

base_url = settings.base_url


def get_pg_conn():
    try:
        pg_conn = psycopg2.connect(settings.tabpg_connstring)
        return pg_conn
    except:
        print('Unable to connect to Postgres, exiting...')
        sys.exit(0)


def qdf(query, tableau_conn=None):
    if not tableau_conn:
        tableau_conn = get_pg_conn()

    c = tableau_conn.cursor()

    try:
        c.execute(query)

    except Exception as e:
        tableau_conn.rollback()
        print(e)
        return pandas.DataFrame()

    out = c.fetchall()
    df = pandas.DataFrame(out, columns=[x[0] for x in c.description])
    c.close()
    return df


def get_ts_users():
    """Returns DataFrame of Users in Tableau Server and UserIDs"""
    df = qdf("""SELECT _u.name,u.luid as id from users u
							    join _users _u on _u.id=u.id
							     where _u.site_id =1
							""")
    df.name = df.name.apply(lambda x: x.upper())
    return df


def get_ts_groups():
    '''Returns DataFrame of Groups in Tablaeu Server
        and Group IDs'''
    df = qdf("SELECT luid as id,name from groups")
    return df


def get_group_users():
    '''Returns all existing assignments for Tableau Users to their
    respective Tableau Groups. All group names are prefixed "zz_"
    to differentiate from groups not associated with permission sets'''

    df =  qdf("""SELECT g.name as group_name,upper(_u.name) as username from group_users gu
						  join groups g on gu.group_id = g.id
						  join users u on u.id = gu.user_id
						  join _users _u on _u.id = u.id
						  		where g.name like 'zz_%'
						  		""")

    df['username_upper'] = df.username.apply(lambda x: x.upper() if type(x) == str else None)
    return df

class tableau_credentials:
    '''Handles authentication - default credetntials in settings file'''

    def __init__(self, username=settings.ts_username, password=settings.ts_password):
        self.username = username
        self.auth_token, self.site_id, self.user_id, self.request_headers = None, None, None, None
        self.authenticated = False
        self.creds = self.sign_in(username=username
                                  , password=password)
        pass

    def sign_in(self, username, password):
        url = settings.base_url + '/auth/signin'
        payload = {
            "credentials": {
                "name": username,
                "password": password,
                "site": {
                    'contentUrl': ''
                }
            }
        }
        req = requests.post(url
                            , data=json.dumps(payload)
                            , headers={'Content-Type': 'application/json'
                , 'Accept': 'application/json'})

        if req.status_code == 200:
            self.authenticated = True
            response_json = req.json()
            self.auth_token = response_json['credentials']['token']
            self.site_id = response_json['credentials']['site']['id']
            self.user_id = response_json['credentials']['user']['id']
            self.request_headers = {'X-Tableau-Auth': self.auth_token
                , 'Content-Type': 'application/json'
                , 'Accept': 'application/json'}
            return response_json

    def get_request_headers(self):
        if self.authenticated == True:
            return self.request_headers
        else:
            raise Exception('Unable to Authenticate with Tableau Server')


def create_group(group_name, credentials=None):
    if not credentials:
        credentials = tableau_credentials()

    resource = '/sites/{site_id}/groups'.format(site_id=credentials.site_id)
    url = settings.base_url + resource
    payload = {'group': {'name': group_name}}
    req = requests.post(url, headers=credentials.get_request_headers(), data=json.dumps(payload))

    if req.status_code == 409:
        print('Group %s already exists' % group_name)

    if req.status_code == 201:
        print('Group %s successfully created' % group_name)

    return req


def add_uid_to_gid(user_id, group_id, credentials=None):
    if not credentials:
        credentials = tableau_credentials()

    resource = '/sites/{site_id}/groups/{group_id}/users'.format(site_id=credentials.site_id
                                                                 , group_id=group_id)
    url = settings.base_url + resource

    payload = {'user': {'id': user_id}}

    req = requests.post(url
                        , headers=credentials.get_request_headers()
                        , data=json.dumps(payload))

    return req

def remove_uid_from_gid(user_id, group_id, credentials=None):
    if not credentials:
        credentials = tableau_credentials()

    resource = '/sites/{site_id}/groups/{group_id}/users/{user_id}'.format(site_id=credentials.site_id
                                                                           , group_id=group_id
                                                                           , user_id=user_id)

    url = settings.base_url + resource
    req = requests.delete(url, headers=credentials.get_request_headers())
    return req



def add_to_usergroup(username, group_name, tableau_groups=None, tableau_users=None, credentials=None):
    if tableau_groups is None:
        tableau_groups = get_ts_groups()

    if tableau_users is None:
        tableau_users = get_ts_users()

    group_dict = tableau_groups.set_index('name').to_dict()['id']
    user_dict = tableau_users.set_index('name').to_dict()['id']
    group_id = group_dict.get(group_name)
    user_id = user_dict.get(username.upper())

    result_dict = {'operation_type':'add_to_usergroup'
                    ,'username':username
                    ,'group_name':group_name
                    ,'outcome':None
                    ,'status':None}

    if not user_id:
        print('User %s does not exist in Tableau' % username)
        result_dict['status'] = 'User does not exist in Tableau'
        result_dict['outcome'] = 'Failed'
        return result_dict

    if not group_id:
        print('Group %s does not exist in Tableau' % group_name)
        result_dict['status'] = 'Group does not exist in Tableau'
        result_dict['outcome'] = 'Failed'
        return result_dict

    req = add_uid_to_gid(user_id=user_id
                         , group_id=group_id
                         , credentials=credentials)

    if req.status_code in (200, 201):
        print('User %s successfully added to %s' % (username, group_name))
        result_dict['status'] = 'User added to group'
        result_dict['outcome'] = 'Success'
        return result_dict

    if req.status_code == 409:
        print('User %s is already a member of %s!' % (username, group_name))
        result_dict['status'] = 'User added to group'
        result_dict['outcome'] = 'Failed'
        return result_dict

    if req.status_code not in (200, 201, 409):
        print(req.text)
        result_dict['status'] = 'Unknown Error'
        result_dict['outcome'] = 'Failed'
        return result_dict

def remove_from_usergroup(username, group_name, tableau_groups=None, tableau_users=None, credentials=None):
    if tableau_groups is None:
        tableau_groups = get_ts_groups()

    if tableau_users is None:
        tableau_users = get_ts_users()

    group_dict = tableau_groups.set_index('name').to_dict()['id']
    user_dict = tableau_users.set_index('name').to_dict()['id']
    group_id = group_dict.get(group_name)
    user_id = user_dict.get(username.upper())
    result_dict = {'operation_type':'remove_from_usergroup'
                    ,'username':username
                    ,'group_name':group_name
                    ,'outcome':None
                    ,'status':None}

    req = remove_uid_from_gid(user_id=user_id,group_id=group_id,credentials=credentials)

    if req.status_code in (200, 201, 204):
        print('User %s successfully removed from %s' % (username, group_name))
        result_dict['outcome'] = 'Success'
        result_dict['status'] = 'User removed from group'
        return result_dict

    if req.status_code == 409:
        print('User %s is not a member of %s!' % (username, group_name))
        result_dict['outcome'] = 'Failed'
        result_dict['status'] = 'User not a member of group'
        return result_dict

    if req.status_code not in (200, 201, 409):
        print(req.text)
        result_dict['status'] = 'Unknown Error'
        result_dict['outcome'] = 'Failed'
        return result_dict
