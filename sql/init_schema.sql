CREATE TABLE train_schedules (
    id INT IDENTITY(1,1) PRIMARY KEY,
    station_name NVARCHAR(100) NOT NULL,
    train_id NVARCHAR(50) NOT NULL,
    vehicle NVARCHAR(50),
    platform NVARCHAR(10),
    destination NVARCHAR(100),
    scheduled_time DATETIME,
    actual_time DATETIME,
    delay_minutes INT DEFAULT 0,
    canceled TINYINT DEFAULT 0,
    status NVARCHAR(50),
    direction NVARCHAR(10),
    last_updated DATETIME DEFAULT GETDATE()
)