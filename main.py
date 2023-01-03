import os
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_cluster_args, create_template_from_args
from lib.managed_instance import create_managed_instance_group
from lib.template import list_instance_templates, delete_instance_template, get_instance_template
from lib.firewall import create_firewall_rule, check_firewall_rule


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

    #Create instance templace
    #TODO: generate template name from the number of created templates
    template_name = "template-2"
    # delete_instance_template(project_id, template_name)
    template = create_template_from_args(project_id, zone, template_name, args)
    
    # Create a managed instance group 
    create_managed_instance_group(project_id, zone, args.cluster_name, template.name)
    # Check if the firewall rule exists
    if check_firewall_rule(project_id, args.cluster_name+"-firewall"):
        print("Firewall rule exists")
    else:
        print("Firewall rule does not exist")
        create_firewall_rule(project_id, args.cluster_name+"-firewall")
    
