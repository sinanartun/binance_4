import asyncio
import json
import time
import datetime
import os
import boto3
from binance import AsyncClient, BinanceSocketManager
import get_credentials


def upload_file_to_s3(local_file_path, remote_file_path, s3_bucket_name='awsbc4hello'):
    credentials = get_credentials.get()
    s3 = boto3.client(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['Token']
    )

    if os.path.exists('./bucket_name'):
        with open('./bucket_name', "r") as f:
            bucket_name = f.read()

    else:
        response = s3.list_buckets()
        print(json.dumps(response, indent=4, sort_keys=True, default=str))
        if len(response['Buckets']) < 1:
            print("There is no bucket in you aws account !!!")
            print("Create a bucket firstly")
            exit()

        buckets = sorted(response["Buckets"], key=lambda b: b["CreationDate"], reverse=True)
        bucket_name = buckets[0]["Name"]

        print("last created bucket name", bucket_name)
        f = open('./bucket_name', 'w')
        f.write(bucket_name)
        f.close()

    s3.upload_fileobj(local_file_path, bucket_name, remote_file_path)


async def main():
    active_file_time = int(round(time.time()) / 60)
    new_local_data_file_path = './data/' + str(int(active_file_time * 60)) + '.tsv'

    f = open(new_local_data_file_path, 'w')
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    trade_socket = bm.trade_socket('BTCUSDT')
    # BTCUSDT parametresindeki market hareketlerinin datasını istiyoruz.
    async with trade_socket as tscm:
        while True:
            res = await tscm.recv()
            new_file_time = int(res['T'] / (1000 * 60))
            # Gelen datanın içindeki unixtime'ı (milisecond cinsinden) dakikaya çeviriyoruz.
            # print(res)
            if new_file_time != active_file_time:
                f.close()
                # Eğer mesajın içindeki Unix dakikası active_file_time'a eşit değil ise 1dk'lık biriktirme süresi,
                # dolmuş ve biriktirilen datanın bucket'a yüklenmesi gerekli.
                local_data_file_path = './data/' + str(active_file_time * 60) + '.tsv'
                remote_data_file_path = 'data_1_min/' + str(active_file_time * 60) + '.tsv'

                upload_file_to_s3(local_data_file_path, remote_data_file_path)
                # Bir dakikalık datası dolmuş olan local_data_file'ı, Bucket'a yüklüyoruz.
                active_file_time = new_file_time
                new_local_data_file_path = './data/' + str(int(active_file_time * 60)) + '.tsv'

                f = open(new_local_data_file_path, 'w')
                print(' #' * 50)
                print(' #' * 50)
                print(' #' * 50)
                print(' #' * 20 + ' new file:' + new_local_data_file_path + ' #' * 20)
                print(' #' * 50)
                print(' #' * 50)
                print(' #' * 50)

            timestamp = f"{datetime.datetime.fromtimestamp(int(res['T'] / 1000)):%Y-%m-%d %H:%M:%S}"
            maker = '0'
            if res['m']:  # Satın almış ise 1, satış yaptı ise 0.
                maker = '1'

            line = str(res['t']) + '\t'
            line += str(res['s']) + '\t'
            line += '{:.2f}'.format(round(float(res['p']), 2)) + '\t'
            line += str(res['q'])[0:-3] + '\t'
            line += str(timestamp) + '\t'
            line += str(maker) + '\n'
            f.write(line)
            # Line oluşturuldu
            # print(line)
            # print(res)

    await client.close_connection()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
