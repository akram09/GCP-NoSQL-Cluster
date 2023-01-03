import os, uuid
from dotenv import load_dotenv
from utils.env import check_env
from utils.args import parse_cluster_args, create_template_from_args, create_template_from_yaml
from lib.managed_instance import create_managed_instance_group
from lib.template import list_instance_templates, delete_instance_template


if __name__ == "__main__":
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
    #print(list_instance_templates(project_id))
    #delete_instance_template(project_id, template_name)


    # test if args has attribute yaml_file
    if hasattr(args, 'yaml_file'):
        template = create_template_from_yaml(project_id, zone, template_name, args.yaml_file)
    else:
        # test if cluster_name and cluster_size are defined in args
        if args.cluster_name == None:
            raise Exception("cluster_name is not defined in the args")  
        if args.cluster_size == None:
            raise Exception("cluster_size is not defined in the args")
            
        template = create_template_from_args(project_id, zone, template_name, args)
    print(template)
    # # Create a managed instance group 
    # create_managed_instance_group(project_id, zone, "mig-1", template.name)
    
