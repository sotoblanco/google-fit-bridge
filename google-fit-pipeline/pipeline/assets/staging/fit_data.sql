/* @bruin
name: staging.fitness_data
type: bq.sql

depends:
  - ingestion.fitness_data

materialization:  
  type: table
  strategy: time_interval
  incremental_key: start_time
  time_granularity: timestamp
  partition_by: DATE(start_time)
  cluster_by: ["data_type"]

columns:
  - name: data_type
    type: string
    description: "Type of fitness metric (steps, heart_rate, sleep)"
    primary_key: true
    checks:
      - name: not_null
  - name: start_time
    type: timestamp
    description: "Start time of the data point"
    primary_key: true
    checks:
      - name: not_null
  - name: end_time
    type: timestamp
    description: "End time of the data point"
    checks:
      - name: not_null
  - name: duration_hours
    type: float
    description: "Duration of the data point in hours"
    checks:
      - name: non_negative
  - name: value
    type: float
    description: "Metric value"
    checks:
      - name: non_negative
  - name: extracted_at
    type: timestamp
    description: "When the data was extracted"
  - name: sleep_stage
    type: string
    description: "Sleep stage (light, deep, rem) for sleep data points"

custom_checks:
  - name: no_duplicate_records
    description: "No duplicate data_type + start_time combinations"
    query: |
      SELECT COUNT(*) - COUNT(DISTINCT CONCAT(data_type, CAST(start_time AS STRING)))
      FROM staging.fitness_data
    value: 0

@bruin */

SELECT
  data_type,
  start_time,
  end_time,
  TIMESTAMP_DIFF(end_time, start_time, MINUTE) / 60.0 AS duration_hours,
  CAST(value AS FLOAT64) AS value,
  extracted_at,
  CASE
    WHEN data_type = 'sleep' AND value = 1 THEN 'awake'
    WHEN data_type = 'sleep' AND value = 2 THEN 'sleep'
    WHEN data_type = 'sleep' AND value = 3 THEN 'out_of_bed'
    WHEN data_type = 'sleep' AND value = 4 THEN 'light'
    WHEN data_type = 'sleep' AND value = 5 THEN 'deep'
    WHEN data_type = 'sleep' AND value = 6 THEN 'rem'
    ELSE NULL
  END AS sleep_stage
FROM ingestion.fitness_data
WHERE start_time >= '{{ start_datetime }}'
  AND start_time < '{{ end_datetime }}'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY data_type, start_time ORDER BY extracted_at DESC) = 1
