# 🚆 Azure Train Schedules - Live Board System

A serverless Azure Functions application that fetches live train schedules from the iRail API and stores them in Azure SQL Database for creating a live departure/arrival board.

## 📋 Project Overview

This project implements a real-time train schedule system using Azure Functions to:
- Fetch live train data from the iRail API for both arrivals and departures
- Store the data in Azure SQL Database
- Automatically update schedules every hour (configurable via cron)
- Provide HTTP endpoint for manual data retrieval
- Support multiple stations simultaneously

## 🏗️ Architecture

### Azure Resources
- **Function App**: `func-train-schedules`
- **SQL Database**: `sqldb-train-schedules`
- **Storage Account**: Required for Azure Functions runtime

### Functions
1. **update_schedules** (HTTP Trigger): Manual fetch of live schedules for specified stations
2. **update_schedules_timer** (Timer Trigger): Automatic updates based on configurable cron schedule (default: every hour)

## 📁 Project Structure

```
af-belgium-train-schedules/
├── function_app.py          # Main Azure Functions app with HTTP and Timer triggers
├── utils/                   # Utility modules
│   ├── db_client.py         # Database operations and connection management
│   └── irail_client.py      # iRail API client with request handling
├── sql/                     # Database schema
│   └── init_schema.sql      # Table creation script
├── requirements.txt         # Python dependencies
├── host.json                # Function app configuration
├── local.settings.json      # Local development settings
├── assets/                  # Project assets and documentation
├── pbix/                    # Power BI dashboard files
└── screenshots/           # Documentation screenshots
```

## 🗄️ Database Schema

The application creates a `train_schedules` table with the following structure:

```sql
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
```

## 🚀 Deployment Instructions

### Prerequisites
- Azure subscription with Function App and SQL Database created
- Python 3.12+ for local development
- Azure Functions Core Tools (for local testing)

### Environment Variables
Configure these in your Function App settings:

```json
{
  "SQL_CONNECTION_STRING": "Driver={ODBC Driver 17 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=sqldb-train-schedules;Uid=<your-username>;Pwd=<your-password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
  "TRAIN_STATIONS": "Brussels-Central,Brussels-North,Brussels-South",
  "UPDATE_SCHEDULES_TIMER_CRON": "0 * * * * *"
}
```

### Deployment Steps

1. **Clone and prepare the project**:
   ```bash
   git clone https://github.com/albertopd/af-belgium-train-schedules.git
   cd af-belgium-train-schedules
   ```

2. **Deploy using Azure Portal**:
   - Zip the entire project folder
   - Go to your Function App in Azure Portal
   - Navigate to "Deployment Center"
   - Choose "Zip Deploy" and upload your zip file

3. **Or deploy using Azure CLI**:
   ```bash
   func azure functionapp publish func-train-schedules --python
   ```

## 🔧 Configuration

### Timer Schedule
The `update_schedules_timer` function runs every hour by default using the cron expression:
```
"schedule": "0 * * * * *"
```

To modify the schedule, set the `UPDATE_SCHEDULES_TIMER_CRON` environment variable.

### Station Configuration
Set the `TRAIN_STATIONS` environment variable to specify which stations to monitor (comma-separated):
```
"TRAIN_STATIONS": "Brussels-Central,Brussels-North,Brussels-South"
```

## 📡 API Usage

### Update Schedules (HTTP Trigger)

**Endpoint**: `https://func-train-schedules.azurewebsites.net/api/update_schedules`

**Parameters**:
- `stations` (optional): Comma-separated list of stations (defaults to `TRAIN_STATIONS` environment variable)

**Example**:
```
GET /api/update_schedules?stations=Brussels-Central,Brussels-North
```

**Response**:
```json
{
  "message": "Schedules updated successfully",
  "stations": ["Brussels-Central", "Brussels-North"],
  "arrival_schedules_counts": [15, 12],
  "departure_schedules_counts": [18, 14],
  "total_schedules": 59,
  "schedules": [...]
}
```

## 🔍 Monitoring

- View function execution logs in Azure Portal under "Functions" > "Monitor"
- Check Application Insights for detailed telemetry and performance metrics
- Monitor database connections and query performance in Azure SQL Database
- Set up alerts for function failures or database connection issues

## 🧪 Local Development

### Setup
1. **Install Azure Functions Core Tools**:
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Create Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure local settings**:
   - Copy `local.settings.json.example` to `local.settings.json`
   - Update the SQL connection string with your database credentials

4. **Run locally**:
   ```bash
   func start
   ```

### Testing
- **HTTP Function**: `http://localhost:7071/api/update_schedules`
- **Timer Function**: Will run automatically based on cron schedule when local runtime is active

## 📊 Data Flow

```
iRail API → Azure Function → Azure SQL Database → Live Board Display
     ↑              ↑              ↑                    ↑
  Live data    Serverless      Persistent          Real-time
               processing      storage             updates
```

1. **iRail API** provides live train schedule data for Belgian railway stations
2. **Azure Function** (Timer/HTTP triggers) fetches, processes, and normalizes the data
3. **Azure SQL Database** stores the processed schedules with timestamps and status information
4. **Live Board Display** consumes the stored data to show real-time departure/arrival information


## 🚨 Troubleshooting

### Common Issues

**1. Database Connection Failures**
- Verify SQL connection string format
- Check firewall rules allow Azure services
- Ensure database credentials are correct

**2. iRail API Timeouts**
- API may be temporarily unavailable
- Check logs for specific error messages
- Consider implementing retry logic

**3. Function Not Triggering**
- Verify timer trigger cron expression
- Check Function App is running (not stopped)
- Review consumption plan limits

**4. Data Not Updating**
- Check if `clear_old_data()` is working correctly
- Verify station names match iRail API format (use exact station names)
- Monitor for parsing errors in logs
- Ensure `TRAIN_STATIONS` environment variable is properly set

### Debug Commands
```bash
# Check function status
func azure functionapp list-functions func-train-schedules

# View recent logs
func azure functionapp logstream func-train-schedules

# Test HTTP function locally
curl "http://localhost:7071/api/update_schedules?stations=Brussels-Central"
```

## 🔮 Future Enhancements

### Suggested Features
- [ ] Historical data retention and analysis
- [ ] Real-time notifications for delays
- [ ] Train route mapping with connections
- [ ] Multi-language support for station names

### Suggested Improvements
- [ ] Implement retry logic with exponential backoff
- [ ] Add data validation and sanitization
- [ ] Create unit tests for core functions
- [ ] Add authentication for HTTP endpoints
- [ ] Implement caching layer (Redis) for frequently accessed data

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👥 Contributors

- [Alberto Pérez Dávila](https://github.com/albertopd)