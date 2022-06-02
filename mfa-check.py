#from datetime import date

import boto3
import csv

# calling all iam users
iam_cl = boto3.client("iam")
users = iam_cl.list_users()
all_usernames = []
for user in users["Users"]:
    myUser = user["UserName"]
    all_usernames.append(myUser)

iam = boto3.resource('iam')

username = []


def pwdNoLastUsedCheck(x):
    try:
        iam.User(x).password_last_used

        return iam.User(x).password_last_used
    except:
        return True


def isPasswordEnabled(x):
    login_profile = iam.LoginProfile(x)
    try:
        login_profile.create_date
        return True
    except:
        return False


# passwordEnabled = true and password last used = no

def noInfoUsers():
    bad_usernames = []
    for iter_user in all_usernames:
        # iter_user = i["UserName"]
        if pwdNoLastUsedCheck(iter_user):
            continue
        else:
            # print(f"not needed{iter_user}")
            # this block will give the users with password last used = nothing
            if isPasswordEnabled(iter_user):
                bad_usernames.append(iter_user)  # return the user with passwordenabled = true
            else:
                continue
    return bad_usernames


no_info_user = noInfoUsers()
actual_users = [x for x in all_usernames if x not in no_info_user]

# extracting the users for whom no mfa  exists
for myUser in actual_users:
    usersMfa = iam_cl.list_mfa_devices(UserName=myUser)
    if not usersMfa["MFADevices"]:
        username.append(myUser)

service_accounts = ['acoe_', 'acoe', 'odp_', 'ite',  'ite_', 'flightdeck', 'odp']
print(username)

def removeServiceAcc(curr_user):
    for serv in service_accounts:
        if curr_user.startswith(serv):
            x = 1
            break
        else:
            x = 0
            continue
    return x


user_to_remove = []
for user in username:
    if removeServiceAcc(user) == 1:
        #username.remove(user)
        user_to_remove.append(user)

for item in user_to_remove:
    username.remove(item)


#form the rows and columns of csv
fields = ["User names"]
rows = len(username)
cols = len(fields)
hasNoMfa = [[username[i] for j in range(cols)] for i in range(rows)]


#alternative of the above - the below loop is eseentially wriiten in compact form above

"""
hasNoMfa = []
for i in range(rows):
    for j in range(cols):
        hasNoMfa.append([username[i]])   #[value to append] ie in [] gives the structure like [[],[]]

"""
#form the csv to write and get the list of users
with open('noUsers.csv', mode='w+', newline="") as file:
    csvwriter = csv.writer(file)
    csvwriter.writerow(fields)
    csvwriter.writerows(hasNoMfa)

