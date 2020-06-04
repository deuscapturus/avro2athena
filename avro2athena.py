#!/usr/bin/python3
import argparse

from avro.schema import RecordSchema
from confluent_kafka.schema_registry import SchemaRegistryClient
from create_statement_creator.athena_schema import create_athena_schema_from_avro
from create_statement_creator.athena_schema import create_athena_column_schema

parser = argparse.ArgumentParser(description='Generate a AWS Athena CREATE TABLE statement from a avro schema in a schema registry')
parser.add_argument('registry_url', nargs='?', help='URL of the avro schema registry', default='http://localhost:8081')
parser.add_argument('avro_subject', nargs='?', help='the schema subject name to generate the create table statement from')
parser.add_argument('athena_database', nargs='?', help='Name of the athena database')
parser.add_argument('athena_table_name', nargs='?', help='The name of the table to create')
parser.add_argument('s3_location', nargs='?', help='S3 location of your database. Example: s3://bucket/folder/')
parser.add_argument('--partition', nargs='+', type=str, help='partitions, can be specified multiple times.', default=[])

args = parser.parse_args()

schema_registry = SchemaRegistryClient({"url": args.registry_url})
avro_schema_literal = schema_registry.get_latest_version(f"{args.avro_subject}").schema.schema_str


athena_schema, partition_schema = create_athena_schema_from_avro(avro_schema_literal, args.partition)

if partition_schema:
    partition_statement = f'\nPARTITIONED BY ({partition_schema})'
else:
    partition_statement = ''


print(f'''
CREATE DATABASE IF NOT EXISTS {args.athena_database};
''')

print(f'''
CREATE EXTERNAL TABLE IF NOT EXISTS
`{args.athena_database}`.`{args.athena_table_name}`
({athena_schema}){partition_statement}
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
WITH SERDEPROPERTIES ('avro.schema.literal'='{avro_schema_literal}')
STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'
LOCATION '{args.s3_location}';
''')
