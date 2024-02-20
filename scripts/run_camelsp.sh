#!/bin/bash
mkdir -p /camelsp/output_data/scripts
exec > >(tee -a /camelsp/output_data/scripts/processing.log) 2>&1

echo "[$(date +%T)] Starting camelsp preprocessing for DE1..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_de1.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE2..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_de2.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE4..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_de4.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE7..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_de7.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE8..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_de8.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DE9..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_de9.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEA..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_dea.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEB..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_deb.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEC..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_dec.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DED..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_ded.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEE..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_dee.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEF..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_def.ipynb

echo "[$(date +%T)] Starting camelsp preprocessing for DEG..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/preprocess_deg.ipynb

echo "[$(date +%T)] Transforming coordinates..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/transform_coords.ipynb

echo "[$(date +%T)] Generating and merging metadata..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/merge_metadata.ipynb

echo "[$(date +%T)] Generate data reports for each station (this may take a while)..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/generate_reports.ipynb

echo "[$(date +%T)] Cleaning up stations..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/cleanup_stations.ipynb

echo "[$(date +%T)] Calculating statistics and generating visualizations for the webiste..."
jupyter nbconvert --execute --output-dir=/camelsp/output_data/scripts --to notebook --log-level WARN /camelsp/scripts/dataset_metrics.ipynb

echo "[$(date +%T)] Finished preprocessing camelsp data."
