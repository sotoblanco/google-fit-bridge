terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}


provider "google" {
    project = var.project_id
    region = var.region
    credentials = file("../service_account.json")
}

resource "google_bigquery_dataset" "staging" {
    dataset_id = "staging"
    location = "US"
}

resource "google_bigquery_dataset" "reports" {
    dataset_id = "reports"
    location = "US"
}
    