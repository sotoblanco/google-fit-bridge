# User Guide: End-to-End Google Fit Bridge

This guide provides a detailed, technically accurate walkthrough of the entire process from hardware acquisition to data-driven insights. It is intended for users who wish to replicate this data platform using a Xiaomi Mi Band (or similar wearable) and Google Fit.

---

## 1. Hardware and Initial Setup

### Choosing the Hardware
The Xiaomi Mi Band (Smart Band) series is the primary hardware for this pipeline. Ensure you are using a version that supports heart rate monitoring and sleep tracking (Mi Band 4 or newer).

### Synchronizing with the Mobile Ecosystem
To move data from the band to the cloud, you must follow this specific data chain:
1.  **Mi Band (Bluetooth)** -> **Zepp Life App** (formerly Mi Fit) or **Mi Fitness App**.
2.  **Zepp Life/Mi Fitness** (Cloud Sync) -> **Google Fit API**.

### Critical Step: Google Fit Integration
Within the Zepp Life/Mi Fitness application settings, you must authorize "Sync to Google Fit." This creates a cloud-to-cloud link where Xiaomi pushes your heart rate, steps, and sleep data to Google's Fitness store.

### Alternative Hardware (Apple Watch, Garmin, Oura)
This project is architected as a **Universal Bridge**. Any wearable device that can synchronize its data with Google Fit will work with this pipeline without modification.

*   **Apple Watch**: Since Apple Health does not have a public cloud API, you must use a "Double Bridge" strategy. Install the **Google Fit** app on your iPhone and enable the integration to "Connect to Apple Health." This allows your iPhone to push Apple Watch data into the Google Fit cloud, where this pipeline can then extract it.
*   **Garmin/Oura/Withings**: These ecosystems often support direct cloud-to-cloud synchronization with Google Fit. Once connected, their data (including high-resolution heart rate and sleep stages) enters the same `staging.fitness_data` table as the Xiaomi data.

---

## 2. Technical Infrastructure

### Google Cloud Platform (GCP) Configuration
Before running the pipeline, you must set up the Google Fit API access:
1.  **Create a GCP Project**: Name it appropriately (e.g., `health-sync`).
2.  **Enable Fitness API**: Search for "Google Fitness API" in the GCP Library and enable it.
3.  **OAuth Consent Screen**: Configure an internal or external consent screen.
4.  **Create Credentials**: Generate an **OAuth 2.0 Client ID** (Desktop Application type).
5.  **Download JSON**: Save this as `credentials.json` in the project root.

### Dataset Provisioning (Terraform)
The pipeline requires two specific datasets in BigQuery: `staging` and `reports`.
1.  Navigate to the `terraform/` directory.
2.  Run `terraform init` and `terraform apply`.
This ensures the underlying storage architecture is correctly configured with the necessary permissions.

---

## 3. Data Pipelines and Ingestion

### Authentication Handshake
To authorize the script to read your health data, run the `auth_fit.py` script locally:
```bash
python auth_fit.py
```
This will open a browser for OAuth2 authentication. Upon success, it generates a `token.json` file. This token is used by the Bruin pipeline for headless operation.

### Running the Orchestrator
The pipeline is managed by **Bruin**. It handles Python ingestion and SQL transformation in a single Directed Acyclic Graph (DAG).

```bash
# General daily execution
bruin run ./google-fit-pipeline/pipeline/

# Historical Backfill (Recommended for initial setup)
bruin run ./google-fit-pipeline/pipeline/ --full-refresh --start-date 2026-03-01 --end-date 2026-03-29
```

---

## 4. Understanding Data Accuracy and Insights

### Challenge: The Sync Lag
The most common technical issue is "missing data." Because the Mi Band syncs to the Mi app via Bluetooth, and then the Mi app syncs to Google Fit via a cloud-to-cloud background task, there can be a **2 to 3-hour delay** before data appears in the API.

**The Technical Solution**: The pipeline uses a `time_interval` materialization strategy. By running a backfill for the last 3 days, Bruin will "sweep up" any delayed records that were missing during the previous day's run.

### Extracting Insights
The data is structured into two main layers:
1.  **Staging Layer**: Cleaned and deduplicated raw metrics.
2.  **Reporting Layer**: Aggregated daily and weekly views.

Use the provided **Looker Studio** template to visualize:
*   **Step Consistency**: Identifying active vs. sedentary days.
*   **Heart Rate Trends**: Monitoring resting heart rate as a proxy for recovery.
*   **Sleep Quality**: Using the `reports.sleep_stages` table to see the ratio of Deep Sleep vs. REM sleep, which is more informative than total sleep duration alone.
