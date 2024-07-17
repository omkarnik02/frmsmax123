from flask import Blueprint, render_template, request, redirect, url_for, session
from app.mailConfiguration import configManager
import pandas as pd

config_manager = configManager(None,pd.read_csv('app/Mailconfig_data.csv'),pd.read_csv('app/delConfig.csv'))
configure_routes = Blueprint('configure_routes', __name__)

@configure_routes.route('/configure/configs', methods=['GET', 'POST'])
def configs():
    username = session.get('username')  # Retrieve username from session
    if not username:
        return redirect(url_for('login'))  # Redirect to login if session is not set

    if request.method == 'POST':
        # Handle form submission to create configuration
        Channel = request.form['Channel']
        AlertType = request.form['AlertType']
        EmailId = request.form['EmailId']

        # Handle configuration creation and validation
        message = config_manager.create_config(Channel, AlertType, EmailId)
        if message:
            return render_template('configure.html', configs=config_manager.df.to_dict('records'), user=username,
                                   message=message)
    config_data = config_manager.df.to_dict('records')
    return render_template('configure.html', configs=config_data, user=username)


@configure_routes.route('/configure/update/<int:conig_id>', methods=['POST'])
def update_config(conig_id):
    # Handle updating configuration
    AlertType = request.form['AlertType']
    EmailId = request.form['EmailId']
    Channel = request.form['Channel']

    # Handle configuration update and validation
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login if session is not set
    config_manager.update_config(conig_id, AlertType, EmailId, Channel, username)
    return redirect(url_for('configure_routes.configs', user=username))


@configure_routes.route('/configure/configs/delete/<int:conig_id>', methods=['POST'])
def delete_config(conig_id):
    # Handle configuration deletion
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login if session is not set
    config_manager.delete_config(conig_id, username)
    return redirect(url_for('configure_routes.configs', user=username))


@configure_routes.route('/configure/configs/toggle/<int:conig_id>', methods=['POST'])
def toggle_config(conig_id):
    # Handle toggling configuration status
    config_manager.toggle_config_status(conig_id)
    return redirect(url_for('configure_routes.configs'))