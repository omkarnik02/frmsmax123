import csv
from flask import render_template, request, redirect, url_for, session
from app import app
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from app.configure_route import configure_routes
from app.rules_watchlist_route import rules_watchlist_routes
from app.alert_route import alert_routes, inAlert

app.secret_key = b'\x08\xa5\xb7\xb42br\xd0\xa0\xf0\xc7f\xbe\xaew^\xf5\x89\x03\xbb\xfe\xd9\xcd\xc0'
from app.roles_route import roles_routes



# Register roles_routes blueprint


server = '172.25.57.117'
database = 'FRMS_AI'
username = 'sa'
password = 'P@ss1234'
Driver='{SQL Server Native Client 11.0}'
engine = create_engine(
    'mssql+pyodbc:///?odbc_connect=DRIVER={SQL Server Native Client 11.0};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
conn = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)


global rule_manager
# global role_manager
# rule_manager = RuleManager(None, pd.read_csv('app/rules.csv'), pd.read_csv('app/delRules.csv'))
# role_manager = RoleManager(None,rolesdf, pd.read_csv('app/delroles.csv'),rolesmaster,ClearanceMaster,engine)
# config_manager = configManager(None,pd.read_csv('app/Mailconfig_data.csv'),pd.read_csv('app/delConfig.csv'))

@app.route('/', methods=['GET', 'POST'])
def LoginPage():
    if request.method == 'POST':
        username1 = request.form['username']
        password2 = request.form['password']
        cursor = conn.cursor()

        cursor.execute('''select um.*,rm.Role,cm.sections from usermaster um
                left join RoleMaster rm on um.RoleID=rm.RoleID
                left join ClearanceMaster cm on um.ClearanceID=cm.ClearanceID WHERE um.UserName COLLATE Latin1_General_CS_AS = ? AND um.Passwords COLLATE Latin1_General_CS_AS = ?''', (username1, password2))
        row = cursor.fetchone()
        print(row)


        if row:
            status = row[6]  
            if status == 'Inactive':
                error = 'User status is inactive. Kindly ask the admin to make it active.'
                return render_template('LoginPage.html', error=error)
            elif status == 'Active':

                session['userdetails'] ={'userid': row[0],'username': row[1], 'email': row[2], 'Role': row[9], 'Clearance': row[10], 'Passwords': row[5]}
                session['username'] = row[1]
                return redirect(url_for('Home', userdetails=session['userdetails']))
            else:
                error = 'Unknown status. Please contact support.'
                return render_template('LoginPage.html', error=error)
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('LoginPage.html', error=error)

    return render_template('LoginPage.html')


@app.route('/Home')
def Home():
    username = session.get('username')
    if not username:
        return redirect(url_for('LoginPage'))
    return render_template('Home.html', user=username)
    
@app.route('/signout')
def sign_out():
    session.pop('username', None)  
    return render_template('LoginPage.html')


@app.route('/analysis')
def analysis():
    username = session.get('username')  # Retrieve username from session
    if not username:
        return redirect(url_for('LoginPage'))
    return render_template('analysis.html', user=username)

@app.route('/cim')
def cim():
    username = session.get('username')  # Retrieve username from session
    if not username:
        return redirect(url_for('LoginPage'))
    return render_template('CIM.html', user=username)



@app.route('/testing_form')
def testing_form():
    username = session.get('username')  # Retrieve username from session
    if not username:
        return redirect(url_for('LoginPage'))
    return render_template('testing_form.html', user=username)
                
    
@app.route('/analysis/analysedetails', methods=['GET', 'POST'])
def analysedetails():
    username = session.get('username')  # Retrieve username from session
    if not username:
        return redirect(url_for('LoginPage'))
    if request.method == 'POST':
        txnid = request.form['TxnID']
        CardNumber = request.form['CardNumber']
        Channel = request.form['channel']
        fromDate = request.form['fromdate']
        todate = request.form['todate']
        mcc = request.form['mcc']
        print(CardNumber)
        prevs = pd.read_csv('app/FRMSTxns.csv')
        if Channel:
            prevs = prevs[prevs['Channel'] == Channel]
        if mcc:
            prevs = prevs[prevs['MCC'] == int(mcc)]
        if fromDate:
            prevs['DateTime'] = pd.to_datetime(prevs['DateTime'])
            prevs = prevs[(prevs['DateTime'] >= fromDate)]
        if todate:
            prevs['DateTime'] = pd.to_datetime(prevs['DateTime'])
            prevs = prevs[prevs['DateTime'] <= todate]
        if txnid:
            prevs['txnID'] = prevs['txnID'].astype(int).astype(str)
            prevs = prevs[prevs['txnID'] == txnid].to_dict('records')
            return render_template('analysis.html', prevs=prevs, user=username)
        if CardNumber:
            prevs['CardNumber'] = prevs['CardNumber'].astype(int).astype(str)
            print(prevs)
            prevs=prevs[prevs['CardNumber'] == CardNumber].to_dict('records')
            return render_template('analysis.html',prevs=prevs,user=username)
        prevs=prevs.to_dict('records')
    return render_template('analysis.html',prevs=prevs,user=username)



app.register_blueprint(rules_watchlist_routes)
app.register_blueprint(roles_routes)
app.register_blueprint(configure_routes)
app.register_blueprint(alert_routes)


