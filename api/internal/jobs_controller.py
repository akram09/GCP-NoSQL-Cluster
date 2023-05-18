# Description: Main functions for the management of the jobs. 
from api.extensions import couchbase


# insert a job in the database  
def add_job(job_id, cluster_name, job_type, status, project_id):
    """
    Insert a job in the database.
    Parameters: 
        job_id (str): the id of the job
        cluster_name (str): the cluster name of the job
        job_type (str): the type of the job
        status (str): the status of the job
        project_id (str): the id of the project
    """
    job= {
        'name': job_id,
        'cluster_name': cluster_name,
        'type': job_type,
        'status': status,
        'project-id': project_id
    }
    # insert the job in the database
    couchbase.insert('jobs', job_id, job)

# update the status of a job
def update_job_status(job_id, status, message=None):
    """
    Update the status of a job.
    Parameters:
        job_id (str): the id of the jobs
        status (str): the status of the job
        message (str): the message of the job
    """
    # get the job from the database
    job = couchbase.get('jobs', job_id)
    # update the status of the job
    job['status'] = status
    if message:
        job['message'] = message
    # update the job in the database
    couchbase.update('jobs', job_id, job)


# check if the job exists in the database.
def check_job(job_id):
    """
    Check if the job exists in the database.
    """
    return couchbase.check('jobs', job_id)

# get the job from the database
def get_job(job_id):
    """
    Get the job from the database.
    """
    return couchbase.get('jobs', job_id)

# get the list of the jobs from the database
def get_job_list():
    """
    Get the list of the jobs from the database.
    """
    jobs_list = couchbase.list('jobs')
    jobs_list = list(map(lambda jobs: jobs['jobs'], jobs_list))
    return jobs_list
