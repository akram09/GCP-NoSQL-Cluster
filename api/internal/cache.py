# Description: This file simulate a caching system it stores the jobs that are running in the background.
import threading 

# create a lock 
jobs_lock = threading.Lock()
jobs = {}


# add a job to the jobs dictionary
def add_job(job_id, cluster_name, job_type, status):
    """
    Add a job to the jobs dictionary, this function is thread safe.
    Parameters: 
        job_id (str): the id of the job
        cluster_name (str): the cluster name of the job
        job_type (str): the type of the job
        status (str): the status of the job
    """
    # acquire the lock
    jobs_lock.acquire()
    jobs[job_id] = {
        'name': job_id,
        'cluster_name': cluster_name,
        'type': job_type,
        'status': status
    }
    # release the lock
    jobs_lock.release()

# update the status of a job
def update_job_status(job_id, status, message=None):
    """
    Update the status of a job, this function is thread safe.
    Parameters:
        job_id (str): the id of the jobs
        status (str): the status of the job
        message (str): the message of the job
    """
    # acquire the lock
    jobs_lock.acquire()
    jobs[job_id]['status'] = status
    if message:
        jobs[job_id]['message'] = message
    # release the lock
    jobs_lock.release()


# check if the job is in the jobs dictionary  
def check_job(job_id):
    """
    Check if the job is in the jobs dictionary.
    """
    return job_id in jobs

# get the job from the jobs dictionary
def get_job(job_id):
    """
    Get the job from the jobs dictionary.
    """
    return jobs[job_id]

# get the job list from the jobs dictionary
def get_job_list():
    """
    Get the job list from the jobs dictionary.
    """
    return list(jobs.values())
