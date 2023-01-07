from lib.managed_instance import list_instances
from jinja2 import Template
from lib.vm_instance import get_instance
from lib.storage import upload_cluster_provisioning_script
# create the couchbase cluster 
def create_couchbase_cluster(project_id, zone, bucket, instance_group_name, cluster_username, cluster_password):
    # list the managed instances 
    managed_instances = list_instances(project_id, zone, instance_group_name)
    # get instance names and ips
    nodes = []
    for managed_instance in managed_instances:
        # get managed instance name 
        managed_instance_name = managed_instance.instance.split("/")[-1]
        # get instance by name
        instance = get_instance(project_id, zone, managed_instance_name)
        # get instance ip
        instance_ip = instance.network_interfaces[0].network_i_p
        # add instance name and ip to nodes list
        nodes.append({"name": managed_instance_name, "ip": instance_ip})
    # get the master node name and ip
    master_node_name = nodes[0]["name"]
    master_node_ip = nodes[0]["ip"]
    # remove the master node from the list 
    nodes.pop(0)
    # render the cluster init script
    with open("./bin/cluster-provisioning/cluster-init.j2", "r") as f:
        template = Template(f.read())
    # render the template 
    rendered_template = template.render(master_node_ip=master_node_ip, admin_username=cluster_username, admin_password=cluster_password, nodes=nodes)
    # write the rendered template to a file
    with open("./bin/cluster-provisioning/cluster-init.sh", "w") as f:
        f.write(rendered_template)
    # upload cluster provisioning script to bucket
    upload_cluster_provisioning_script(bucket)
