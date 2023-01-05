import subprocess 
from jinja2 import Template


# initialize the db cluster 
def execute_cluster_init(master_node_name, master_node_ip, admin_username, admin_password, nodes):
    # render the cluster init script
    render_cluster_init_script(master_node_ip, admin_username, admin_password, nodes)
    # execute the cluster init script
    subprocess.run(["./bin/cluster-provisioning/execute.sh", master_node_name])


# render the cluster init script using jinja2 
def render_cluster_init_script(master_node_ip, admin_username, admin_password, nodes):
    # read the template 
    with open("./bin/cluster-provisioning/create-cluster.j2", "r") as f:
        template = Template(f.read())
    # render the template 
    rendered_template = template.render(master_node_ip=master_node_ip, admin_username=admin_username, admin_password=admin_password, nodes=nodes)
    print(rendered_template)
    # write the rendered template to a file
    with open("./bin/cluster-provisioning/cluster-init.sh", "w") as f:
        f.write(rendered_template)

    # make the cluster init script executable
    subprocess.run(["chmod", "+x", "./bin/cluster-provisioning/cluster-init.sh"])
