

jobs = {}


# add a job to the jobs dictionary
def add_job(job_id, cluster_name, job_type, status):
    jobs[job_id] = {
        'name': job_id,
        'cluster_name': cluster_name,
        'type': job_type,
        'status': status
    }

# update the status of a job
def update_job_status(job_id, status, message=None):
    jobs[job_id]['status'] = status
    if message:
        jobs[job_id]['message'] = message



# check if the job is in the jobs dictionary  
def check_job(job_id):
    return job_id in jobs

# get the job from the jobs dictionary
def get_job(job_id):
    return jobs[job_id]

