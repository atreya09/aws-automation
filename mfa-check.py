import time
from pprint import pprint

start_time = time.time()

import boto3
import csv

service_accounts = ('acoe_', 'acoe', 'odp_', 'ite', 'ite_', 'flightdeck', 'odp', 'ec2import')


# calling all iam users
def removeServiceAcc(curr_user):
    for serv in service_accounts:
        if curr_user.lower().startswith(serv.lower()):
            return 1
    return 0


iam = boto3.resource('iam')
#print()

# iam_cl = boto3.client("iam") # use Meta or try to use iam.user.name check boto3 fist video
# pagination  get_paginator().paginate --> will return all users else use resource, by default iam returns 100 users only in one go
"""
for user in iam.users.all():
print(user.name)
"""
users = iam.meta.client.get_paginator("list_users")
page = users.paginate()
#iam.LoginProfile("Harry_UI")

#all_usernames = []


def getActualUsers():
    all_users = []
    for user in page:
        for username in user["Users"]:
            myUser = username["UserName"]
            if removeServiceAcc(myUser) != 1:
                all_users.append(myUser)
    return all_users



target_users = tuple(getActualUsers())
def getNoMFA():

    false_mfa_users = []
    # extracting the users for whom no mfa  exists
    for myUser in target_users:

        usersMfa = iam.meta.client.get_paginator('list_mfa_devices')
        #usersMfa = iam.meta.client.list_mfa_devices(UserName = myUser)
        mfa_page = usersMfa.paginate(UserName=myUser)
        for sample in mfa_page:
            if not sample["MFADevices"]:
                false_mfa_users.append(myUser)
    return false_mfa_users

users_to_check = tuple(getNoMFA())

# dir(iam) -> gives list of all attributes for iam object
def pwdNoLastUsedCheck(x):
    if iam.User(x).password_last_used:

        return 1
    else:
        return 0


def isPasswordEnabled(x):
    try:
        iam.LoginProfile(x)
        login_profile = iam.LoginProfile(x)
        if login_profile.create_date:
            return 1
    except:
        return 0


# passwordEnabled = true and password last used = no


def noInfoUsersRemoved():
    no_info_users = list(users_to_check)
    for iter_user in users_to_check:
        # iter_user = i["UserName"]

        if pwdNoLastUsedCheck(iter_user) == 0:
            # removes password last used having some date ie give NA and no information

            if isPasswordEnabled(iter_user) == 1:
                no_info_users.remove(iter_user)  # return the user with password enabled = true because with NA it
                # will be false
    return no_info_users



username = noInfoUsersRemoved()

"""
user_to_remove = []
for user in username:
    if removeServiceAcc(user) == 1:
        # username.remove(user)
        user_to_remove.append(user)

for item in user_to_remove:
    username.remove(item)
"""
# form the rows and columns of csv
fields = ["User names"]
rows = len(username)
cols = len(fields)
hasNoMfa = [[username[i] for j in range(cols)] for i in range(rows)]

# alternative of the above - the below loop is eseentially wriiten in compact form above

"""
hasNoMfa = []
for i in range(rows):
    for j in range(cols):
        hasNoMfa.append([username[i]])   #[value to append] ie in [] gives the structure like [[],[]]

"""
# form the csv to write and get the list of users
with open('noUsers.csv', mode='w+', newline="") as file:
    csvwriter = csv.writer(file)
    csvwriter.writerow(fields)
    csvwriter.writerows(hasNoMfa)
"""



"""
print("--- %s seconds for %d users---" % (time.time() - start_time, len(target_users)))
