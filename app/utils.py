from datetime import datetime
import json

from motor.motor_asyncio import AsyncIOMotorClient


SELECTED_DT_FORMATS = {
    'hour': '%Y-%m-%d %H',
    'day': '%Y-%m-%d',
    'week': '%Y-%U',
    'month': '%Y-%m',
}
DT_FRMT = "%Y-%m-%dT%H:%M:%S"


async def calculate_sum_all_payments(
    dt_from: str,
    dt_upto: str,
    group_type: str,
    client: AsyncIOMotorClient,
) -> dict[str, list]:
    collection = client.sampleDB.sample_collection
    pipeline = [
        {
            '$match': {
                'dt': {
                    '$gte': datetime.strptime(dt_from, DT_FRMT),
                    '$lte': datetime.strptime(dt_upto, DT_FRMT),
                },
            },
        },
        {
            '$group': {
                '_id': {
                    '$dateToString': {
                        'date': '$dt',
                        'format': SELECTED_DT_FORMATS[group_type],
                    },
                },
                'value': {'$sum': '$value'},
            },
        },
        {
            '$project': {
                '_id': 0,
                'label': '$_id',
                'amount': '$value',
            }
        }
    ]
    cursor = collection.aggregate(pipeline)
    result = [doc async for doc in cursor]
    dataset = [entry['amount'] for entry in result]
    labels = [
        datetime.strptime(entry['label'], SELECTED_DT_FORMATS[group_type])
        .replace(day=1, hour=0, minute=0, second=0)
        .strftime(DT_FRMT)
        for entry in result
    ]
    return json.dumps({"dataset": dataset, "labels": labels})
