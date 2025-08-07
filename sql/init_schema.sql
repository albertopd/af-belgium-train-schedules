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