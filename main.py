
from utils.template import get_instance_template
from config import PROJECT_ID


if __name__ == "__main__":
    template_name = "template-sample-1"
    vm_template = get_instance_template(PROJECT_ID,template_name)

    print(vm_template)