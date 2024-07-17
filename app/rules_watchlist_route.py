from datetime import datetime
import pyodbc
from sqlalchemy import create_engine
from flask import Blueprint, render_template, request, redirect, url_for, session
from app.RuleManagement import RuleManager,log_event
import pandas as pd
from app.alert_route import inAlert, upAlert


server = '172.25.57.117'
database = 'FRMS_AI'
username = 'sa'
password = 'P@ss1234'
Driver='{SQL Server Native Client 11.0}'
engine = create_engine(
    'mssql+pyodbc:///?odbc_connect=DRIVER={SQL Server Native Client 11.0};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
rolesdf=pd.read_sql('''select * from RuleTable''', conn)

global role_manager
rule_manager = RuleManager(None, rolesdf, pd.read_csv('app/delRules.csv'), engine,conn)

rules_watchlist_routes = Blueprint('rules_watchlist_routes', __name__)
def get_options_from_db():
    cursor = conn.cursor()
    cursor.execute("SELECT OperatorValue,OperatorType from OperatorMaster")
    operator = cursor.fetchall()
    cursor.execute("SELECT ChannelID,Channel from ChannelMaster")
    channel = cursor.fetchall()
    cursor.execute("SELECT ColumnID,ColumnName from ColumnMaster")
    columnname = cursor.fetchall()
    options = {
        "operator": operator,
        "channel": channel,
        "columnname":columnname
    }
    cursor.close()
    return options

# def paginate_data(filtered_rules_data, page, per_page):
#     total_alerts = len(filtered_rules_data)
#     total_pages = (total_alerts + per_page - 1) // per_page
#
#     # Slice the DataFrame for the current page
#     start_idx = (page - 1) * per_page
#     end_idx = start_idx + per_page
#     filtered_rules_data=pd.DataFrame(filtered_rules_data)
#     rules_data_page = filtered_rules_data.iloc[start_idx:end_idx]
#
#     rules_list = rules_data_page.to_dict('records')
#     return rules_list, total_pages

def get_latest_row():
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 * FROM form_data ORDER BY id DESC")
    row = cursor.fetchone()

    if row:
        latest_row = [row.slider_value, (row.ruleswitch ==1),
                      (row.aiswitch==1 )]
    else:
        latest_row = [0, 1, 1]

    cursor.close()
    return latest_row

def extract_search_parameters(filtered_rules_data):
    search_id = request.args.get('search_id')
    search_channel = request.args.get('search_channel')
    search_columns = request.args.get('search_columns')
    search_allow_prevent = request.args.get('search_Allow/Prevent')
    search_created_on = request.args.get('search_created_on')
    search_created_by = request.args.get('search_created_by')
    search_status = request.args.get('search_Status')
    search_modified_on = request.args.get('search_modified_on')
    search_modified_by = request.args.get('search_modified_by')

    if search_id:
        filtered_rules_data = filtered_rules_data[filtered_rules_data['id'].astype(str).str.contains(search_id.strip())]
    if search_channel:
        filtered_rules_data = filtered_rules_data[
            filtered_rules_data['channel'].str.contains(search_channel.strip(), case=False)]
    if search_columns:
        filtered_rules_data = filtered_rules_data[
            filtered_rules_data['column_name'].str.contains(search_columns.strip(), case=False)]
    if search_allow_prevent:
        filtered_rules_data = filtered_rules_data[
            filtered_rules_data['allowprevent'].str.contains(search_allow_prevent.strip(), case=False)]
    if search_created_on:
        try:
            search_created_on_date = datetime.strptime(search_created_on, '%Y-%m-%d').date()
            filtered_rules_data = filtered_rules_data[
                pd.to_datetime(filtered_rules_data['created_on'], errors='coerce').dt.date == search_created_on_date]
        except ValueError:
            pass
    if search_created_by:
        filtered_rules_data = filtered_rules_data[
            filtered_rules_data['created_by'].str.contains(search_created_by, case=False)]
    if search_status:
        filtered_rules_data = filtered_rules_data[filtered_rules_data['status'].str.contains(search_status.strip(), case=False)]
    if search_modified_on:
        try:
            search_modified_on_date = datetime.strptime(search_modified_on, '%Y-%m-%d').date()
            filtered_rules_data = filtered_rules_data[
                pd.to_datetime(filtered_rules_data['modified_on'], errors='coerce').dt.date == search_modified_on_date]
        except ValueError:
            pass
    if search_modified_by:
        filtered_rules_data = filtered_rules_data[
            filtered_rules_data['modified_by'].str.contains(search_modified_by.strip(), case=False)]

    return filtered_rules_data

    # Debugging output to verify filtered data
@rules_watchlist_routes.route('/rules_watchlist/sys', methods=['GET', 'POST'])
def submit_form():
    username = session.get('username')  # Retrieve username from session
    if not username:
        return redirect(url_for('LoginPage'))  # Redirect to login if session is not set

    if request.method == 'POST':
        data = request.get_json()
        sliderbarValue = data.get('sliderbarValue', 0)  # Default to 0 if sliderbarValue is missing
        ruleSwitchValue = 1 if data.get('ruleSwitchValue') == 1 else 0
        aiSwitchValue = 1 if data.get('aiSwitchValue') == 1 else 0

        # Assuming 'conn' is your database connection object
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO form_data (slider_value, ruleswitch, aiswitch)
            VALUES (?, ?, ?)
        ''', (sliderbarValue,ruleSwitchValue, aiSwitchValue))

        conn.commit()
        cursor.close()

    # Fetch roles_data and latest data after inserting into the database
    rules_data = rule_manager.df.to_dict('records')
    latest_data = get_latest_row()  # Assuming get_latest_row() fetches the latest data from the database
    return render_template('rules.html', latest=latest_data, rules=rules_data, user=username)

@rules_watchlist_routes.route('/rules_watchlist/rules', defaults={'subpath': ''}, methods=['GET', 'POST'])
@rules_watchlist_routes.route('/rules_watchlist/rules/<path:subpath>', methods=['GET', 'POST'])
def rules(subpath):
    # page = int(request.args.get('page', 1))
    # per_page = 10
    options = get_options_from_db()
    operator = options['operator']
    channel = options['channel']
    columnname=options['columnname']
    userdetails=session.get('userdetails')
    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))  # Redirect to login if session is not set
    rules_data = rule_manager.get_rules()
    rules_data = extract_search_parameters(rules_data)
    if request.method == 'POST' and subpath == '':
        # Handle form submission to create rule
        column_name = request.form['column_name']
        operator = request.form['operator']
        value = request.form['value']
        allpre = request.form['allpre']
        channel = request.form['channel']

        # Handle rule creation and validation
        message = rule_manager.create_rule(channel, column_name, operator, value, allpre, username)
        if type(message) is not int:

            return render_template('rules.html', rules=rule_manager.df.to_dict('records'), user=username,
                                   userdetails=userdetails,message=message)


        inAlert({'AlertCategory': 'rule_Addition', 'NavLink': '/rules_watchlist/rules/pending',
                 'Description':username+ '(Maker) added the rule', 'is_seen': 0,
                 'to_whom': 3,
                 'ObjId': message},'group')
    if subpath == 'pending':
        objid = None
        if request.method == 'POST':
            objid = int(request.form['objid'])
            upAlert(int(request.form['altid']))
            return redirect(url_for('rules_watchlist_routes.rules', subpath=subpath, objid=objid))
        # pending_rules_data=rules_data[rules_data['appAction']=='Pending'].to_dict('records')
        # return render_template('rules.html', rules=pending_rules_data,userdetails=userdetails, user=username ,action=subpath,objid=objid)
        pending_rules_data = rules_data[rules_data['appAction'] == 'Pending'].to_dict('records')
        return render_template('rules.html', rules=pending_rules_data, userdetails=userdetails, user=username,
                               action=subpath, objid=objid, latest=get_latest_row(),operator=operator,channel=channel,columnname=columnname)
    elif subpath == 'declined' :
        objid = None
        if request.method == 'POST':
            objid = int(request.form['objid'])
            upAlert(int(request.form['altid']))
        Approved_rules_data = rules_data[rules_data['appAction'] == 'Declined'].to_dict('records')

        return render_template('rules.html', rules=Approved_rules_data,userdetails=userdetails, user=username,action=subpath,objid=objid, latest=get_latest_row(),operator=operator,channel=channel,columnname=columnname)

    elif subpath == 'approved' :
        objid = None
        if request.method == 'POST':
            objid = int(request.form['objid'])
            upAlert(int(request.form['altid']))
            return redirect(url_for('rules_watchlist_routes.rules', subpath=subpath, objid=objid))
        Approved_rules_data = rules_data[rules_data['appAction'] == 'Approved'].to_dict('records')
        return render_template('rules.html', rules=Approved_rules_data,userdetails=userdetails, user=username,action=subpath,objid=objid,operator=operator,channel=channel,columnname=columnname, latest=get_latest_row())

    elif subpath == '':
        # Handle the default rules page
        Approved_rules_data = rules_data[rules_data['appAction'] == 'Approved'].to_dict('records')
        return render_template('rules.html', rules=Approved_rules_data,userdetails=userdetails, user=username,action=subpath, latest=get_latest_row(),operator=operator,channel=channel,columnname=columnname)



@rules_watchlist_routes.route('/rules_watchlist/update/<int:rule_id>', methods=['POST'])
def update_rule(rule_id):
    # Handle updating rule
    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))
    if 'action' in request.form and request.form['action'] == 'approved':
        rule_manager.update_rule(rule_id=rule_id,appstatus= 'Approved',modified_by=username,ActionTookby=username)
        inAlert({'AlertCategory': 'rule_Approved', 'NavLink': '/rules_watchlist/rules/approved',
                 'Description': username+' (Approver) approved the rule', 'is_seen': 0,
                 'to_whom': rule_manager.df[rule_manager.df['id'] == rule_id]['created_by'].values[0],
                 'ObjId': rule_id}, 'personal')
        return redirect(url_for('rules_watchlist_routes.rules',  subpath='pending',user=username))
    elif 'action' in request.form and request.form['action'] == 'alert':
        errmsg= inAlert({'AlertCategory': 'rule_alert', 'NavLink': '/rules_watchlist/rules/pending',
                 'Description': username+' (Maker) re-alert the rule', 'is_seen': 0,
                 'to_whom':3,
                 'ObjId': rule_id}, 'group')

        if errmsg:
            return redirect(url_for('rules_watchlist_routes.rules', subpath='pending', user=username,erromsg=errmsg))
        return redirect(url_for('rules_watchlist_routes.rules', subpath='pending', user=username))
    elif 'action' in request.form and request.form['action'] == 'RequestAgain':
        rule_manager.update_rule(rule_id=rule_id,appstatus= 'Pending',ActionTookby='',modified_by=username)
        inAlert({'AlertCategory': 'rule_Resent', 'NavLink': '/rules_watchlist/rules/pending',
                 'Description': username+' (Maker) resend the rule', 'is_seen': 0,
                 'to_whom':3,
                 'ObjId': rule_id}, 'group')
        return redirect(url_for('rules_watchlist_routes.rules',  subpath='declined',user=username))
    elif 'action' in request.form and request.form['action'] == 'declined':
        rule_manager.update_rule(rule_id=rule_id, appstatus='Declined' ,modified_by=username,ActionTookby=username)
        inAlert({'AlertCategory': 'rule_declined', 'NavLink': '/rules_watchlist/rules/declined',
                 'Description': username +'(Approver) declined the rule', 'is_seen': 0,
                 'to_whom': rule_manager.df[rule_manager.df['id'] == rule_id]['created_by'].values[0],
                 'ObjId': rule_id},'personal')
        return redirect(url_for('rules_watchlist_routes.rules', subpath='pending', user=username))
    elif 'action' in request.form and request.form['action'] == 'reupdate':
        channel = request.form['channel']
        column_name = request.form['column_name']
        operator = request.form['operator']
        value = request.form['value']
        rule_manager.update_rule(rule_id, channel, column_name, operator, value, username)
        return redirect(url_for('rules_watchlist_routes.rules', subpath='declined', user=username))
    else:
        channel = request.form['channel']
        column_name = request.form['column_name']
        operator = request.form['operator']
        value = request.form['value']
        rule_manager.update_rule(rule_id, channel, column_name, operator, value, username)
        return redirect(url_for('rules_watchlist_routes.rules', user=username))


@rules_watchlist_routes.route('/rules_watchlist/delete/<int:rule_id>', methods=['POST'])
def delete_rule(rule_id):
    # Handle deleting rule
    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))  # Redirect to login if session is not set
    rule_manager.delete_rule(rule_id, username)
    if 'action' in request.form and request.form['action'] == 'declined':
        return redirect(url_for('rules_watchlist_routes.rules',  subpath='declined',user=username))
    if 'action' in request.form and request.form['action'] == 'pending':
        return redirect(url_for('rules_watchlist_routes.rules',  subpath='pending',user=username))
    return redirect(url_for('rules_watchlist_routes.rules', user=username))


@rules_watchlist_routes.route('/rules_watchlist/toggle/<int:rule_id>', methods=['POST'])
def toggle_rule(rule_id):
    # Handle toggling rule status
    rule_manager.toggle_rule_status(rule_id)
    return redirect(url_for('rules_watchlist_routes.rules'))

# You can define other routes related to rules and watchlist similarly
