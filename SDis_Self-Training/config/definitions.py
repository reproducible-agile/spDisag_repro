import os

#ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
#parent_path = os.path.dirname(ROOT_DIR)

ROOT_DIR = "C:/Users/OstermannFO/GitHub/spDisag_repro/SDis_Self-Training"
parent_path = "C:/Users/OstermannFO/GitHub/spDisag_repro"
year=2018
ancillary_path = parent_path + '/AncillaryData/'
pop_path = "C:/FUME/Dasymetric_Mapping/GroundTruth/"
#path to folder with gdal executable files
gdal_rasterize_path = r'C:/Users/OstermannFO/Miniconda3/envs/spdisag_env/bin'
python_scripts_folder_path = r'C:/Users/OstermannFO/Miniconda3/envs/spdisag_env/Scripts'

temp_shp= ancillary_path + "/temp_shp/"
temp_tif= ancillary_path + "/temp_tif/"
