from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc
from sqlalchemy import create_engine
from app.RoleManagement import RoleManager
import pandas as pd

roles_routes = Blueprint('roles_routes', __name__)


server = '172.25.57.117'
database = 'FRMS_AI'
username = 'sa'
password = 'P@ss1234'
Driver='{SQL Server Native Client 11.0}'
engine = create_engine(
    'mssql+pyodbc:///?odbc_connect=DRIVER={SQL Server Native Client 11.0};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
rolesdf=pd.read_sql('''select um.id,um.UserName,um.email,um.phoneNo,rm.[Role],cm.sections as [Clearance],um.groups,um.Passwords,um.[Status] from usermaster um
left join RoleMaster rm on um.RoleID=rm.RoleID
left join ClearanceMaster cm on um.ClearanceID=cm.ClearanceID''',conn)
rolesmaster=pd.read_sql('''select * from RoleMaster''',conn)
ClearanceMaster=pd.read_sql('''select * from ClearanceMaster''',conn)

global rule_manager

role_manager = RoleManager(None,rolesdf, pd.read_csv('app/delroles.csv'),rolesmaster,ClearanceMaster,engine)

@roles_routes.route('/System_module/roles', methods=['GET', 'POST'])
def roles():
    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))  # Redirect to login if session is not set

    if request.method == 'POST':
        # Handle form submission to create role
        UserName = request.form['UserName']
        email = request.form['email']
        phoneNo = request.form['phoneNo']
        Role = request.form['Role']
        Clearance = request.form['Clearance']
        groups = request.form['groups']
        Passwords = request.form['Passwords']
        Status = request.form['Status']

        # Handle role creation and validation
        message = role_manager.create_role(UserName, email, phoneNo, Role, Clearance, groups, Passwords, Status)
        if message:
            return render_template('System_module.html', roles=role_manager.df.to_dict('records'), user=username,
                                   message=message)

    roles_data = role_manager.df.to_dict('records')
    return render_template('System_module.html', roles=roles_data, user=username)


@roles_routes.route('/System_module/update/<int:role_id>', methods=['POST'])
def update_role(role_id):
    # Handle updating role
    UserName = request.form['UserName']
    email = request.form['email']
    phoneNo = request.form['phoneNo']
    Role = request.form['Role']
    Clearance = request.form['Clearance']
    groups = request.form['groups']
    Passwords = request.form['Passwords']
    Status = request.form['Status']

    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))  # Redirect to login if session is not set
    role_manager.update_role(role_id, UserName, email, phoneNo, Role, Clearance, groups, Passwords, Status)
    return redirect(url_for('roles_routes.roles', user=username))


@roles_routes.route('/System_module/delete/<int:role_id>', methods=['POST'])
def delete_role(role_id):
    # Handle deleting role
    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))
    role_manager.delete_role(role_id, username)
    return redirect(url_for('roles_routes.roles', user=username))


@roles_routes.route('/System_module/toggle/<int:role_id>', methods=['POST'])
def toggle_role(role_id):
    # Handle toggling role status
    role_manager.toggle_role_status(role_id)
    return redirect(url_for('roles_routes.roles'))

# You can define other routes related to roles similarly
