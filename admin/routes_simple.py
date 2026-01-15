# admin/routes_simple.py (temporary test file)
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import admin_bp

@admin_bp.route('/')
@login_required
def dashboard():
    return "Admin Dashboard - Working!"

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    return "Admin Login Page - Working! <a href='/admin/'>Go to Dashboard</a>"

@admin_bp.route('/logout')
def logout():
    return "Logout - Working!"