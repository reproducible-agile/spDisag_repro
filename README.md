<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Code Usage](#code-usage)
* [Contact](#contact)
* [Citation](#citation)
* [Acknowledgements](#acknowledgements)

<!-- About the Project -->
## Spatial Disaggregation
This repository contains the code for the spatial disaggregation of population data from various administrative levels to 100m. grid cells.
The repository includes completed and on-going work.
The considered methods are : single- and multi- output Random Forests and Gradient Boosting with Catboost and multi-output Convlutional Neural Networks with Tensorflow. So far, it is possible to use the tool and reproduce the study by implementing the multi-output Random Forests and Gradient Boosting following the guidelines below. Information about the CNN implementation will be given in the future.

The following steps are required:
1. An environment with the packages included in env.yml.
2. An AncillaryData folder with the desired ancillary data for each case study. GHS, CORINE LAND COVER, ESM etc are examples of ancillary data. 
You need to define them in anciDt.py (raster format).
3. A SDis_Self-Training/Shapefiles/ with the vector layer of the administrative units (shp).
4. A SDis_Self-Training/Statistics/ folder with the aggregated counts respectively (csv).

<!-- Code Usage -->
## Code Usage
In order to reproduce the experiments for the multi-output Regression Trees with Random Forest and Gradient Boosting, please follow the next guidelines:
```
$ git clone https://github.com/mgeorgati/spDisag
$ cd spDisag
$ conda env create -f env.yml 
$ conda activate spdisag_env
$ git checkout multi-output_RF_GB
```
### Input Data Structure
#### Population Data Preparation
A file with the population dataset along with key field corresponding to the administrative unit should be included in a *Statistics* folder in csv format. A file with the administrative borders should be included in a *Shapefile* folder in shp format.

#### Ancillary Data Preparation
A folder with tha ancillary data should be stored in the parent folder. The GHS layer is essential to initiate the process. Topographic layers may include information about land uses, building features, etc.

### Workflow
The *main* file controls the executed processes for each case study. In the *main* file, major variables should be defined based on the input population data and the desired process needs to be selected. The required variables are the following: the city name, the name of the GHS file, the common key between the population data and the administrative unit, the explored demographic groups. Firstly, at least one of the simple heuristic estimates are to be calculated by either performing the pycnophilactic interpolation or the dasymentric mapping. The execution of that produces the desired input for training the regression model. 
Additional parameters need to be defined for training the regression model, such as the type of the model, the desired training dataset, the input to be used, the number of iterations. 
For each of the above outputs, it is suggested to verify the mass preservation, while if the ground truth data at the target resolution is available the direct evaluation of the results may be lastly executed. It is recommended to execute each step seprately.  

### Execute Python Code 
To perform the disaggregation method on your own dataset, please run the following code in python after you have collected the above mentioned datasets.

Usage: 
attr_value=args.attr_value, city=args.city, popraster = args.popraster, key=args.key, 
            run_Pycno=args.run_Pycno, run_Dasy=args.run_Dasy, run_Disaggregation = args.run_Disaggregation, maxIters = args.maxIters, methodopts=args.methodopts, ymethodopts=args.ymethodopts, 
            inputDataset=args.inputDataset, verMassPreserv=args.verMassPreserv, run_Evaluation=args.run_Evaluation 


```
cd spDisag/SDis_Self-Training

python main.py --attr_value=[demographic_groups] --city=[case_study_area] --group_split=[group_split] \
--popraster=[input_pop_layer] --key=[key] --run_Pycno=[run_Pycno] --run_Dasy=[run_Dasy] \
--run_Disaggregation=[run_Disaggregation] \
--maxIters=[maxIters] --methodopts=[methodopts] --ymethodopts=[ymethodopts] --inputDataset=[inputDataset] \
--verMassPreserv=[verMassPreserv] --run_Evaluation=[run_Evaluation]
```

```
--attr_value, the examined demographic groups
--city, case study area
--group_split, points to split the groups (not working yet)
--popraster, population input layer
--key, common key for csv and shp
--run_Pycno, Run pycnophylactic Interpolation
--run_Dasy, Run Dasymetric mapping
--run_Disaggregation, Run Disaggregation
--maxIters, maximum iterations
--methodopts, disaggregation method
--ymethodopts, input layers for disaggregation 
--inputDataset, training dataset
--verMassPreserv, Run mass preservation
--run_Evaluation, Run Evaluation to ground truth
```

Example:    
Perform dasymetric mapping on Amsterdam data with 2 different population groups divided by age and region of origin.     
```
python main.py --attr_value children students mobadults nmobadults elderly sur ant mar tur nonwestern western autoch --city ams \
--group_split 5 12 --popraster GHS_POP_100_near_cubicspline.tif --key Buurtcode --run_Pycno no --run_Dasy no \
--run_Disaggregation yes --iterMax 2 --methodopts apcatbr --ymethodopts Dasy --inputDataset AIL1 \
--verMassPreserv no --run_Evaluation no
```

<!-- Contact -->
## Contact
Marina Georgati - marinag@plan.aau.dk

<!-- Citation -->
## Citation
If you use this algorithm in your research or applications, please cite this source:
M. Georgati, João Monteiro, Bruno Martins and Carsten Keßler [Spatial Disaggregation of Population Subgroups Leveraging Self-Trained Multi-Output Gradient Boosted Regression Trees] 

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
The main architecture was designed by João Monteiro.
This work has been supported by the European Union's Horizon 2020 research and innovation programme under grant agreement No 870649, the project Future Migration Scenarios for Europe (FUME; https://futuremigration.eu). The researchers from INESC-ID were partially funded by Funda\c{c}{\~a}o para a Ci{\^{e}}ncia e Tecnologia (FCT), through the MIMU project with reference PTDC/CCI-CIF/32607/2017, and also through the INESC-ID multi-annual funding from the PIDDAC program (UIDB/50021/2020).
