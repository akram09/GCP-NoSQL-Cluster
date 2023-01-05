# GCP NoSQL cluster creation
Python script for automating the creation of a nosql cluster on GCP

## Features
- Creation of stateful managed instance group from created template.
- Running with command line arguments allows users to pass input to the script and modify its behavior at runtime through the use of arguments and options.
- Start-up scripts for most of linux distributions.
- Using Google Cloud Storage to store start-up script.

...


Built on Python: 3.10.8



## File Structure 
\# Todo: needs update
```
.
├── bin
    ├── startuo-script-debian.sh
    ├── startuo-script-rhel.sh
    └── startuo-script-suse.sh
├── cluster
    └── cluster.py
├── lib
    ├── managed_instance.py
    ├── storage.py
    ├── template.py
    └── vm_instance.py
├── utils
    ├── args.py
    ├── env.py
    └── gcp.py
├── .gitignore
├── main.py
├── requirements.txt
├── .env
├── template.json
└── service.json
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

- Put there the necessary info

- Run main.py
1) passing cluster arguments with command line, for example: 
```bash
python main.py --cluster-name mig-2 --cluster-size 4 --machine-type e2-micro --image-project debian-cloud --image-family debian-11 --disk-type pd-standard --disk-size 10
```
2) passing cluster arguments with yaml file, Here's a `template.yaml`:
```yaml
cluster_name: mig-4
cluster_size: 4
image_project: debian-cloud
image_family: debian-11
machine_type: e2-micro
disk_type: pd-standard
disk_size: 10
bucket: bucket-7972cfbe-3da3-4f7f-a1fa-770a13c853eb 
```

```bash
python main.py --yaml-file template.yaml
```
