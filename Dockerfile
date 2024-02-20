# Pull python base image
FROM python:3.10

# Update pip
RUN pip install --upgrade pip

# Install dependencies for camelsp with fixed versions
RUN pip install geopandas==0.14.3
RUN pip install "pandas<2.2.0"
RUN pip install numpy==1.25.2
RUN pip install matplotlib==3.8.3
RUN pip install plotly==5.19.0
RUN pip install pyproj==3.6.1
RUN pip install dateparser==1.2.0
RUN pip install dask==2024.2.0
RUN pip install ydata-profiling==4.6.4
RUN pip install tqdm==4.66.2
RUN pip install openpyxl==3.1.2

# Install camelsp from GitHub
RUN git clone https://github.com/CAMELS-DE/camelsp.git
WORKDIR /camelsp
RUN pip install -e .

# Install jupyter
RUN pip install jupyter

# Create a new user, this fixes permission issues of files created by the container / camelsp
RUN useradd -m camel

# Switch to the new user
USER camel

# Copy run_camelsp.sh to the container
COPY --chown=camel scripts/run_camelsp.sh /camelsp/run_camelsp.sh

# Make the script executable
RUN chmod +x /camelsp/run_camelsp.sh

# Run the script when the Docker image is run
CMD ["/camelsp/run_camelsp.sh"]