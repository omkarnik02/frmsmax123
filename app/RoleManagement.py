import pandas as pd
from flask import Flask
from datetime import datetime

import time

app = Flask(__name__)


class MyRoleclass:
    def __init__(self, UserName, email, phoneNo, Role, Clearance, groups, Passwords, Status):
        self.id = int(time.time())
        self.UserName = UserName
        self.email = email
        self.phoneNo = phoneNo
        self.Role = Role
        self.Clearance = Clearance
        self.groups=groups
        self.Passwords=Passwords
        self.Status = Status


class RoleManager:
    def __init__(self, user, df, del_df, rolesmaster, ClearanceMaster, engine):
        self.user = user
        self.df = df
        self.deleted_df = del_df
        self.rolesmaster=rolesmaster
        self.ClearanceMaster=ClearanceMaster
        self.engine=engine
    
    def save_to_database(self, savedf):
        print('save')
        role_map = self.rolesmaster.set_index("Role").to_dict()["RoleID"]
        clearance_map = self.ClearanceMaster.set_index("sections").to_dict()["ClearanceID"]

        # Replace Role with RoleID
        savedf["RoleID"] = savedf["Role"].map(role_map)

        # Replace Clearance with ClearanceID
        savedf["ClearanceID"] = savedf["Clearance"].map(lambda x: clearance_map.get(str(x), x))

        # Drop original Role and Clearance columns if necessary
        savedf = savedf.drop(["Role", "Clearance"], axis=1, errors="ignore")
        self.engine.connect()
        savedf.to_sql(name='UserMaster', con=self.engine, if_exists='replace', index=False)
        self.engine.dispose()

    def create_role(self, UserName, email, phoneNo, Role, Clearance, groups, Passwords, Status):
        existing_role = self.df[
            (self.df['UserName'] == UserName) & 
            (self.df['email'] == email) &
            (self.df['phoneNo'] == phoneNo) &
            (self.df['Role'] == Role) & 
            (self.df['Clearance'] == Clearance) & 
            (self.df['groups'] == groups)&
            (self.df['Passwords'] == Passwords) & 
            (self.df['Status'] == Status) 
        ]
        
        if not existing_role.empty:
            return "Role already exists"
        r1role = MyRoleclass(UserName, email, phoneNo, Role, Clearance, groups, Passwords, Status)
        role_data = {
            'id': r1role.id,
            'UserName': UserName,
            'email': email,
            'phoneNo': phoneNo,
            'Role': Role,
            'Clearance': Clearance,
            'groups': groups,
            'Passwords': Passwords,
            'Status': Status
        }

        with open('logs.txt', 'a') as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f" Created role:  with id  on Date: {now}+\n")
        self.df = pd.concat([self.df, pd.DataFrame([role_data])], ignore_index=True)
        self.save_to_database(self.df)

    def update_role(self, role_id, UserName=None, email=None, phoneNo=None, Role=None, Clearance=None, groups=None,
                    Passwords=None, Status=None):
        if role_id in self.df['id'].values:
            old_row = self.df[self.df['id'] == role_id].iloc[0]
            print(UserName)
            old_role = old_row['Role']
            old_email=old_row['email']
            old_phoneNo = old_row['phoneNo']
            old_Clearance = old_row['Clearance']
            old_groups = old_row['groups']
            old_Passwords = old_row['Passwords']
            old_Status = old_row['Status']

            if UserName:
                self.df.loc[self.df['id'] == role_id, 'UserName'] = UserName
            if email:
                self.df.loc[self.df['id'] == role_id, 'email'] = email
            if phoneNo:
                self.df.loc[self.df['id'] == role_id, 'phoneNo'] = phoneNo
            if Role:
                self.df.loc[self.df['id'] == role_id, 'Role'] = Role
            if Clearance:
                self.df.loc[self.df['id'] == role_id, 'Clearance'] = Clearance
            if groups:
                self.df.loc[self.df['id'] == role_id, 'groups'] = groups
            if Passwords:
                self.df.loc[self.df['id'] == role_id, 'Passwords'] = Passwords
            if Status:
                self.df.loc[self.df['id'] == role_id, 'Status'] = Status

            with open('logs.txt', 'a') as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"User updated role with ID: {role_id}, from:\n"
                        f"   Role: {old_role}, Email: {old_email}, PhoneNo: {old_phoneNo}, Clearance: {old_Clearance}, Groups: {old_groups}, Passwords: {old_Passwords}, Status: {old_Status}\n"
                        f" to:\n"
                        f"   Role: {Role}, Email: {email}, PhoneNo: {phoneNo}, Clearance: {Clearance}, Groups: {groups}, Passwords: {Passwords}, Status: {Status}\n"
                        f"Updated on: {now}\n")

            self.save_to_database(self.df)

    def delete_role(self, role_id, username):
        if role_id in self.df['id'].values:
            self.deleted_df = pd.concat([self.deleted_df, self.df[self.df['id'] == role_id]], ignore_index=True)
            self.df = self.df[self.df['id'] != role_id]
            with open('logs.txt', 'a') as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"Role ID: {role_id} deleted by {username} on: {now}\n")
            self.save_to_database(self.df)

    def toggle_role_status(self, role_id):
        if role_id in self.df['id'].values:
            current_status = self.df.loc[self.df['id'] == role_id, 'Status'].iloc[0]
            new_status = 'Active' if current_status == 'Inactive' else 'Inactive'
            self.df.loc[self.df['id'] == role_id, 'Status'] = new_status
            with open('logs.txt', 'a') as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"Role ID: {role_id}, Status changed from {current_status} to {new_status}, Changed on: {now}\n")
            self.save_to_database(self.df)

    def get_roles(self):
        # Return rules as a list of dictionaries
        return self.df.to_dict('records')
