"""Couchbase cluster manager

This script allows to perform basic operations to manage the lifecycle of a Couchbase cluster on the Google Cloud Platform.

The script can be used to create a new cluster, update an existing one or start a web server to manage the cluster. 

This script requires the following environment variables to be set:
    SERVICE_ACCOUNT_OAUTH_TOKEN: the oauth token of the service account used to perform operations on the Google Cloud Platform. This token can also be updated using the server's REST API 
    COUCHBASE_USER: the username of the Couchbase administrator.
    COUCHBASE_PASSWORD: the password of the Couchbase administrator.

Usage:
    python main.py [command] [options]

Commands:
    create: create a new Couchbase cluster on the Google Cloud Platform. 
    update: update an existing Couchbase cluster on the Google Cloud Platform.
    server: start a web server to manage the Couchbase cluster.
"""



from utils.args import parse_args_from_cmdline 
from utils.env import load_environment_variables
from cmd.create_cmd import create_cluster
from cmd.update_cmd import update_cluster
from cmd.server_cmd import start_server

def main():
    # init environment 
    load_environment_variables()
    # parse application args  
    arguments = parse_args_from_cmdline()
    if arguments.command == "create":
        create_cluster(arguments)
    elif arguments.command == "update":
        update_cluster(arguments)
    elif arguments.command == "server":
        start_server(arguments)

        



if __name__ == "__main__": 
    main()
