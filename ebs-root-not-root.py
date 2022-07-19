import boto3
import pandas as pd

boto3.setup_default_session(profile_name='S5')

ec2 = boto3.client("ec2")
ec2_page = ec2.get_paginator("describe_instances")
ec2_resp = ec2_page.paginate(Filters=[
    {
        "Name": "instance-state-name",
        "Values": ["running"],
    }
],

)

my_vols = {}

abc = []

for page in ec2_resp:
    for reservation in page["Reservations"]:
        for run_ins in reservation["Instances"]:
            for block_ind, block_val in enumerate(run_ins['BlockDeviceMappings']):

                if block_ind == 0:  # first_row of block device mapping items give the root device
                    my_vols[block_val["Ebs"]["VolumeId"]] = ["root", 0]

                else:
                    my_vols[block_val["Ebs"]["VolumeId"]] = ["non-root",0]
                    # add a zero as a place to fill the vol_type here later

#180 instances
print(len(my_vols))

my_list = list(my_vols.keys()) #474

vol_page = ec2.get_paginator("describe_volumes")

b = vol_page.paginate(Filters=[
        {
            'Name': 'attachment.status',
            'Values': [
                'attached',
            ]
        },
    ],)
"""START this block tells which ids are not listed while calling the blok device mapping above and stil present 
in volumes console because volumes console will list all voulmes even for Stopped EC2s"""
mn = []
for x in b:
    for y in x['Volumes']:
        mn.append(y["VolumeId"])
for id in mn:
    if id not in my_list:
        print("false" , id)
"""END: end of block """
vol_type_resp = vol_page.paginate(VolumeIds=my_list)
for page in vol_type_resp:
    for x in page["Volumes"]:
        my_vols.get(x["VolumeId"])[1] = x["VolumeType"]

print(my_vols)
print(len(my_vols))



df = pd.DataFrame.from_dict(my_vols).T

# xyz = df.rename_axis("Vol_Ids", axis="columns")
yrg = df.rename(index=str, columns={0: "R/N", 1: "VolType"})
yrg.to_csv("ebs_details_s5.csv", index_label="Vol_Ids", mode='w+')

# main funciton
# exceptions
# functions under define
#logger
#time check of execution
