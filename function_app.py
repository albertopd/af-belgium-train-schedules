from datetime import datetime
from zoneinfo import ZoneInfo
import azure.functions as func
import logging
import json
import os
from utils.irail_client import IRailClient
from utils.db_client import DatabaseClient

app = func.FunctionApp()


def update_schedules_logic(stations):
    """
    Core logic to fetch live schedules from iRail API and update DB.
    Returns detailed info about the update process.
    """
    irail_client = IRailClient()
    db_client = DatabaseClient()

    # Ensure database tables exist
    db_client.create_tables_if_not_exist()

    arrival_schedules_counts = [0 for _ in stations]
    departure_schedules_counts = [0 for _ in stations]
    all_schedules = []

    for idx, station in enumerate(stations):
        for direction in ["arrival", "departure"]:
            logging.info(
                f"[update_schedules_logic] Fetching {direction} schedules for station: {station}"
            )

            schedules = irail_client.get_schedules(station, direction)

            if schedules:
                if direction == "arrival":
                    arrival_schedules_counts[idx] = len(schedules)
                else:
                    departure_schedules_counts[idx] = len(schedules)

                all_schedules.extend(schedules)
            else:
                logging.warning(
                    f"[update_schedules_logic] No {direction} schedules found for station '{station}'"
                )

    if all_schedules:
        logging.info(f"[update_schedules_logic] Found {len(all_schedules)} schedules")

        # Clear old data before inserting new schedules
        logging.info("[update_schedules_logic] Clearing old schedule data")
        db_client.clear_old_data()

        # Add last updated timestamp to each schedule
        current_timestamp = datetime.now(tz=ZoneInfo("Europe/Brussels"))
        for schedule in all_schedules:
            schedule["last_updated"] = current_timestamp

        # Insert new schedules into the database
        logging.info(
            "[update_schedules_logic] Inserting new schedules into the database"
        )
        db_client.insert_schedules(all_schedules)

    return {
        "stations": stations,
        "arrival_schedules_counts": arrival_schedules_counts,
        "departure_schedules_counts": departure_schedules_counts,
        "total_schedules": len(all_schedules),
        "schedules": all_schedules,
    }


@app.function_name(name="update_schedules")
@app.route(route="update_schedules", methods=["GET"])
def update_schedules(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered function to update schedules.
    Takes 'stations' from query params or environment variables.
    """
    logging.info("[update_schedules] Started")

    try:
        stations = (
            req.params.get("stations")
            or os.environ.get("TRAIN_STATIONS", "Brussels-Central")
        ).split(",")

        if not stations:
            return func.HttpResponse(
                json.dumps({"error": "No stations provided"}),
                status_code=400,
                mimetype="application/json",
            )

        result = update_schedules_logic(stations)

        response_data = {
            "message": "Schedules updated successfully",
            **result,
        }

        return func.HttpResponse(
            json.dumps(response_data, default=str),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"[update_schedules] ERROR: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
        )

    finally:
        logging.info("[update_schedules] Completed")


def register_timer_trigger():
    cron_schedule = os.environ.get("UPDATE_SCHEDULES_TIMER_CRON", "0 * * * * *")

    @app.function_name(name="update_schedules_timer")
    @app.schedule(
        schedule=cron_schedule,
        arg_name="timer",
        run_on_startup=False,
        use_monitor=True,
    )
    def update_schedules_timer(timer: func.TimerRequest) -> None:
        """
        Timer-triggered function to update schedules every 15 minutes.
        """
        logging.info("[update_schedules_timer] Timer trigger started")

        try:
            logging.info(f"[update_schedules_timer] Timer trigger fired")

            stations = os.environ.get("TRAIN_STATIONS", "Brussels-Central").split(",")
            if not stations:
                logging.error(
                    "[update_schedules_timer] No stations provided in environment variable"
                )
                return

            update_schedules_logic(stations)

        except Exception as e:
            logging.error(f"[update_schedules_timer] ERROR: {str(e)}")

        finally:
            logging.info("[update_schedules_timer] Timer trigger completed")


register_timer_trigger()