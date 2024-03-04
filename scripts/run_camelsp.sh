#!/bin/bash
mkdir -p /camelsp/output_data/scripts/camelsp

exec > >(tee -a /camelsp/output_data/scripts/camelsp/processing.log) 2>&1

# Start processing
echo "[$(date +%F\ %T)] Starting processing of camelsp for the CAMELS-DE dataset..."

echo "[$(date +%T)] Starting camelsp preprocessing for DE1..."
papermill /camelsp/scripts/preprocess_de1.ipynb /camelsp/output_data/scripts/camelsp/preprocess_de1_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DE2..."
papermill /camelsp/scripts/preprocess_de2.ipynb /camelsp/output_data/scripts/camelsp/preprocess_de2_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DE4..."
papermill /camelsp/scripts/preprocess_de4.ipynb /camelsp/output_data/scripts/camelsp/preprocess_de4_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DE7..."
papermill /camelsp/scripts/preprocess_de7.ipynb /camelsp/output_data/scripts/camelsp/preprocess_de7_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DE8..."
papermill /camelsp/scripts/preprocess_de8.ipynb /camelsp/output_data/scripts/camelsp/preprocess_de8_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DE9..."
papermill /camelsp/scripts/preprocess_de9.ipynb /camelsp/output_data/scripts/camelsp/preprocess_de9_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DEA..."
papermill /camelsp/scripts/preprocess_dea.ipynb /camelsp/output_data/scripts/camelsp/preprocess_dea_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DEB..."
papermill /camelsp/scripts/preprocess_deb.ipynb /camelsp/output_data/scripts/camelsp/preprocess_deb_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DEC..."
papermill /camelsp/scripts/preprocess_dec.ipynb /camelsp/output_data/scripts/camelsp/preprocess_dec_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DED..."
papermill /camelsp/scripts/preprocess_ded.ipynb /camelsp/output_data/scripts/camelsp/preprocess_ded_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DEE..."
papermill /camelsp/scripts/preprocess_dee.ipynb /camelsp/output_data/scripts/camelsp/preprocess_dee_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DEF..."
papermill /camelsp/scripts/preprocess_def.ipynb /camelsp/output_data/scripts/camelsp/preprocess_def_output.ipynb --no-progress-bar

echo "[$(date +%T)] Starting camelsp preprocessing for DEG..."
papermill /camelsp/scripts/preprocess_deg.ipynb /camelsp/output_data/scripts/camelsp/preprocess_deg_output.ipynb --no-progress-bar

echo "[$(date +%T)] Transforming coordinates..."
papermill /camelsp/scripts/transform_coords.ipynb /camelsp/output_data/scripts/camelsp/transform_coords_output.ipynb --no-progress-bar

echo "[$(date +%T)] Generating and merging metadata..."
papermill /camelsp/scripts/merge_metadata.ipynb /camelsp/output_data/scripts/camelsp/merge_metadata_output.ipynb --no-progress-bar

echo "[$(date +%T)] Generate data reports for each station (this may take a while)..."
papermill /camelsp/scripts/generate_reports.ipynb /camelsp/output_data/scripts/camelsp/generate_reports_output.ipynb --no-progress-bar

echo "[$(date +%T)] Cleaning up stations..."
papermill /camelsp/scripts/cleanup_stations.ipynb /camelsp/output_data/scripts/camelsp/cleanup_stations_output.ipynb --no-progress-bar

echo "[$(date +%T)] Calculating statistics and generating visualizations for the webiste..."
papermill /camelsp/scripts/dataset_metrics.ipynb /camelsp/output_data/scripts/camelsp/dataset_metrics_output.ipynb --no-progress-bar

echo "[$(date +%T)] Finished camelsp processing."

# change permissions of the output data
chmod -R 777 /camelsp/output_data/