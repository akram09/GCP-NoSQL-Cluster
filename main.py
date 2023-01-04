import os, uuid
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_cluster_args, create_template_from_args, create_template_from_yaml
from lib.managed_instance import create_managed_instance_group
from lib.template import list_instance_templates, delete_instance_template, get_instance_template
from lib.firewall import create_firewall_rule, check_firewall_rule
from lib.vm_instance import create_instance_from_template, delete_instance

if __name__ == "__main__":
    # parse arguments
    args = parse_cluster_args()

    # load environment variables
    load_dotenv()
    # check environment variables 
    check_env()

    # get project id
    project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
    # get zone
    zone = os.environ["GOOGLE_CLOUD_ZONE"]


    # parse arguments
    args = parse_cluster_args()

    #Create instance templace
    template_name = f"template-{uuid.uuid4()}"

    #delete_all_templates(project_id);exit()
    # test if args has attribute yaml_file
    if args.yaml_file != None:
        template = create_template_from_yaml(project_id, zone, template_name, args.yaml_file)
    else:
        # test if cluster_name and cluster_size are defined in args
        if args.cluster_name == None:
            raise Exception("cluster_name is not defined in the args")  
        if args.cluster_size == None:
            raise Exception("cluster_size is not defined in the args")
        if args.bucket == None:
            raise Exception("bucket is not defined in the args")

        template = create_template_from_args(project_id, zone, template_name, args)

    # #print(template)
    
    # Creating vm instance in order to test the service account option in template for downloading files from bucket
    #create_instance_from_template(project_id, zone, "instance-1", template.self_link)
    #delete_instance(project_id, zone, "instance-1")


    # Create a managed instance group 
    create_managed_instance_group(project_id, zone, args.cluster_name, template.name)
    # Check if the firewall rule exists
    if check_firewall_rule(project_id, args.cluster_name+"-firewall"):
        print("Firewall rule exists")
    else:
        print("Firewall rule does not exist")
        create_firewall_rule(project_id, args.cluster_name+"-firewall")
    
