import asyncio
import datetime
from binance import AsyncClient, BinanceSocketManager
import boto3


async def main(table):
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    trade_socket = bm.trade_socket('BTCUSDT')
    async with trade_socket as tscm:
        while True:
            res = await tscm.recv()
            timestamp = f"{datetime.datetime.fromtimestamp(int(res['T'] / 1000)):%Y-%m-%d %H:%M:%S}"
            maker = '0'
            if res['m']:  # Satın almış ise 1, satış yaptı ise 0.
                maker = '1'

            bid = int(res['t'])
            parameter = str(res['s'])
            price = '{:.2f}'.format(round(float(res['p']), 2))
            quantity = str(res['q'])[0:-3]
            timestamp = str(timestamp)
            maker = str(maker)
            response = table.put_item(
                Item={
                    'bid': bid,
                    'parameter': parameter,
                    'price': price,
                    'quantity': quantity,
                    'timestamp': timestamp,
                    'maker': maker,
                }
            )

    await client.close_connection()


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('BTCUSDT')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(table))
