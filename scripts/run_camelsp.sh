#!/bin/bash
mkdir -p /camelsp/output_data/scripts
exec > >(tee -a /camelsp/output_data/scripts/processing.log) 2>&1

echo "[$(date +%T)] Starting camelsp preprocessing for DE1..."
papermill /camelsp/scripts/preprocess_de1.ipynb /camelsp/output_data/scripts/preprocess_de1_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE2..."
papermill /camelsp/scripts/preprocess_de2.ipynb /camelsp/output_data/scripts/preprocess_de2_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE4..."
papermill /camelsp/scripts/preprocess_de4.ipynb /camelsp/output_data/scripts/preprocess_de4_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE7..."
papermill /camelsp/scripts/preprocess_de7.ipynb /camelsp/output_data/scripts/preprocess_de7_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE8..."
papermill /camelsp/scripts/preprocess_de8.ipynb /camelsp/output_data/scripts/preprocess_de8_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE9..."
papermill /camelsp/scripts/preprocess_de9.ipynb /camelsp/output_data/scripts/preprocess_de9_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEA..."
papermill /camelsp/scripts/preprocess_dea.ipynb /camelsp/output_data/scripts/preprocess_dea_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEB..."
papermill /camelsp/scripts/preprocess_deb.ipynb /camelsp/output_data/scripts/preprocess_deb_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEC..."
papermill /camelsp/scripts/preprocess_dec.ipynb /camelsp/output_data/scripts/preprocess_dec_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DED..."
papermill /camelsp/scripts/preprocess_ded.ipynb /camelsp/output_data/scripts/preprocess_ded_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEE..."
papermill /camelsp/scripts/preprocess_dee.ipynb /camelsp/output_data/scripts/preprocess_dee_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEF..."
papermill /camelsp/scripts/preprocess_def.ipynb /camelsp/output_data/scripts/preprocess_def_output.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEG..."
papermill /camelsp/scripts/preprocess_deg.ipynb /camelsp/output_data/scripts/preprocess_deg_output.ipynb

echo "[$(date +%T)] Transforming coordinates..."
papermill /camelsp/scripts/transform_coords.ipynb /camelsp/output_data/scripts/transform_coords_output.ipynb

echo "[$(date +%T)] Generating and merging metadata..."
papermill /camelsp/scripts/merge_metadata.ipynb /camelsp/output_data/scripts/merge_metadata_output.ipynb

echo "[$(date +%T)] Generate data reports for each station (this may take a while)..."
papermill /camelsp/scripts/generate_reports.ipynb /camelsp/output_data/scripts/generate_reports_output.ipynb

echo "[$(date +%T)] Cleaning up stations..."
papermill /camelsp/scripts/cleanup_stations.ipynb /camelsp/output_data/scripts/cleanup_stations_output.ipynb

echo "[$(date +%T)] Calculating statistics and generating visualizations for the webiste..."
papermill /camelsp/scripts/dataset_metrics.ipynb /camelsp/output_data/scripts/dataset_metrics_output.ipynb

echo "[$(date +%T)] Finished preprocessing camelsp data."

chmod -R 777 /camelsp/output_data/