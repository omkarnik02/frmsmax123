import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import time

app = Flask(__name__)


# Id	Channel	AlertType	EmailId	CreatedBy	ModifiedBy
class Config:
    def __init__(self, AlertType, EmailId, Channel, created_by):
        self.AlertType = AlertType
        self.EmailId = EmailId
        self.Channel = Channel
        self.created_on = datetime.now()
        self.created_by = created_by
        self.modified_on = ''
        self.modified_by = ''
        self.Id = int(time.time())
        self.status = 'Enabled'


class configManager:
    def __init__(self, user, df, del_df):
        self.user = user
        self.df = df
        self.deleted_df = del_df

    def create_config(self, Channel, AlertType, EmailId):
        existing_rule = self.df[
            (self.df['Channel'] == Channel) & (self.df['AlertType'] == AlertType) & (self.df['EmailId'] == EmailId)]
        if not existing_rule.empty:
            return "Rule with the same column, operator, and value already exists"

        config = Config(AlertType, EmailId, Channel, self.user)
        config_data = {
            'Id': config.Id,
            'Channel': config.Channel,
            'AlertType': config.AlertType,
            'EmailId': config.EmailId,
            'created_on': config.created_on,
            'created_by': config.created_by,
            'modified_on': '',
            'modified_by': '',
            'status': config.status
        }
        self.df = pd.concat([self.df, pd.DataFrame([config_data])], ignore_index=True)
        self.df.to_csv('app/Mailconfig_data.csv', index=False)

    def update_config(self, conig_id, AlertType=None, EmailId=None, Channel=None, modified_by=None):
        if conig_id in self.df['Id'].values:
            if AlertType:
                self.df.loc[self.df['Id'] == conig_id, 'AlertType'] = AlertType
            if EmailId:
                self.df.loc[self.df['Id'] == conig_id, 'EmailId'] = EmailId
            if Channel:
                self.df.loc[self.df['Id'] == conig_id, 'Channel'] = Channel
            if modified_by:
                self.df.loc[self.df['Id'] == conig_id, 'modified_by'] = modified_by

            self.df.loc[self.df['Id'] == conig_id, 'modified_on'] = datetime.now()
            self.df.to_csv('app/Mailconfig_data.csv', index=False)

    def delete_config(self, conig_id, deleted_by):
        if conig_id in self.df['Id'].values:
            deleted_row = self.df[self.df['Id'] == conig_id].copy()
            deleted_row['deleted_on'] = datetime.now()
            deleted_row['deleted_by'] = deleted_by
            self.deleted_df = pd.concat([self.deleted_df, deleted_row], ignore_index=True)
            self.df = self.df[self.df['Id'] != conig_id]
            self.deleted_df.to_csv('app/delConfig.csv', index=False)
            self.df.to_csv('app/Mailconfig_data.csv', index=False)

    def toggle_config_status(self, conig_id):
        if conig_id in self.df['Id'].values:
            current_status = self.df.loc[self.df['Id'] == conig_id, 'status'].iloc[0]
            new_status = 'Enabled' if current_status == 'Disabled' else 'Disabled'
            self.df.loc[self.df['Id'] == conig_id, 'status'] = new_status
            self.df.to_csv('app/Mailconfig_data.csv', index=False)

    def get_configs(self):
        # Return rules as a list of dictionaries
        return self.df.to_dict('records')



