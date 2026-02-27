"""
Database Connection Manager
Handles MySQL database connection using mysql-connector-python
"""

import mysql.connector
from mysql.connector import Error


class Database:
    """Database connection singleton class"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database connection"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self, host='localhost', database='worklog_db', user='root', password=''):
        """
        Establish database connection
        
        Args:
            host: MySQL host (default: localhost)
            database: Database name (default: worklog_db)
            user: MySQL username (default: root)
            password: MySQL password (default: empty for XAMPP)
        
        Returns:
            connection object or None
        """
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(
                    host=host,
                    database=database,
                    user=user,
                    password=password
                )
                if self._connection.is_connected():
                    print(f"Successfully connected to MySQL database: {database}")
            return self._connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def get_connection(self):
        """Get the current database connection"""
        if self._connection and self._connection.is_connected():
            return self._connection
        else:
            return self.connect()
    
    def close(self):
        """Close the database connection"""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("Database connection closed")
    
    def execute_query(self, query, params=None):
        """
        Execute a single query (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            return False
    
    def fetch_one(self, query, params=None):
        """
        Fetch a single record
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            Single record or None
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """
        Fetch multiple records
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            List of records or empty list
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
    
    def get_last_insert_id(self):
        """Get the last inserted ID"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Error as e:
            print(f"Error getting last insert ID: {e}")
            return None


# Create a global database instance
db = Database()
