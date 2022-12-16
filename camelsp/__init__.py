# set some common paths
import os

from .__version__ import __version__
from .util import nuts3

# This package is intended to be installed along with the data folder
BASEPATH = os.path.abspath(os.path.dirname(__file__))

INPUT_PATH = os.path.abspath(os.path.join(BASEPATH, '..', 'input_data'))
OUTPUT_PATH = os.path.abspath(os.path.join(BASEPATH, '..', 'output_data'))
