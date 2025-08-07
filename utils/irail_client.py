import requests
import logging
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional


class IRailClient:
    BASE_URL = "https://api.irail.be"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Azure-Train-Schedules/1.0'", "Accept": "application/json"}
        )

    def get_schedules(
        self,
        station: str,
        direction: str = "departure",
        lang: str = "en",
        alerts: bool = False,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get schedules for a specific station.

        Args:
            station: Station name (e.g., "Brussels-Central")
            direction: "departure" or "arrival"
            lang: Language code ("en", "fr", "nl", "de")
            alerts: Include alerts in response

        Returns:
            Dictionary containing the liveboard data or None if failed
        """
        endpoint = f"{self.BASE_URL}/liveboard/"

        params = {
            "station": station,
            "arrdep": direction,
            "format": "json",
            "lang": lang,
            "alerts": "true" if alerts else "false",
        }

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            logging.info(f"[IRailClient] Successfully fetched schedules for {station}")

            return self.__parse_liveboard_data(data, station, direction)

        except requests.exceptions.RequestException as e:
            logging.error(
                f"[IRailClient] Error fetching schedules for {station}: {str(e)}"
            )
            return None

        except json.JSONDecodeError as e:
            logging.error(f"[IRailClient] Error parsing JSON response: {str(e)}")
            return None

    def __parse_liveboard_data(
        self, liveboard_data: Dict[str, Any], station: str, direction: str = "departure"
    ) -> List[Dict[str, Any]]:
        """
        Parse the liveboard JSON data into a structured format.

        Args:
            liveboard_data: Raw JSON data from iRail API
            direction: "departure" or "arrival"

        Returns:
            List of dictionaries containing parsed schedule data
        """
        if not liveboard_data:
            logging.warning("[IRailClient] Invalid live board data structure")
            return []

        schedules = liveboard_data.get(f"{direction}s", {}).get(direction, [])

        parsed_schedules = []

        for schedule in schedules:
            try:
                # Parse timestamps
                scheduled_time = self._parse_timestamp(schedule.get("time", "0"))
                delay = int(schedule.get("delay", "0"))
                actual_time = (
                    scheduled_time + timedelta(seconds=delay)
                    if scheduled_time and delay > 0
                    else scheduled_time
                )

                # Extract vehicle information
                vehicle_id = schedule.get("vehicle")
                vehicle_info = schedule.get("vehicleinfo", {})
                vehicle_name = vehicle_info.get("shortname", vehicle_id.split(".")[-1])

                # Extract platform
                platform = schedule.get("platform", "")

                # Extract station
                if direction == "departure":
                    departure_station = station
                    arrival_station = schedule.get("station", "")
                else:
                    departure_station = schedule.get("station", "")
                    arrival_station = station

                # Check if canceled
                canceled = 1 if schedule.get("canceled", "0") == "1" else 0

                schedule_entry = {
                    "train_id": vehicle_id,
                    "train_name": vehicle_name,
                    "direction": direction,
                    "departure_station": departure_station,
                    "arrival_station": arrival_station,
                    "platform": "" if platform == "?" else platform,
                    "scheduled_time": scheduled_time,
                    "actual_time": actual_time,
                    "delay_minutes": (
                        delay // 60 if delay > 0 else 0
                    ),  # Convert seconds to minutes
                    "canceled": canceled,
                    "current_status": (
                        "Canceled"
                        if canceled
                        else ("Delayed" if delay > 0 else "On Time")
                    ),
                }

                parsed_schedules.append(schedule_entry)

            except Exception as e:
                logging.warning(f"[IRailClient] Error parsing schedule entry: {str(e)}")
                continue

        logging.info(f"[IRailClient] Parsed {len(parsed_schedules)} schedule entries")
        return parsed_schedules

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        Parse iRail timestamp format to datetime object.

        Args:
            timestamp_str: Timestamp string from iRail API

        Returns:
            datetime object or None if parsing fails
        """
        try:
            # iRail timestamps are in Unix timestamp format
            timestamp = int(timestamp_str)

            # Convert to UTC
            dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)

            # Convert to local Belgium time (with DST awareness)
            dt_belgium = dt_utc.astimezone(ZoneInfo("Europe/Brussels"))
            return dt_belgium

        except (ValueError, TypeError) as e:
            logging.warning(
                f"[IRailClient] Error parsing timestamp '{timestamp_str}': {str(e)}"
            )
            return None
