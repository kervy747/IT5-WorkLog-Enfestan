"""
Work Log - Employee Attendance Monitoring System
Main Application Entry Point

"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from views.login_view import LoginView
from views.admin_dashboard_view import AdminDashboardView
from views.employee_dashboard_view import EmployeeDashboardView


class WorkLogApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Work Log")
        self.app.setOrganizationName("Work Log Inc.")
        
        # Load stylesheet
        self.load_stylesheet()
        
        # Current dashboard window
        self.dashboard = None
        
        # Show login window
        self.show_login()
    
    def load_stylesheet(self):
        """Load QSS stylesheet for the application"""
        stylesheet_path = os.path.join(
            os.path.dirname(__file__), 
            'styles', 
            'theme.qss'
        )
        
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                self.app.setStyleSheet(stylesheet)
                print("Stylesheet loaded successfully")
        else:
            print(f"Warning: Stylesheet not found at {stylesheet_path}")
    
    def show_login(self):
        """Show login window"""
        self.login_window = LoginView()
        self.login_window.clear_inputs()  # Clear previous inputs
        self.login_window.login_successful.connect(self.handle_login_success)
        self.login_window.show()
    
    def handle_login_success(self, user_data, role):
        """
        Handle successful login
        
        Args:
            user_data: Dictionary containing user information
            role: User role (Admin or Employee)
        """
        print(f"Login successful: {user_data['full_name']} as {role}")
        
        # Hide login window
        self.login_window.hide()
        
        # Close any existing dashboard
        if self.dashboard:
            self.dashboard.close()
        
        # Open appropriate dashboard based on role
        if role == "Admin":
            self.dashboard = AdminDashboardView(user_data)
        else:  # Employee
            self.dashboard = EmployeeDashboardView(user_data)
        
        # Show dashboard
        self.dashboard.show()
        
        # When dashboard closes, show login again
        self.dashboard.finished.connect(self.on_dashboard_closed)
    
    def on_dashboard_closed(self):
        """Handle dashboard closed - return to login"""
        self.show_login()
    
    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    
    
    print("=" * 60)
    print("Work Log - Employee Attendance Monitoring System")
    print("=" * 60)
    print("\nStarting application...")
    print("\nDefault Login Credentials:")
    print("  Admin    - Username: admin, Password: password123")
    print("  Employee - (assign role via Admin > User Accounts)")
    print("\nMake sure MySQL database is running (XAMPP)")
    print("=" * 60)
    print()
    
    # Check database connection
    try:
        from models.database import db
        connection = db.connect()
        if connection:
            print("[OK] Database connection successful")
        else:
            print("[FAIL] Database connection failed!")
            print("  Please check:")
            print("  1. XAMPP MySQL is running")
            print("  2. Database 'worklog_db' exists")
            print("  3. schema.sql has been imported")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Database error: {e}")
        print("\nPlease ensure:")
        print("1. XAMPP is installed and MySQL is running")
        print("2. Run schema.sql to create database")
        print("3. Install: pip install mysql-connector-python")
        sys.exit(1)
    
    # Create and run application
    app = WorkLogApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
