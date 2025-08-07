import pyodbc
import os
import logging
from typing import List, Dict, Any

class DatabaseClient:
    CREATE_TRAIN_SCHEDULES_TABLE_SQL = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='train_schedules' AND xtype='U')
        CREATE TABLE train_schedules (
            id INT IDENTITY(1,1) PRIMARY KEY,
            train_id NVARCHAR(50) NOT NULL,
            train_name NVARCHAR(50) NOT NULL,
            direction NVARCHAR(10) NOT NULL,
            departure_station NVARCHAR(100) NOT NULL,
            arrival_station NVARCHAR(100) NOT NULL,
            platform NVARCHAR(10) NOT NULL,
            scheduled_time DATETIME NOT NULL,
            actual_time DATETIME NOT NULL,
            delay_minutes INT DEFAULT 0,
            canceled TINYINT DEFAULT 0,
            current_status NVARCHAR(10) NOT NULL,
            last_updated DATETIME DEFAULT GETDATE()
        )
        """
    INSERT_TRAIN_SCHEDULE_RECORD_SQL = """
        INSERT INTO train_schedules (
            train_id, 
            train_name, 
            direction, 
            departure_station, 
            arrival_station, 
            platform, 
            scheduled_time, 
            actual_time, 
            delay_minutes, 
            canceled, 
            current_status,
            last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    REMOVE_ALL_SCHEDULE_RECORDS_SQL = "DELETE FROM train_schedules"
    RETRIEVE_TRAIN_SCHEDULES_SQL = """
        SELECT TOP (?)
            train_id, 
            train_name, 
            station_name, 
            direction, 
            departure_station, 
            arrival_station, 
            platform, 
            scheduled_time, 
            actual_time, 
            delay_minutes, 
            canceled, 
            status, 
            last_updated
        FROM train_schedules
        ORDER BY departure_station, scheduled_time
        """

    def __init__(self):
        self.connection_string = os.environ.get("DB_CONNECTION_STRING") 

    def get_connection(self):
        """Create and return a database connection."""
        try:
            logging.info("[DatabaseClient] Attempting to connect to the database")
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logging.error(f"[DatabaseClient] Database connection failed: {str(e)}")
            raise
        finally:
            logging.info("[DatabaseClient] Database connection established successfully") 

    def create_tables_if_not_exist(self):
        """
        Create the necessary tables if they don't exist.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(self.CREATE_TRAIN_SCHEDULES_TABLE_SQL)
                conn.commit()
                logging.info("[DatabaseClient] Tables created or verified successfully")
        except Exception as e:
            logging.error(f"[DatabaseClient] Error creating tables: {str(e)}")
            raise

    def clear_old_data(self):
        """
        Clear old data from the train_schedules table.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(self.REMOVE_ALL_SCHEDULE_RECORDS_SQL)
                deleted_rows = cursor.rowcount
                conn.commit()
                logging.info(f"[DatabaseClient] Cleared {deleted_rows} old records")
        except Exception as e:
            logging.error(f"[DatabaseClient] Error clearing old data: {str(e)}")
            raise

    def insert_schedules(self, schedules: List[Dict[str, Any]], clear_old_data: bool = True):
        """
        Insert new schedules into the database.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if clear_old_data:
                    cursor.execute(self.REMOVE_ALL_SCHEDULE_RECORDS_SQL)

                # Insert new data
                for schedule in schedules:
                    cursor.execute(
                        self.INSERT_TRAIN_SCHEDULE_RECORD_SQL,
                        (
                            schedule.get("train_id", ""),
                            schedule.get("train_name", ""),
                            schedule.get("direction", ""),
                            schedule.get("departure_station", ""),
                            schedule.get("arrival_station", ""),
                            schedule.get("platform", ""),
                            schedule.get("scheduled_time"),
                            schedule.get("actual_time"),
                            schedule.get("delay_minutes", 0),
                            schedule.get("canceled", 0),
                            schedule.get("current_status", ""),
                            schedule.get("last_updated", None),
                        ),
                    )

                conn.commit()
                logging.info(f"[DatabaseClient] Inserted {len(schedules)} schedule records successfully")
        except Exception as e:
            logging.error(f"[DatabaseClient] Error inserting schedules: {str(e)}")
            raise

    def get_latest_schedules(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve the latest schedules for a station.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(self.RETRIEVE_TRAIN_SCHEDULES_SQL, (limit,))

                columns = [column[0] for column in cursor.description]
                results = []

                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))

                return results
        except Exception as e:
            logging.error(f"[DatabaseClient] Error retrieving schedules: {str(e)}")
            raise
