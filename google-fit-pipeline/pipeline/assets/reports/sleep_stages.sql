/* @bruin
name: reports.sleep_stages
type: bq.sql
depends:
  - staging.fitness_data

materialization:
  type: table
  strategy: time_interval
  incremental_key: date
  time_granularity: date
@bruin */

SELECT 
  DATE(start_time) as date,
  sleep_stage,
  SUM(duration_hours) as duration_hours
FROM staging.fitness_data
WHERE data_type = 'sleep'
  AND start_time >= '{{ start_datetime }}'
  AND start_time < '{{ end_datetime }}'
GROUP BY 1, 2
