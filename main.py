from utils.args import parse_args_from_cmdline 
from utils.env import load_environment_variables
from cmd.create_cluster import create_cluster
from cmd.update_cluster import update_cluster
from cmd.start_server import start_server

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
