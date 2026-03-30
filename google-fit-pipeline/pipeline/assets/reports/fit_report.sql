/* @bruin

name: reports.fitness_daily
type: bq.sql

depends:
  - staging.fitness_data

materialization:
  type: table
  strategy: time_interval
  incremental_key: date
  time_granularity: date

columns:
  - name: data_type
    type: string
    description: "Type of fitness metric (steps, heart_rate, sleep)"
    primary_key: true
  - name: date
    type: DATE
    description: "Date of the data point"
    primary_key: true
  - name: metric_value
    type: float
    description: "Metric value"
    checks:
      - name: non_negative

@bruin */

SELECT
  DATE(start_time) AS date,
  data_type,
  CASE
    WHEN data_type = 'heart_rate' THEN AVG(value)
    WHEN data_type = 'sleep' THEN SUM(duration_hours)
    ELSE SUM(value)
  END AS metric_value
FROM staging.fitness_data
WHERE start_time >= '{{ start_datetime }}'
  AND start_time < '{{ end_datetime }}'
GROUP BY date, data_type
