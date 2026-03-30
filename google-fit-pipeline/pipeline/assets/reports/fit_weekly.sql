/* @bruin

name: reports.fitness_weekly
type: bq.sql

depends:
  - staging.fitness_data

materialization:
  type: table
  strategy: time_interval
  incremental_key: week_start
  time_granularity: date

columns:
  - name: data_type
    type: string
    description: "Type of fitness metric (steps, heart_rate, sleep)"
    primary_key: true
  - name: week_start
    type: DATE
    description: "Start of the week"
    primary_key: true
  - name: metric_value
    type: float
    description: "Metric value"
    checks:
      - name: non_negative

@bruin */

SELECT
  DATE_TRUNC(DATE(start_time), WEEK(MONDAY)) AS week_start,
  data_type,
  CASE
    WHEN data_type = 'heart_rate' THEN AVG(value)
    WHEN data_type = 'sleep' THEN SUM(duration_hours) / NULLIF(COUNT(DISTINCT DATE(start_time)), 0)
    ELSE SUM(value)
  END AS metric_value
FROM staging.fitness_data
WHERE start_time >= '{{ start_datetime }}'
  AND start_time < '{{ end_datetime }}'
GROUP BY week_start, data_type
