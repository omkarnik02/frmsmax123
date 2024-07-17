import pandas as pd
from flask import Flask, session
from datetime import datetime
import time

app = Flask(__name__)


def log_event(role_id, UserName, event_description, navlink, obj_id,conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='loginfo' AND xtype='U')
                CREATE TABLE loginfo(
                    id VARCHAR(255),
                    logtime DATETIME,
                    [user] VARCHAR(255),
                    events VARCHAR(255),
                    navlink VARCHAR(255),
                    obj_id VARCHAR(255)
                )
            ''')

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO loginfo(id, logtime, [user], events, navlink, obj_id ) VALUES (?, ?, ?, ?, ?, ?)",
                       (role_id, now, UserName, event_description, navlink, obj_id))

        conn.commit()
    except Exception as e:
        print(f"An error occurred while logging event: {str(e)}")


class Rule:
    def __init__(self, channel, column_name, operator, value, allpre, created_by):
        self.column_name = column_name
        self.operator = operator
        self.channel = channel
        self.value = value
        self.allowprevent=allpre
        self.created_on = datetime.now()
        self.created_by = created_by
        self.modified_on = ''
        self.modified_by = ''
        self.id = int(time.time())
        self.status = 'Enabled'
        self.appAction = 'Pending'
        self.appAprrovedby = ''



class RuleManager:
    def __init__(self, user, df, del_df, engine,conn):
        self.user = user
        self.df = df
        self.deleted_df = del_df
        self.engine = engine
        self.conn = conn



    def save_to_database(self,savedf):
        self.engine.connect()
        savedf.to_sql(name='RuleTable', con=self.engine, if_exists='replace', index=False)
        self.engine.dispose()

    def create_rule(self, channel, column_name, operator, value, allpre, created_by):
        existing_rule = self.df[
            (self.df['column_name'] == column_name) & (self.df['operator'] == operator) & (self.df['value'] == value)]
        if not existing_rule.empty:
            return "Rule with the same column, operator, and value already exists"

        rule = Rule(channel, column_name, operator, value, allpre, created_by)
        rule_data = {
            'id': rule.id,
            'channel': rule.channel,
            'column_name': rule.column_name,
            'operator': rule.operator,
            'value': rule.value,
            'allowprevent': rule.allowprevent,
            'created_on': rule.created_on,
            'created_by': rule.created_by,
            'modified_on': '',
            'modified_by': '',
            'status': rule.status,
            'appAction': rule.appAction,
            'appAprrovedby': rule.appAprrovedby
        }
        self.df = pd.concat([self.df, pd.DataFrame([rule_data])], ignore_index=True)
        self.save_to_database(self.df)
        id = f'log_{int(time.time())}'
        navlink = '/rules_watchlist/rules'
        obj_id = f'rule_{rule.id}'
        log_event(id, session.get('username'), f'{session.get("username")} created rule ', navlink, obj_id,self.conn)
        return rule.id

    def update_rule(self, rule_id, channel=None, column_name=None, operator=None, value=None, modified_by=None,
                    appstatus=None, ActionTookby=None):
        if rule_id in self.df['id'].values:
            if channel:
                self.df.loc[self.df['id'] == rule_id, 'channel'] = channel
            if column_name:
                self.df.loc[self.df['id'] == rule_id, 'column_name'] = column_name
            if operator:
                self.df.loc[self.df['id'] == rule_id, 'operator'] = operator
            if value:
                self.df.loc[self.df['id'] == rule_id, 'value'] = value
            if modified_by:
                self.df.loc[self.df['id'] == rule_id, 'modified_by'] = modified_by
            if appstatus:
                self.df.loc[self.df['id'] == rule_id, 'appAction'] = appstatus
            if ActionTookby:
                self.df.loc[self.df['id'] == rule_id, 'ActionTookby'] = ActionTookby

            self.df.loc[self.df['id'] == rule_id, 'modified_on'] = datetime.now()
            self.save_to_database(self.df)
            id = f'log_{int(time.time())}'
            navlink = '/rules_watchlist/rules'
            obj_id = f'rule_{rule_id}'
            log_event(
                id,
                session.get('username'),
                f' rule {appstatus if appstatus is not None else "updated"} by {session.get("username")}',
                navlink,
                obj_id,
                self.conn
            )
    def delete_rule(self, rule_id, deleted_by):
        if rule_id in self.df['id'].values:
            deleted_row = self.df[self.df['id'] == rule_id].copy()
            deleted_row['deleted_on'] = datetime.now()
            deleted_row['deleted_by'] = deleted_by
            self.deleted_df = pd.concat([self.deleted_df, deleted_row], ignore_index=True)
            self.df = self.df[self.df['id'] != rule_id]
            self.deleted_df.to_sql(name='Deleted_RuleTable', con=self.engine, if_exists='replace', index=False)
            self.save_to_database(self.df)
            id = f'log_{int(time.time())}'
            navlink = '/rules_watchlist/rules'
            obj_id = f'rule_{rule_id}'
            log_event(id, session.get('username'), f'{session.get("username")} deleted rule ', navlink, obj_id,self.conn)


    def toggle_rule_status(self, rule_id):
        if rule_id in self.df['id'].values:
            current_status = self.df.loc[self.df['id'] == rule_id, 'status'].iloc[0]
            new_status = 'Enabled' if current_status == 'Disabled' else 'Disabled'
            self.df.loc[self.df['id'] == rule_id, 'status'] = new_status
            self.save_to_database(self.df)
            id = f'log_{int(time.time())}'
            navlink = '/rules_watchlist/rules'
            obj_id = f'rule_{rule_id}'
            log_event(id, session.get('username'),f'{session.get("username")} change role status from {current_status} to {new_status} ', navlink, obj_id,self.conn)

    def get_rules(self):
        self.engine.connect()
        query = "SELECT * FROM RuleTable"
        self.df = pd.read_sql(query, con=self.engine)


        return self.df
