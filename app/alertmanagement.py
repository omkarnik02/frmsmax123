from flask import Flask
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

class AlertManager:
    def __init__(self, engine,username,role):
        self.engine = engine
        self.df = pd.read_sql(
            f"SELECT a.id, a.AlertCategory, a.NavLink, a.[Description], a.[is_seen], a.ObjId, a.CreatedOn, ROW_NUMBER() OVER(PARTITION BY a.ObjId ORDER BY a.CreatedOn desc) AS rank FROM AlertConfig a JOIN UserMaster u ON u.id IN (SELECT value FROM STRING_SPLIT(REPLACE(REPLACE(a.UserID, '[', ''), ']', ''), ',')) WHERE u.username = '{username}' ORDER BY a.CreatedOn desc",
            self.engine.connect())

    def get_alerts_for_user(self):
        return self.df

