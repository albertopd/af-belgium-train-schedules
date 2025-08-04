import azure.functions as func
import logging
import json
import os
from function_app import app
from utils.irail_client import IRailClient

@app.function_name(name="update-schedules")
@app.route(route="update-schedules", methods=["GET", "POST"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered Azure Function to fetch live schedules from iRail API and update them in the DB.
    """
    logging.info("[update-schedules] Started")

    try:
        stations = (req.params.get("stations") or os.environ.get("STATIONS", "Brussels-Central")).split(",")
        if not stations:
            return func.HttpResponse(
                json.dumps({"error": "No stations provided"}),
                status_code=400,
                mimetype="application/json",
            )
                
        irail_client = IRailClient()

        all_schedules = []

        for station in stations:
            for direction in ["departure", "arrival"]:
                # Log the direction being processed
                logging.info(f"[update-schedules] Fetching {direction} schedules for station: {station}")

                # Fetch schedules from iRail API
                schedules = irail_client.get_schedules(station, direction)
                
                if schedules:
                    all_schedules.extend(schedules)
                else:
                    logging.warning(f"[update-schedules] No schedules found in the response for {direction} at station: {station}")        

        # Return success response
        response_data = {
            "message": "Schedules updated successfully",
            "stationS": stations,
            "schedules_count": len(all_schedules),
            "schedules": all_schedules #[:10]  # Return first 10 for preview
        }

        return func.HttpResponse(
            json.dumps(response_data, default=str),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"[update-schedules] ERROR: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json",
        )
    
    finally:
        logging.info("[update-schedules] Completed")
