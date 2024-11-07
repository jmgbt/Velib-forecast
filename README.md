# Velib-forecast

## API Information




---

# Velib-forecast Project

This project sets up a data pipeline to fetch, process, and analyze data from the Velib bike-sharing API. The entire pipeline is orchestrated using **Apache Airflow** and includes data ingestion, transformation, and visualization. Each step in the pipeline is executed by scheduled Airflow DAGs and leverages the following tools: **Google Cloud Storage (GCS)**, **Airbyte**, **BigQuery**, **dbt**, and **Looker**.

## Data souces
- [Availability](https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json)
- [Station Information](https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json)
Here’s the `README.md` formatted according to GitHub's basic writing and formatting syntax:

## Project Steps
### 1. Request Data from the Velib API
- **Description**: Every 10 minutes, data is requested from the Velib API, which provides real-time information about the availability of bikes and docking stations.
- **API Documentation Summary**: The Velib API provides endpoints for accessing station information and bike availability. Each response includes a list of stations with attributes such as `station_id`, `name`, `bikes_available`, `docks_available`, etc
***see***
  - https://www.data.gouv.fr/fr/datasets/velib-velos-et-bornes-disponibilite-temps-reel/
  - https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/information/?disjunctive.name&disjunctive.is_installed&disjunctive.is_renting&disjunctive.is_returning&disjunctive.nom_arrondissement_communes
- **Airflow Implementation**: 
  - An Airflow task uses the `requests` library to pull data from the API at a 10-minute interval.
  - The API key and endpoint are stored as environment secrets for security.
  
### 2. Create JSONL Files for Each API Response
- **Description**: Each API response is processed to flatten and save the data in a `jsonl` (JSON Lines) format, where each line represents a single data record in JSON.
- **Implementation**: 
  - An Airflow `PythonOperator` loops through the API response and saves each station's data as a separate line in the `jsonl` format.
  - This approach allows efficient storage and streaming of data in downstream tasks.
  
### 3. Upload JSONL File to Google Cloud Storage (GCS)
- **Description**: The generated `jsonl` file is uploaded to a GCS bucket (`velib_status`) for intermediate storage.
- **GCP API Documentation**: The **Google Cloud Storage API** allows programmatic access to store, retrieve, and manage objects within GCS buckets.
- **Airflow Implementation**: 
  - The `google-cloud-storage` library is used within an Airflow task to handle the upload process.
  - The bucket name and object path are configured as Airflow variables.

### 4. Transfer Data from GCS to BigQuery Using Airbyte
- **Description**: Airbyte is used to transfer data from the GCS bucket to **Google BigQuery**.
- **Airbyte API Documentation**: Airbyte provides a connector-based approach to data integration. The GCS-to-BigQuery connector moves files from GCS into BigQuery tables.
- **Airflow Implementation**: 
  - An Airbyte connection priorily established on the webased UI is triggered via Airflow to load data from the `velib_status` bucket into a staging table in BigQuery.
  - Airflow operators can manage Airbyte syncs programmatically.

### 5. Data Transformation Using dbt
- **Description**: Data transformation is performed in BigQuery using **dbt (Data Build Tool)**. Data moves through `staging`, `intermediate`, and `mart` layers, ensuring clean, aggregated, and business-friendly data models.
- **dbt Implementation**:
  - **Staging**: Initial tables created from raw data.
  - **Intermediate**: Data is aggregated and filtered for easier analysis.
  - **Mart**: Final tables that are ready for analytics in Looker.
- **Airflow Integration**: 
  - Airflow triggers dbt commands to run and build the models. Tasks can run `dbt run`, `dbt test`, and `dbt seed` commands to automate the transformation.

### 6. Data Presentation and Analysis in Looker
- **Description**: The final step is to connect **Looker** to the BigQuery data mart, allowing data analysts and business users to create dashboards and analyze Velib data.
- **Implementation**:
  - Looker is configured to connect to BigQuery and access the tables built in the `mart` layer.
  - Dashboards and reports are created to visualize data trends like bike availability, station usage, and other key metrics.

## Project Structure

- **`dags/`**: Airflow DAGs orchestrating the entire pipeline and encompassing the necessary Python scripts for API requests, Json transformation,  uploading, Airbyte transfer
- **`dbt/`**: dbt project files, including `models`, `seeds`, and `macros` executed via a bash commmand triggered within Apache Airflow Dags scripts
- **`looker/`**: Looker configurations for dashboard setup and data mart connection.

## Getting Started

### Prerequisites
1. **Python 3.9.20 and **pip** for running scripts and dbt.
2. **Google Cloud SDK** for GCS and BigQuery.
3. 
4. **Airflow**,**Airbyte-APi**, **dbt**, and **Looker** set up in your environment.

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/velib-data-pipeline.git]
   ```
2. Install dependencies:
   ```poetry install
   pip install -r requirements.txt
   ```

### Running the Pipeline
1. Set up Airflow with the DAGs in `dags/` and configure Google Cloud and Airbyte connections.
2. Run `dbt run` to build the data models manually or trigger from Airflow.
3. Configure Looker to connect to BigQuery and visualize the processed data.

## Usage

- Monitor the pipeline’s progress in Airflow.
- Check data quality and transformations in dbt.
- Analyze final results using Looker dashboards.

## Acknowledgments

This project leverages **Airflow** for orchestration, **GCP** for storage and data processing, **Airbyte** for data integration, **dbt** for transformations, and **Looker** for visualization.

---

This README is now formatted according to GitHub’s markdown syntax. Let me know if there’s anything more you’d like to adjust!
