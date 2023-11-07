#!/usr/bin/python
import os
import time

from apcaccess import status as apc

# Client v1
import influxdb
# Client v2
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Influxdb choosing
dbversion    = int(os.getenv('INFLUXDB_VERSION', '2'))
# Influxdb 1
v1_host      = os.getenv('INFLUXDB1_HOST', 'influxdb')
v1_port      = os.getenv('INFLUXDB1_PORT', 8086)
v1_user      = os.getenv('INFLUXDB1_USER')
v1_password  = os.getenv('INFLUXDB1_PASSWORD')
v1_dbname    = os.getenv('INFLUXDB1_DATABASE', 'apcupsd')
# Influxdb 2
v2_url       = os.getenv('INFLUXDB2_URL', 'http://influxdb:8086')
v2_token     = os.getenv('INFLUXDB2_TOKEN', 'my-token')
v2_org       = os.getenv('INFLUXDB2_ORG', 'my-org')
v2_bucket    = os.getenv('INFLUXDB2_BUCKET', 'my-bucket')
# Other configs
interval     = float(os.getenv('INTERVAL', 5))
ups_alias    = os.getenv('UPS_ALIAS','none')
apcupsd_host = os.getenv('APCUPSD_HOST', 'localhost')
verbose      = os.getenv('VERBOSE', 'false').lower()

if (dbversion == 1):
    client = influxdb.InfluxDBClient(v1_host, v1_port, v1_user, v1_password, v1_dbname)
    client.create_database(v1_dbname)
    print("INFLUXDB1_HOST: ", v1_host)
    print("INFLUXDB1_PORT: ", v1_port)
    print("INFLUXDB1_USER: ", v1_user)
    print("INFLUXDB1_PASSWORD: [redacted]")
    print("INFLUXDB1_DATABASE: ", v1_dbname)
elif (dbversion == 2):
    client = influxdb_client.InfluxDBClient(url=v2_url, token=v2_token, org=v2_org)
    #client.create_database(dbname)
    print("INFLUXDB2_URL: ", v2_url)
    print("INFLUXDB2_TOKEN: [redacted]")
    print("INFLUXDB2_ORG: ", v2_org)
    print("INFLUXDB2_BUCKET: ", v2_bucket)

# Print envs
print("UPS_ALIAS", ups_alias)
print("INTERVAL: ", interval)
print("APCUPSD_HOST", apcupsd_host)
print("VERBOSE: ", verbose)

while True:
    try:
        ups = apc.parse(apc.get(host=apcupsd_host), strip_units=True)
        watts = float(os.getenv('WATTS', ups.get('NOMPOWER', 0.0))) * 0.01 * float(ups.get('LOADPCT', 0.0))
        json_body = [
            {
                'measurement': 'apcaccess_status',
                'fields': {
                    'WATTS': watts,
                    'STATUS': ups.get('STATUS'),
                    'LOADPCT': float(ups.get('LOADPCT', 0.0)),
                    'BCHARGE': float(ups.get('BCHARGE', 0.0)),
                    'TONBATT': float(ups.get('TONBATT', 0.0)),
                    'TIMELEFT': float(ups.get('TIMELEFT', 0.0)),
                    'NOMPOWER': float(ups.get('NOMPOWER', 0.0)),
                    'CUMONBATT': float(ups.get('CUMONBATT', 0.0)),
                    'BATTV': float(ups.get('BATTV', 0.0)),
                    'OUTPUTV': float(ups.get('OUTPUTV', 0.0)),
                    'ITEMP': float(ups.get('ITEMP', 0.0)),
                },
                'tags': {
                    'host': os.getenv('HOSTNAME', ups.get('HOSTNAME', 'apcupsd-influxdb-exporter')),
                    'serial': ups.get('SERIALNO', None),
                    'ups_alias' : ups_alias,
                }
            }
        ]
        if verbose == 'true':
            print(json_body)
            if (dbversion == 1):
                print(client.write_points(json_body))
            elif (dbversion == 2):
                print(client.write_api(write_options=SYNCHRONOUS).write(bucket=v2_bucket, record=json_body))
        else:
            if (dbversion == 1):
                client.write_points(json_body)
            elif (dbversion == 2):
                client.write_api(write_options=SYNCHRONOUS).write(bucket=v2_bucket, record=json_body)
    except Exception as e:
        print('General error, retry in seconds...', e)
    time.sleep(interval)
