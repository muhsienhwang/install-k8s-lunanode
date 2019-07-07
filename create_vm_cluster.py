#!/usr/bin/env python
from lndynamic import LNDynamic
import natsort
import time

# find lunanode credentials
with open(r"/home/hme/.lunanode/commands.txt") as hpass:
    lines = hpass.readlines()
api = LNDynamic(lines[0].rstrip('\n'), lines[1].rstrip('\n'))


def create_master_cluster(name):
    api.request("vm", "create",
                {'hostname': name, 'plan_id': 4, 'region': 'roubaix', 'image_id': 148540, 'storage': 70})


cluster_name = 'k8s-cluster-'
number_of_vm = input("Nbr_of_cluster ? ")

for i in range(1, int(number_of_vm) + 1):
    create_master_cluster(cluster_name + str(i) + "-master")
    for j in range(1, 4):
        vm_name = cluster_name + str(i) + "-node-" + str(j)
        api.request("vm", "create",
                    {'hostname': vm_name, 'plan_id': 4, 'region': 'roubaix', 'image_id': 148540, 'storage': 70})

# sleep while lunanode set up public ip addresses for each VMs
time.sleep(120)
results = api.request('vm', 'list')
f = open(r"/home/hme/inventory_lunanode", "w+")
hfile = open(r"/home/hme/user_list_k8s", "w+")
val = results.get("vms")
user_dic = {}
print
len(val)
for i in range(0, len(val)):
    flag = 0
    for key, value in val[i].items():
        if key == 'name':
            if "k8s-cluster" not in value:
                break
            print('name=', value)
            user = value
        if key == 'primaryip':
            ip = value
            print('ip=', value)
        if key == 'plan_id':
            print('plan_id=', value)
        if key == 'vm_id':
            print('vm_id=', value)
            vm_info = api.request('vm', 'info', {'vm_id': value})
            st = vm_info.get('info')
            # print(st)
            # print type(st)
            # print len(st)
            try:
                print(st['login_details'])
                user_login = st['login_details']
                a = user_login.split()
                print(str(ip), str(a[1]), str(a[3]))
                gt = str(a[1])[:-1]
                line = "{}  ansible_ssh_user={}  ansible_ssh_pass={} ansible_ssh_extra_args='-o StrictHostKeyChecking=no'\n".format(
                    str(ip), str(gt), str(a[3]))
                # user_line="{} \t {} \t centos \t lawn-vex\n".format(user,str(ip))
                f.write(line)
                user_dic[str(user)] = str(ip)
                # hfile.write(user_line)
            except KeyError as error:
                pass
            # for v in range (0,len(st)):
            #    for z,y in st[v].items():
            #        if z == 'login_details':
            #            print( "user = ",y)

f.close()
# print (user_dic)
list_user = user_dic.keys();
natural = natsort.natsorted(list_user)
# print natural
for vts in range(0, len(natural)):
    myip = user_dic[natural[vts]]
    user_line = "{} \t {} \t centos \n".format(natural[vts], myip)
    hfile.write(user_line)
hfile.close()
