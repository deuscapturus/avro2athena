# avro2athena

* Generates a `create table` statement for AWS Athena from an avro schema or schema registry (CLI).
* The statement can be used to create an Athena table from (partitioned) avro files.
* Avoids the need of crawling avro data with AWS Glue

## CLI Usage

* Install dependencies `pip install -r requirements.txt --user`
* See `./avro2athena.py --help`

### Example

```
/avro2athena.py http://schema-registry.domain.com:8081 topic.StackExchangePosts-value stack_exchange posts s3://bucket/dir --partition community
```
Creates the following Athena `CREATE TABLE` output:
```
CREATE DATABASE IF NOT EXISTS stack_exchange


CREATE EXTERNAL TABLE IF NOT EXISTS
`stack_exchange`.`posts`
(`id` int, 
`title` string, 
`body` string, 
`tags` array<string>, 
`post_type_id` int, 
`parent_id` int, 
`accepted_answer_id` int, 
`score` int, 
`view_count` int, 
`creation_date` string, 
`last_edit_date` string, 
`favorite_count` int, 
`closed_date` string)
PARTITIONED BY (`community` string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
WITH SERDEPROPERTIES ('avro.schema.literal'='{"type":"record","name":"StackExchangePosts","namespace":"topic.StackExchangePosts","fields":[{"name":"community","type":"string"},{"name":"id","type":"int"},{"name":"title","type":["null","string"],"default":null},{"name":"body","type":"string"},{"name":"tags","type":{"type":"array","items":"string"}},{"name":"post_type_id","type":"int"},{"name":"parent_id","type":["null","int"],"default":null},{"name":"accepted_answer_id","type":["null","int"],"default":null},{"name":"score","type":"int"},{"name":"view_count","type":"int"},{"name":"creation_date","type":{"type":"string","logicalType":"iso-datetime"}},{"name":"last_edit_date","type":["null",{"type":"string","logicalType":"iso-datetime"}],"default":null},{"name":"favorite_count","type":"int"},{"name":"closed_date","type":["null",{"type":"string","logicalType":"iso-datetime"}],"default":null}]}')
STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'
LOCATION 's3://bucket/dir';
```

## Module Usage

* See the example in `run_example.py`. It works in `python3.7` with `avro-python3==1.9.1`.
* The partition statement is optional. It should be of the form `PARTITIONED BY (year string, month string, day string)`. If you don't have partitions, set `partition_statement = ''`.
* It is assumed that the most outer schema type is `Record`.
* Aliases in the avro schema are allowed.
* The schema tree is analyzed recursively, so trees of arbitrary depth are allowed.


### Example
Taking the following standard example schema as input:
```
{
  "namespace": "com.linkedin.haivvreo",
  "name": "test_serializer",
  "type": "record",
  "fields": [
    { "name":"string1", "type":"string" },
    { "name":"int1", "type":"int" },
    { "name":"tinyint1", "type":"int" },
    { "name":"smallint1", "type":"int" },
    { "name":"bigint1", "type":"long" },
    { "name":"boolean1", "type":"boolean" },
    { "name":"float1", "type":"float" },
    { "name":"double1", "type":"double" },
    { "name":"list1", "type":{"type":"array", "items":"string"} },
    { "name":"map1", "type":{"type":"map", "values":"int"} },
    { "name":"struct1", "type":{"type":"record", "name":"struct1_name", "fields": [
          { "name":"sInt", "type":"int" }, { "name":"sBoolean", "type":"boolean" }, { "name":"sString", "type":"string" } ] } },
    { "name":"union1", "type":["float", "boolean", "string"] },
    { "name":"enum1", "type":{"type":"enum", "name":"enum1_values", "symbols":["BLUE","RED", "GREEN"]} },
    { "name":"nullableint", "type":["int", "null"] },
    { "name":"bytes1", "type":"bytes" },
    { "name":"fixed1", "type":{"type":"fixed", "name":"threebytes", "size":3} }
  ] }
```
we obtain the following Athena `create table` output:
```
    CREATE EXTERNAL TABLE IF NOT EXISTS 
    `my_database`.`my_table`
    (`string1` string, `int1` int, `tinyint1` int, `smallint1` int, `bigint1` bigint, `boolean1` boolean, `float1` float, `double1` double, `list1` array<string>, `map1` map<string,int>, `struct1` struct<sint:int,sboolean:boolean,sstring:string>, `union1` float, `enum1` string, `nullableint` int, `bytes1` bytes, `fixed1` string) 
    PARTITIONED BY (year string, month string, day string)
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
    WITH SERDEPROPERTIES ('avro.schema.literal'='{"namespace": "com.linkedin.haivvreo", "name": "test_serializer", "type": "record", "fields": [{"name": "string1", "type": "string"}, {"name": "int1", "type": "int"}, {"name": "tinyint1", "type": "int"}, {"name": "smallint1", "type": "int"}, {"name": "bigint1", "type": "long"}, {"name": "boolean1", "type": "boolean"}, {"name": "float1", "type": "float"}, {"name": "double1", "type": "double"}, {"name": "list1", "type": {"type": "array", "items": "string"}}, {"name": "map1", "type": {"type": "map", "values": "int"}}, {"name": "struct1", "type": {"type": "record", "name": "struct1_name", "fields": [{"name": "sInt", "type": "int"}, {"name": "sBoolean", "type": "boolean"}, {"name": "sString", "type": "string"}]}}, {"name": "union1", "type": ["float", "boolean", "string"]}, {"name": "enum1", "type": {"type": "enum", "name": "enum1_values", "symbols": ["BLUE", "RED", "GREEN"]}}, {"name": "nullableint", "type": ["int", "null"]}, {"name": "bytes1", "type": "bytes"}, {"name": "fixed1", "type": {"type": "fixed", "name": "threebytes", "size": 3}}]}') 
    STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat' 
    OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat' 
    LOCATION 's3://my_bucket/my_folder/'

```


### Translations of data types

* For a `Primitive`, `long` is translated to `bigint`.
* `Array` becomes `array<>`.
* `Map` becomes `map<>`.
* `Record` becomes `struct<>`.
* For a `Union`, the first non `null` type is chosen.
* `Enum` and `Fixed` become `string`, respectively.

## Some hints for importing avro files as AWS Athena table

* Unions with mutliple primitive types: an example is `["float", "boolean", "string"]`. In general, these kind of data types might cause trouble in Athena. Our schema creator will pick the first element `float` form the union. Consider changing such multiple types to `string`. 

* Infer the schema directly from `.avro` data files: see `util/avro_file_schema_parser.py` for how to do that from a single file.
    * Useful if, for whatever reason, the schema of the files is not available. 
    * Useful if Athena does not like the schema for some reason - even though it works with other systems. We experienced examples where inferring the schema from a data file solves the problem. In this case in `create_athena_table_statement_from_avsc` replace `parse_literal_schema_from_file` by `infer_schema_from_avro_file`.



