import os

ts_hostname = os.environ.get('TABLEAU_SERVER_HOSTNAME') # e.g. 'https://mycompany.tableau.com
ts_username = os.environ.get('TABLEAU_SERVER_USERNAME')
ts_password = os.environ.get('TABLEAU_SERVER_PASSWORD')
tableau_api_version = '2.8'
base_url = '{ts_hostname}/api/{tableau_api_version}'.format(
                ts_hostname=ts_hostname
                , tableau_api_version=tableau_api_version)

tabpg_connstring = os.environ.get('tabpg_connstring')


help_text = '''
Setup:
Modify the variables in settings.py or add these environment variables to system:
TABLEAU_SERVER_HOSTNAME - Hostname for your Tableau Server, e.g. https://tableau.mycompany.com
TABLEAU_SERVER_USERNAME - Username for an admin account that can add / subtract from groups in Tableau Server
TABLEAU_USERVER_PASSWORD - Password for an admin account that can add / subtract groups in Tableau Server
tabpg_connstring - pyscopg2 connection string for a readonly account for your Tableau Instance
    This can be a Python str, example
        "host='192.168.1.1' dbname='workgroup' user='admin' password='password' port=8060"
'''


# if not pg_conn_string:
#     tabpg_hostname = os.environ.get('tabpg_hostname')
#     tabpg_dbname = os.environ.get('tabpg_dbname')
#     tabpg_usr = os.environ.get('tabpg_usr')
#     tabpg_pass = os.environ.get('tabpg_pass')
#     tabpg_port = os.environ.get('tabpg_port')
#     pg_conn_string = "host='{host}' dbname='{dbname}' user='{user}' password='{password}' port={port}".format(
#                         host=tabpg_hostname
#                         , dbname=tabpg_dbname
#                         , user=tabpg_usr
#                         , password=tabpg_pass
#                         , port=tabpg_port
#                     )
