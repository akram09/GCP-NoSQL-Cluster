from utils.args import parse_args_from_cmdline 
from utils.env import init
from cmd.create_cluster import create_cluster


def main():
    # init environment 
    init()
    # parse application args  
    arguments = parse_args_from_cmdline()
    if arguments.command == "create":
        create_cluster(arguments)



if __name__ == "__main__": 
    main()
