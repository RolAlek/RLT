from datetime import datetime, timedelta
import json
from dateutil.relativedelta import relativedelta

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCommandCursor


SLCD_FRMTS = {
    'hour': '%Y-%m-%d %H',
    'day': '%Y-%m-%d',
    'month': '%Y-%m',
}
DT_FRMT = "%Y-%m-%dT%H:%M:%S"


async def get_dt_range(
    dt_from: str,
    dt_upto: str,
    group_type: str
) -> list[str]:
    current_dt = datetime.strptime(dt_from, DT_FRMT)
    dt_range = []
    while current_dt <= datetime.strptime(dt_upto, DT_FRMT):

        match group_type:
            case 'month': shift = relativedelta(months=1)
            case 'day': shift = timedelta(days=1)
            case 'hour': shift = timedelta(hours=1)

        date = current_dt.strftime(SLCD_FRMTS[group_type])
        dt_range.append(
            datetime.strptime(
                date,
                SLCD_FRMTS[group_type]
            ).isoformat()
        )
        current_dt += shift

    return dt_range


async def get_payments_data(
    dt_from: str,
    dt_upto: str,
    group_type: str,
    client: AsyncIOMotorClient,
) -> AsyncIOMotorCommandCursor:
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
                        'format': SLCD_FRMTS[group_type],
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
        },
        {
            '$sort': {'label': 1}
        }
    ]
    return client.sampleDB.sample_collection.aggregate(pipeline)


async def get_result(
    data: list[dict],
    dt_from: str,
    dt_upto: str,
    group_type: str
) -> dict[str, list[int | str]]:
    dataset = [entry['amount'] for entry in data]
    labels = [
        datetime.strptime(entry['label'], SLCD_FRMTS[group_type]).isoformat()
        for entry in data
    ]

    for index, date in enumerate(
        await get_dt_range(dt_from, dt_upto, group_type)
    ):
        if date not in labels:
            dataset.insert(index, 0)
            labels.insert(index, date)

    return {'dataset': dataset, 'labels': labels}


async def calculate_sum_all_payments(
    dt_from: str,
    dt_upto: str,
    group_type: str,
    client: AsyncIOMotorClient,
) -> str:
    data = [
        doc
        async for doc in await get_payments_data(
            dt_from,
            dt_upto,
            group_type,
            client
        )
    ]
    return json.dumps(
        await get_result(data, dt_from, dt_upto, group_type)
    )
