import azure.functions as func
import logging
import json
from function_app import app

@app.function_name(name="update-schedules")
@app.route(route="update-schedules", methods=["GET", "POST"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered Azure Function to fetch live schedules from iRail API and update them in the DB.
    """
    logging.info("[update-schedules] Started")

    try:
        #TODO: Implement the logic to fetch live schedules from iRail API
        # and update them in the database.
        
        # Return success response
        response_data = {"message": "Schedules updated successfully"}

        logging.info("[update-schedules] Completed")

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
