import os

TEMP_PATH = 'mlops/tmp/'
TEMP_PROCESSED_PATH = 'mlops/tmp_processed/'
DELIMITER = '+++'

if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)
if not os.path.exists(TEMP_PROCESSED_PATH):
    os.mkdir(TEMP_PROCESSED_PATH)