
class TemplateParams:
    def __init__(self, name, machine_type="e2-micro", disk_size=10, disk_type="pd-standard", extra_disk_type="pd-standard", extra_disk_size=20, image_project="debian-cloud", image_family="debian-11"):
        self.name = name
        self.machine_type = machine_type
        self.disk_size = disk_size
        self.disk_type = disk_type
        self.extra_disk_size = extra_disk_size
        self.extra_disk_type = extra_disk_type
        self.image_project = image_project
        self.image_family = image_family
    
    def __str__(self):
        return f"TemplateParams(name={self.name}, machine_type={self.machine_type}, disk_size={self.disk_size}, disk_type={self.disk_type}, extra_disk_size={self.extra_disk_size}, extra_disk_type={self.extra_disk_type}, image_project={self.image_project}, image_family={self.image_family})"
