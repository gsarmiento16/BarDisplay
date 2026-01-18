from datetime import datetime
import logging

from schemas.emt_schemas import EmtArrivalResponse

logger = logging.getLogger("emt")


class EmtMadridService:
    def __init__(self, http_client, settings):
        self.http_client = http_client
        self.settings = settings

    async def get_arrival_bus(self, stop_id: str, line_arrive: str) -> EmtArrivalResponse:
        
        try:
            line_arrive = "131"
            #path = f"/v2/transport/busemtmad/stops/{stop_id}/arrives/{line_arrive}/"
            path = f"/v2/transport/busemtmad/stops/{stop_id}/arrives/:lineArrive/"
            headers = {"accessToken": self.settings.EMT_ACCESS_TOKEN}
            body = {
                "cultureInfo": "ES",
                "Text_StopRequired_YN": "N",
                "Text_EstimationsRequired_YN": "Y",
                "Text_IncidencesRequired_YN": "N",
                "DateTime_Referenced_Incidencies_YYYYMMDD": "year-month-day",
            }
            response = await self.http_client.post(path, headers=headers, json=body)
            payload = response.json()
            logger.info("emt response stop=%s line=%s status=%s payload=%s", stop_id, line_arrive, response.status_code, payload)
            print("emt response stop=%s line=%s status=%s payload=%s", stop_id, line_arrive, response.status_code, payload)
            #print(datetime.now().strftime("%Y-%m-%d"))
            return EmtArrivalResponse.model_validate(payload)
        except Exception as e:
            logger.error("Error fetching EMT arrivals for stop=%s line=%s: %s", stop_id, line_arrive, str(e))
            print("Error fetching EMT arrivals for stop=%s line=%s: %s", stop_id, line_arrive, str(e))
            raise
