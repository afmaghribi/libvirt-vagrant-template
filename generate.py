#!/usr/bin/env python3
import os, yaml
from jinja2 import Environment,FileSystemLoader
from crypt import crypt,mksalt,METHOD_SHA512

def render_network(specs):
    template_file = Environment(loader=FileSystemLoader("./templates")).get_template("network-config.j2")

    for vms in (specs['vm_specs']):
        if not os.path.isdir("./"+vms['hostname']):
            os.makedirs("./"+vms['hostname'])

        output = open("./"+vms['hostname']+"/network-config","w")
        output.write(template_file.render(specs))
        output.close()

        output = open("./"+vms['hostname']+"/meta-data","w")
        output.close()

def render_cloud_init(specs):
    template_file = Environment(loader=FileSystemLoader("./templates")).get_template("user-data.j2")
    
    for vms in (specs['vm_specs']):
        vms['hashed_password']= crypt(vms['password'], mksalt(METHOD_SHA512))

        if "pub_key" not in specs.keys():
            key_path = os.path.expanduser('~/.ssh/id_rsa.pub')
            vms["pub_key"] = open(key_path,"r").read().strip()
            vms["priv_key"] = key_path[:-4]
        elif "ssh-rsa" not in vms["pub_key"]:
            vms["pub_key"] = open(vms["pub_key"],"r").read().strip()
            vms["priv_key"] = vms["pub_key"][:-4]

        if not os.path.isdir("./"+vms['hostname']):
            os.makedirs("./"+vms['hostname'])

        output = open("./"+vms['hostname']+"/user-data","w")
        output.write(template_file.render(vms))
        output.close()
        os.system(f"mkisofs -output {vms['hostname']}.iso -volid cidata -joliet -rock -R {vms['hostname']}")

def render_vagrantfile(specs):
    template_file = Environment(loader=FileSystemLoader("./templates")).get_template("Vagrantfile.j2")
    
    for vms in (specs['vm_specs']):
        vms["cloud_init_path"] = os.getcwd() + "/" + vms['hostname'] + ".iso"

    output = open("./Vagrantfile","w")
    output.write(template_file.render(specs))
    output.close()


if __name__ == "__main__": 
    config = yaml.safe_load(open("vagrant-specs.yaml","r"))
    render_network(config['vagrant_specs'])
    render_cloud_init(config['vagrant_specs'])
    render_vagrantfile(config['vagrant_specs'])