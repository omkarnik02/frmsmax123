import time
from datetime import datetime
import pyodbc
from flask import Blueprint, render_template, redirect, url_for, session, request
from sqlalchemy import create_engine
from app.alertmanagement import AlertManager
import pandas as pd

alert_routes = Blueprint('alert_routes', __name__)

server = '172.25.57.117'
database = 'FRMS_AI'
username = 'sa'
password = 'P@ss1234'
Driver = '{SQL Server Native Client 11.0}'
engine = create_engine(
    f'mssql+pyodbc:///?odbc_connect=DRIVER={Driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)
connection_string = "DRIVER={SQL Server};SERVER=" + server + ";DATABASE=" + database + ";UID=" + username + ";PWD=" + password


@alert_routes.route('/alerts', methods=['GET'])
def alerts():
    username = session.get('username')
    userdetails = session.get('userdetails')

    if not username:
        return redirect(url_for('LoginPage'))

    search_id = request.args.get('search_id')
    search_alert_category = request.args.get('search_alert_category')
    search_created_on = request.args.get('search_created_on')
    search_visited = request.args.get('search_visited')
    search_object_id = request.args.get('search_object_id')

    alert_manager = AlertManager(engine, username, userdetails.get('Role'))
    alerts_data = alert_manager.get_alerts_for_user()

    if search_id:
        alerts_data = alerts_data[alerts_data['id'].astype(str).str.contains(search_id)]
    if search_alert_category:
        alerts_data = alerts_data[alerts_data['AlertCategory'].str.contains(search_alert_category, case=False)]
    if search_created_on:
        try:
            search_created_on_date = datetime.strptime(search_created_on, '%Y-%m-%d').date()
            alerts_data = alerts_data[
                pd.to_datetime(alerts_data['CreatedOn'], errors='coerce').dt.date == search_created_on_date]
        except ValueError:
            pass
    if search_visited:
        visited = '1' if search_visited.lower() == 'yes' else '0'
        alerts_data = alerts_data[alerts_data['is_seen'] == visited]
    if search_object_id:
        alerts_data = alerts_data[alerts_data['ObjId'].astype(str).str.contains(search_object_id)]

    alerts_list = alerts_data.to_dict('records')

    return render_template('alerts.html', alertsk=alerts_list, user=username)
def inAlert(alertdata,typeOfEntry):
    with pyodbc.connect(connection_string) as conn:
        if typeOfEntry == 'personal':
            cursor = conn.cursor()

            cursor.execute(f"SELECT id FROM UserMaster WHERE UserName = ?", alertdata['to_whom'])

            # Fetching all the results
            results = cursor.fetchall()

            # Extracting the ids into a list
            id_list = [row[0] for row in results]
            a=time.time()
            conn.execute(
                "INSERT INTO AlertConfig VALUES (?, ?, ?, ?, 0, ?, ?,?)",
                int(a), alertdata['AlertCategory'], alertdata['NavLink'], alertdata['Description'],
                str(id_list), alertdata['ObjId'],time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(a))
            )
        if typeOfEntry == 'group':
            cursor = conn.cursor()
            if alertdata['AlertCategory'] == 'rule_alert':
                cursor.execute(f"SELECT max(CreatedOn) FROM alertconfig WHERE ObjId= ? and AlertCategory=?", alertdata['ObjId'],alertdata['AlertCategory'])
                lastdate_str = cursor.fetchone()[0]
                if lastdate_str:
                    lastdate=time.mktime(time.strptime(lastdate_str, "%Y-%m-%d %H:%M:%S"))
                    currenttime = time.mktime(time.localtime(time.time()))
                    print(currenttime-lastdate)
                    if currenttime-lastdate < 1440*60:
                        remaining_time_seconds = 1440 * 60 - (currenttime-lastdate)
                        remaining_hours = int(remaining_time_seconds // 3600)
                        remaining_minutes = int((remaining_time_seconds % 3600) // 60)
                        return f"Alert has been raised in the last 24 hours. Please wait for {remaining_hours} hours and {remaining_minutes} minutes."

            a=time.time()
            # Executing the SQL query
            cursor.execute(f"SELECT id FROM UserMaster WHERE roleID = {alertdata['to_whom']}")

            # Fetching all the results
            results = cursor.fetchall()

            # Extracting the ids into a list
            id_list = [row[0] for row in results]

            conn.execute(
                "INSERT INTO AlertConfig VALUES (?, ?, ?, ?, 0, ?, ?,?)",
                int(a), alertdata['AlertCategory'], alertdata['NavLink'], alertdata['Description'],
                str(id_list), alertdata['ObjId'],time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(a))
            )






def upAlert(AlertID):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE AlertConfig SET [is_seen] = 1 WHERE id = ?", AlertID)
        conn.commit()