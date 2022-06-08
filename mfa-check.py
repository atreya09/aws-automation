
import time
start_time = time.time()

import boto3
import csv

service_accounts = ['acoe_', 'acoe', 'odp_', 'ite', 'ite_', 'flightdeck', 'odp', 'ec2import']


# calling all iam users
def removeServiceAcc(curr_user):
    for serv in service_accounts:
        if curr_user.lower().startswith(serv.lower()):
            return 1
    return 0


iam_cl = boto3.client("iam")
users = iam_cl.list_users()

all_usernames = []


def getActualUsers():
    for user in users["Users"]:
        myUser = user["UserName"]
        if removeServiceAcc(myUser) != 1:
            all_usernames.append(myUser)
    return all_usernames


getActualUsers()
iam = boto3.resource('iam')


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
print(all_usernames)
print(len(all_usernames))


def noInfoUsersRemoved():
    bad_usernames = all_usernames
    for iter_user in bad_usernames:
        # iter_user = i["UserName"]

        if pwdNoLastUsedCheck(iter_user) == 0:
            # removes password last used having some date ie give NA and no information

            if isPasswordEnabled(iter_user) == 1:

                all_usernames.remove(iter_user)  # return the user with password enabled = true because with NA it
                # will be false
    return all_usernames


def getNoMFA():
    target_users = noInfoUsersRemoved()

    # extracting the users for whom no mfa  exists
    for myUser in target_users:

        usersMfa = iam_cl.list_mfa_devices(UserName=myUser)
        if usersMfa["MFADevices"]:
            all_usernames.remove(myUser)
    return all_usernames



username = getNoMFA()
print(username)
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
print("--- %s seconds for %d users---" % (time.time() - start_time, len(all_usernames)))
