# GCP NoSQL cluster creation
Python script for automating the creation of a nosql cluster on GCP. 

## Features
- Creation of stateful managed instance group from created template.
- Running with command line arguments allows users to pass input to the script and modify its behavior at runtime through the use of arguments and options.
- Using Google Cloud Storage to store start-up script.
- Start-up scripts for the created managed virtual machine instances. 
- `server` command to bring up a rest api server that exposes all the core commands. 
- `Regional` Managed instance Group. 
- `REST API` server support running the operations in a multi-threading way. 
- `REST API` server with `swagger` documentation

...


Built on Python: 3.10.8


## Note 
The REST API server module interacts with a couchbase database server in order to persist the following items:
- Users registered to the platform
- Parallel Jobs running in the background
- Cluster creation/update payloads




## File Structure 
```
.
├── api
│   ├── config.py
│   ├── extensions.py
│   ├── __init__.py
│   ├── internal
│   │   ├── cache.py
│   │   ├── couchbase.py
│   │   ├── threads.py
│   │   └── utils.py
│   ├── models
│   │   └── user.py
│   └── routes
│       ├── auth.py
│       ├── cluster.py
│       ├── job.py
│       ├── kms.py
│       ├── managed_instance.py
│       ├── storage.py
│       └── template.py
├── cmd
│   ├── create_cmd.py
│   ├── __init__.py
│   ├── server_cmd.py
│   └── update_cmd.py
├── example.env
├── main.py
├── README.md
├── requirements.txt
├── shared
│   ├── bin
│   │   ├── shutdown-scripts
│   │   │   ├── shutdown-script-debian.j2
│   │   │   ├── shutdown-script-rhel.j2
│   │   │   └── shutdown-script-suse.j2
│   │   └── startup-scripts
│   │       ├── startup-script-debian.j2
│   │       ├── startup-script-rhel.j2
│   │       └── startup-script-suse.j2
│   ├── core
│   │   ├── apply_migration_cluster.py
│   │   ├── create_cluster.py
│   │   ├── instance_template_operations.py
│   │   ├── kms_operations.py
│   │   ├── managed_instance_group_operations.py
│   │   ├── storage_operations.py
│   │   └── update_cluster.py
│   ├── discovery
│   │   ├── kms.py
│   │   └── secrets_manager.py
│   ├── entities
│   │   ├── cluster.py
│   │   ├── couchbase.py
│   │   ├── gcp_project.py
│   │   ├── storage.py
│   │   └── template.py
│   └── lib
│       ├── disks.py
│       ├── firewall.py
│       ├── images.py
│       ├── instances.py
│       ├── kms.py
│       ├── regional_managed_instance.py
│       ├── secrets_manager.py
│       ├── storage.py
│       └── template.py
├── template.yaml
├── update-template.yaml
└── utils
    ├── args.py
    ├── env.py
    ├── exceptions.py
    ├── __init__.py
    ├── parse_requests.py
    ├── shared.py
    └── yaml.py
```

## Installation and usage
- clone the repository
```bash
git clone [ .git repository link]
cd GCP-NoSQL-Cluster
```

- use `venv` virtual environment
```bash
pip install venv
python -m venv venv
source $PWD/venv/bin/activate
```

- Install dependencies
```bash
pip install -r requirements.txt
```

- Create env from env template:
```bash
cp example.env .env 
```
- Set the environment variables:
```
SERVICE_ACCOUNT_OAUTH_TOKEN=
COUCHBASE_USER=
COUCHBASE_PASSWORD=
```
or 
```
COUCHBASE_CERT_PATH=
```

- Run main.py
1) Using the `create` command in order to create a cluster 
  a)  passing cluster arguments with command line, for example: 
    ```bash
      python main.py create --cluster-name mig-2 --cluster-size 4 --machine-type e2-micro --image-project debian-cloud --image-family debian-11 --disk-type pd-standard --disk-size 10
    ```

  b) passing cluster arguments with yaml file:
  ```bash
    python main.py create --yaml-file template.yaml
  ```

2) Using the `update` command in order to update a cluster 
  a)  passing cluster arguments with command line, for example: 
    ```bash
      python main.py update --cluster-name mig-2 --cluster-size 4 --machine-type e2-micro --image-project debian-cloud --image-family debian-11 --disk-type pd-standard --disk-size 10
    ```

  b) passing cluster arguments with yaml file:
  ```bash
    python main.py update --yaml-file template.yaml
  ```

3) Using the `server` command in order to start the REST API that exposes routes to perform lifecycle management operations. 
  ```bash
  python main.py server
  ```
