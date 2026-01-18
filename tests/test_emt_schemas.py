from datetime import datetime
from schemas.emt_schemas import EmtArrivalResponse


def test_emt_parsing():
    payload = {
        "code": "00",
        "description": "Success",
        "datetime": datetime.utcnow().isoformat(),
        "data": [
            {
                "Arrive": [
                    {
                        "line": "131",
                        "stop": "3216",
                        "isHead": "N",
                        "destination": "CAMPAMENTO",
                        "deviation": 0,
                        "bus": 1234,
                        "geometry": {"type": "Point", "coordinates": [40.0, -3.7]},
                        "estimateArrive": 357,
                        "DistanceBus": 1200,
                        "positionTypeBus": "REAL",
                    }
                ],
                "StopInfo": [],
                "ExtraInfo": [],
                "Incident": {},
            }
        ],
    }

    parsed = EmtArrivalResponse.model_validate(payload)
    assert parsed.code == "00"
    assert parsed.data[0].Arrive[0].line == "131"
    assert parsed.data[0].Arrive[0].estimateArrive == 357
