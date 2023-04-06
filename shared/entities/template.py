from loguru import logger
class TemplateParams:
    def __init__(self, name, machine_type="e2-micro", image_project="debian-cloud", image_family="debian-11", template_labels = {}):
        self.name = name
        self.machine_type = machine_type
        self.image_project = image_project
        self.image_family = image_family
        self.labels = template_labels
    def set_disks(self, disks):
        # check if the disk is a list
        if isinstance(disks, list):
            main_disks_count = 0
            disks_params = []
            for disk in disks:
                if disk['boot'] == True:
                    main_disks_count += 1
                    disks_params.append(TemplateDiskParams(disk['size'], disk['type'],  disk['boot']))
                else:
                    disks_params.append(TemplateDiskParams(disk['size'], disk['type'],  disk['boot']))
            if main_disks_count > 1:
                logger.error("More than one boot disk found")
                raise Exception("More than one boot disk found")
            self.disks = disks_params

            
        else:
            logger.error("Template Disks must be a list")
            exit(0)
        # check if disks contains only one main disk
        
    
    def __str__(self):
        return f"Template Name: {self.name}, Machine Type: {self.machine_type}, Image Project: {self.image_project}, Image Family: {self.image_family}, Disks: {self.disks}"


class TemplateDiskParams:
    def __init__(self, size, type, boot=True):
        self.size = size
        self.type = type
        self.boot = boot
    def __str__(self):
        return f"Disk Size: {self.size}, Disk Type: {self.type}, Boot: {self.boot}"
