from lib.managed_instance import list_instances
from jinja2 import Template
from lib.vm_instance import get_instance
from lib.storage import upload_cluster_provisioning_script
# create the couchbase cluster 
def create_couchbase_cluster(project_id, nodes, bucket, cluster_username, cluster_password):
    # get the master node name 
    master_node_name = nodes[0].name
    # map nodes list to hostnames list  using gcp internal dns
    hostnames = list(map(lambda node: node.name + ".c." + project_id + ".internal", nodes))
    # get the master node hostname
    master_node_hostname = hostnames[0]
    # remove the master node from the list 
    hostnames.pop(0)
    # render the cluster init script
    with open("./bin/cluster-provisioning/cluster-init.j2", "r") as f:
        template = Template(f.read())
    # render the template 
    rendered_template = template.render(master_node_name=master_node_name, master_node_hostname=master_node_hostname, admin_username=cluster_username, admin_password=cluster_password, nodes=hostnames)
    # write the rendered template to a file
    with open("./bin/cluster-provisioning/cluster-init.sh", "w") as f:
        f.write(rendered_template)
    # upload cluster provisioning script to bucket
    upload_cluster_provisioning_script(bucket)
