import glob
import os

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
import rasterio.mask
from osgeo import gdal

import osgeoutils as osgu
#from config.definitions import ROOT_DIR, ancillary_path, city, pop_path
from evaluateFunctions import (percentage_error,div_error, mae_error, nmae_error, nrmse_error,
                               prop_error, rmse_error) #, zonalStat
from gdalutils import maskRaster
from plotting.plotRaster import plot_map
from plotting.plotVectors import plot_mapVectorPolygons

print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.mainFunctions.basic import createFolder

"""
    EVALUATION OF THE PREDICTIONS WITH THE GROUND TRUTH DATA OF OISg DATASET
"""
def eval_Results_GC_ams(ROOT_DIR, pop_path, ancillary_path, year, city, attr_value):
    if city == 'ams': 
        #Required directories
        evalPath = ROOT_DIR + "/Evaluation/{}_final/".format(city) 
    else: 
        #Required directories
        evalPath = ROOT_DIR + "/Evaluation/{}_cbs/".format(city) 
    print(attr_value)
    # Required files
    actualPath = pop_path + "/OIS/gridCells/{0}_{1}.tif".format(year,attr_value)
    raster_file = ancillary_path + '/temp_tif/ams_CLC_2012_2018.tif'
    polyPath = ROOT_DIR + "/Shapefiles/{1}/{0}_{1}.shp".format(year,city)
    municipalities = "C:/Users/NM12LQ/OneDrive - Aalborg Universitet/DasymetricMapping/ams_ProjectData/AncillaryData/adm/municipalities/{0}_{1}_GM.shp".format(year,city)
    districtPath =  'C:/Users/NM12LQ/OneDrive - Aalborg Universitet/DasymetricMapping/ams_ProjectData/AncillaryData/adm/ams_districts.geojson'
    waterPath = 'C:/Users/NM12LQ/OneDrive - Aalborg Universitet/DasymetricMapping/ams_ProjectData/AncillaryData/corine/waterComb_grootams_CLC_2012_2018.tif'.format(city)
   
    aggr_outfileSUMGT = ROOT_DIR + "/Shapefiles/Comb/{0}_ams_ois.shp".format(year,city)
    ##### -------- PLOT Ground truth at Grid Cells -------- #####
    print("----- Plotting Population Distribution -----") 
    print("----- Ground Truth for Amsterdam at Grid Cells -----") 
    templatePathGA = ROOT_DIR + '/Rasters/template/{0}_template_100.tif'.format(city)
    #ds,rastergeo  = osgu.readRaster(actualPath)
    # Clip GT to extent of Municipality 
    data = gdal.Open(templatePathGA)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0] 
    maxy = geoTransform[3] 
    maxx = minx + geoTransform[1] * data.RasterXSize 
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    bbox = (minx,maxy,maxx,miny)
    outputGTL =  ROOT_DIR + "/Evaluation/{1}_groundTruth/{0}_{1}_{2}.tif".format(year,city,attr_value)
    if not os.path.exists(outputGTL):
        gdal.Translate(outputGTL, actualPath, projWin=bbox)

    outputGT =  ROOT_DIR + "/Evaluation/{1}_groundTruth/{0}_{1}_{2}.tif".format(year,city,attr_value)
    if not os.path.exists(outputGT):
        maskRaster(polyPath, outputGTL, outputGT)
    
    exportPath = evalPath + "/ams_GT_{}.png".format(attr_value)
    if not os.path.exists(exportPath):
        title ="Population Distribution (persons)\n(Ground Truth: {})(2018)".format(attr_value)
        LegendTitle = "Population (persons)"
        src = rasterio.open(outputGT)
        #plot_map(city,'popdistribution', src, exportPath, title, LegendTitle, districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
    
    ##### -------- Get files to be processed -------- #####
    print("----- Get prediction files to be evaluated -----") 
    evalFiles = [ROOT_DIR + "/Results/{0}/aprf/dissever00WIESMN_2018_ams_Dasy_aprf_p[1]_12AIL12_1IL_it10_{1}.tif".format(city,attr_value), 
                 #ROOT_DIR + "/Results/{0}/aprf/dissever01WIESMN_100_2018_ams_DasyA_aprf_p[1]_12AIL12_13IL_it10_{1}.tif".format(city,attr_value),
                 #ROOT_DIR + "/Results/{0}/apcatbr/dissever01WIESMN_500_2018_ams_DasyA_apcatbr_p[1]_12AIL12_12IL_it10_ag_{1}.tif".format(city,attr_value)
                 ]
    # All files ending with .shp with depth of 2 folder
    """# Get all spatial data for neighborhoods in list
    evalFiles = [ROOT_DIR + "/Results/{0}/Pycno/{2}_{0}_{1}_pycno.tif".format(city,attr_value,year),ROOT_DIR + "/Results/{0}/Dasy/{2}_{0}_{1}_dasyWIESMN.tif".format(city,attr_value,year),
                 ROOT_DIR + "/Results/{0}/aprf/dissever00WIESMN_2018_ams_Dasy_aprf_p[1]_3AIL5_1IL_it10_{1}.tif".format(city,attr_value),ROOT_DIR + "/Results/{0}/aprf/dissever00WIESMN_2018_ams_Dasy_aprf_p[1]_12AIL12_1IL_it10_{1}.tif".format(city,attr_value),
                 ROOT_DIR + "/Results/{0}/aprf/dissever01WIESMN_100_2018_ams_DasyA_aprf_p[1]_3AIL5_13IL_it10_{1}.tif".format(city,attr_value), ROOT_DIR + "/Results/{0}/aprf/dissever01WIESMN_100_2018_ams_DasyA_aprf_p[1]_12AIL12_13IL_it10_{1}.tif".format(city,attr_value)]
    # All files ending with .shp with depth of 2 folder
    #evalFiles1 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/*".format(city,attr_value))
    evalFiles1A = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/dissever01WIESMN_500*{1}.tif".format(city,attr_value))
    
    evalFiles3 = glob.glob(ROOT_DIR + "/Results/{0}/aprf/dissever00WIESMN*3AIL5_1IL_it10_{1}.tif".format(city,attr_value))
    evalFiles4 = glob.glob(ROOT_DIR + "/Results/{0}/aprf/dissever00WIESMN*12AIL12_1IL_it10_{1}.tif".format(city,attr_value))
    
    evalFiles5 = glob.glob(ROOT_DIR + "/Results/{0}/aprf/*100_*_3AIL5_1IL_it10*_{1}.tif".format(city,attr_value))
    evalFiles6 = glob.glob(ROOT_DIR + "/Results/{0}/aprf/*100_*_12AIL12_1IL_it10*_{1}.tif".format(city,attr_value))
    
    
    evalFiles8 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/dissever01WIESMN_100_2018_ams_DasyA_apcatbr_p[1]_12AIL12_12IL_it10_{1}.tif".format(city,attr_value))
    
    evalFiles7 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/*_100_*_12IL_it10*_{1}.tif".format(city,attr_value))
    evalFiles9 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/*_250_*_12IL_it10*_{1}.tif".format(city,attr_value))
    evalFiles11 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/*_500_*_it10*_{1}.tif".format(city,attr_value))
    
    evalFiles10 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/dissever01WIESMN_250_2018_ams_DasyA_apcatbr_p[1]_12AIL12_12IL_it10_{1}.tif".format(city,attr_value))    
    evalFiles12 = glob.glob(ROOT_DIR + "/Results/{0}/apcatbr/dissever01WIESMN_500_2018_ams_DasyA_apcatbr_p[1]_12AIL12_12IL_it10_{1}.tif".format(city,attr_value))
    evalFiles2 = glob.glob(ROOT_DIR + "/Results/{0}/Dasy/*_{0}_{1}_dasyWIESMN.tif".format(city,attr_value))
    evalFiles1 = glob.glob(ROOT_DIR + "/Results/{0}/Pycno/*_{0}_{1}_pycno.tif".format(city,attr_value))
    evalFiles4 = glob.glob(ROOT_DIR + "/Results/{0}/GHS/*.tif".format(city))
    a =[ROOT_DIR + "/Results/{0}/aprf/dissever00WIESMN_500_2018_ams_Dasy_aprf_p[1]_12AIL12_1IL_it10_{1}.tif".format(city,attr_value)]
    evalFiles.extend(evalFiles7)
   
    evalFiles.extend(evalFiles9)
    
    evalFiles.extend(evalFiles11)
    evalFiles.extend(a)"""
    print(evalFiles)
    print("----- {} files to be evaluated -----".format(len(evalFiles))) 

    if city == 'grootams':
        ##### -------- PLOT PREDICTIONS for Greater Amsterdam at Grid Cells -------- #####
        print("----- Plotting Population Distribution -----") 
        print("----- ", len(evalFiles), "files for Greater Amsterdam at Grid Cells -----") 
        evalPathGA = ROOT_DIR + "/Evaluation/{}_gridcells/".format(city) #export directory
        for k in evalFiles:
            path = Path(k)
            name = path.stem 
            exportPath = evalPathGA + "/{}.png".format(name)
            if not os.path.exists(exportPath):
                title ="Population Distribution (persons)\n({})(2018)".format(name)
                LegendTitle = "Population (persons)"
                src = rasterio.open(path)
                plot_map(city,'popdistributionPred', src, exportPath, title, LegendTitle, districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
        
    filenamemetrics2e = evalPath + '/{1}_EvaluationA_{0}.csv'.format(attr_value,city)
    if os.path.exists(filenamemetrics2e):
        os.remove(filenamemetrics2e)

    ##### -------- Process Evaluation: Steps -------- #####
    print("----- Plotting Population Distribution -----") 
    print("----- Ground Truth for Amsterdam at Grid Cells -----")      
    for file in evalFiles:
        path = Path(file)
        fileName = path.stem
        method = fileName.split("_",1)[1]
        print(fileName)
        # Clip the predictions to AMS extent 
        input = file
        if 'aprf' in fileName:
            if 'dissever00' in fileName:
                outputPath = evalPath + "/aprf/dissever00"
                createFolder(outputPath)
            else:
                outputPath = evalPath + "/aprf/dissever01"
                createFolder(outputPath)
        elif 'apcatbr' in fileName:
            outputPath = evalPath + "/apcatbr"
            createFolder(outputPath)
        elif 'GHS' in fileName:
            outputPath = evalPath + "/GHS"
            createFolder(outputPath)
        elif fileName.endswith('_dasyWIESMN'):
            outputPath = evalPath + "/Dasy"
            createFolder(outputPath)
        elif fileName.endswith('_pycno'):
            outputPath = evalPath + "/Pycno"
            createFolder(outputPath)
        else: 
            outputPath = evalPath
            
        outputfile = outputPath + "/ams_{}.tif".format(fileName)
        if not os.path.exists(outputfile):
            maskRaster(polyPath, input, outputfile)
        # Plot the population distribution of the predictions 
        exportPath = outputPath + "/ams_{}.png".format(fileName)
        if not os.path.exists(exportPath):
            print("----- Step #1: Plotting Population Distribution -----")
            title ="Population Distribution (persons)\n({})(2018)".format(fileName)
            LegendTitle = "Population (persons)"
            src = rasterio.open(path)
            #plot_map(city,'popdistributionPred', src, exportPath, title, LegendTitle, districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
        
        print("----- Step #2: Calculating Metrics -----")
        src_real = rasterio.open(outputGT)
        actual = src_real.read(1)
        
        src_pred = rasterio.open(input)
        predicted = src_pred.read(1)
        predicted[(np.where((predicted <= -100000)))] = np.nan
        predicted = np.nan_to_num(predicted, nan=0) 
        actSum = np.nansum(actual)
        predSum =np.nansum(predicted)
        
        actMax = np.nanmax(actual)
        predMax =np.nanmax(predicted)
        
        actMean = np.nanmean(actual)
        predMean =np.nanmean(predicted)
        # Read raster to get extent for writing the rasters later
        ds, rastergeo = osgu.readRaster(input)

        r1, MAEdataset, std = mae_error(actual, predicted) 
        r2 = round(rmse_error(actual, predicted), 1)
        r3 = round(nmae_error(actual, predicted), 4)
        r4 = round(nrmse_error(actual, predicted), 4)

        r5 = prop_error(actual, predicted)[0]
        MAEdataset = prop_error(actual, predicted)[1]
        #r6 = div_error(actual, predicted)[0]
        #DIVdataset = div_error(actual, predicted)[1]
        r6 = percentage_error(actual, predicted)[0]
        DIVdataset = np.absolute(percentage_error(actual, predicted)[1])
        DIVdataset[(np.where(DIVdataset == 100))] = 0
        
        
        stdActual = round(np.std(actual, dtype=np.float64),2)
        stdPred = round(np.std(predicted, dtype=np.float64),2)
        
        print("----- Step #2: Writing CSV with Metrics -----")    
        if os.path.exists(filenamemetrics2e):
            with open(filenamemetrics2e, 'a') as myfile:
                myfile.write(fileName + ';' + "{0}/±{1}".format(r1,std) + ';'+ str(r2) + ';' + str(r3) + ';' + str(r4) + ';' + str(round(r5,2)) + ';' 
                            + str(round(r6,2)) +';' + str(actSum) + ';' + str(predSum) +  ';' + str(actMax) + ';' + str(predMax) + ';' + str(round(actMean,2)) + ';' + str(round(predMean,2)) + ';' + str(stdActual) + ';' + str(stdPred) + '\n')       
        else:
            with open(filenamemetrics2e, 'w+') as myfile:
                myfile.write('Comparison among the predictions and the ground truth data for the Municipality of Amsterdam\n')
                myfile.write('Method;MAE/SD;RMSE;MAEMEAN;RMSEMEAN;PrE;PE;ActualSum;PredictedSum;ActualMax;PredictedMax;ActualMean;PredictedMean;ActualSTD;PredictedSTD\n')
                myfile.write(fileName + ';' + "{0}/±{1}".format(r1,std) + ';'+ str(r2) + ';' + str(r3) + ';' + str(r4) + ';' + str(round(r5,2)) + ';' 
                            + str(round(r6,2)) + ';' + str(actSum) + ';' + str(predSum) +  ';' + str(actMax) + ';' + str(predMax) + ';' + str(round(actMean,2)) + ';' + str(round(predMean,2)) + ';' + str(stdActual) + ';' + str(stdPred) + '\n')
             
        # Write the difference and the quotient TIF files (gridcells) 
        print("----- Step #3: Writing TIF files with Difference and quotient -----") 
        outfileMAECL = outputPath + "/mae_ams_{}CL.tif".format(fileName)
        outfileDivCL = outputPath + "/div_ams_{}CL.tif".format(fileName)
        
        osgu.writeRaster(MAEdataset[:,:], rastergeo, outfileMAECL)
        osgu.writeRaster(DIVdataset[:,:], rastergeo, outfileDivCL)
        
        outfileMAE = outputPath + "/mae_ams_{}.tif".format(fileName)
        outfileDiv = outputPath + "/div_ams_{}.tif".format(fileName)
        maskRaster(polyPath,outfileMAECL, outfileMAE)
        maskRaster(polyPath,outfileDivCL, outfileDiv)
        
        os.remove(outfileMAECL)
        os.remove(outfileDivCL)
        
        # Write the difference and the quotient TIF files (gridcells) 
        print("----- Step #3A: Plotting Difference and quotient -----") 
        exportPath = outputPath + "/mae_{}_Grid.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Absolute Error (persons)\n({})(2018)".format(fileName)
            LegendTitle = "Absolute Error (persons)"
            src = rasterio.open(outfileMAE)
            #plot_map(city,'mae', src, exportPath, title, LegendTitle, districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
        
        exportPath = outputPath + "/div_{}_Grid.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Absolute Percentage Error (%)\n({})(2018)".format(fileName)
            LegendTitle = "Error (%)"
            src = rasterio.open(outfileDiv)
            plot_map(city,'pe', src, exportPath, title, LegendTitle, districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
        
        """
        # Calculate the mean difference and the quotient by neighborhood 
        # Write Zonal Statistics file and csv
        print("----- Step #4: Calculating the mean difference and the quotient by neighborhood -----")
        aggr_outfileMAE = outputPath + "/mae_ams_{}.geojson".format(fileName)
        aggr_outfileDiv = outputPath + "/div_ams_{}.geojson".format(fileName)
        statistics = "mean"
        print("----- Step #4A: Calculating ZSTAT (mean) -----")
        if not os.path.exists(aggr_outfileMAE):
            print('NO ZONAL STAT CALCULATED')
            #zonalStat(outfileMAE, aggr_outfileMAE, polyPath, statistics)
        if not os.path.exists(aggr_outfileDiv):
            print('NO ZONAL STAT CALCULATED')
            #zonalStat(outfileDiv, aggr_outfileDiv, polyPath, statistics)
        
        print("----- Step #4B: Plotting the mean difference and the quotient by neighborhood -----")
        src = gpd.read_file(aggr_outfileMAE)
        #src = src.loc[src['BU_CODE'].str.contains('BU0363')]
        exportPath = outputPath + "/mae_{}_Polyg.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Mean Absolute Error by Neighborhood (persons)\n({})(2018)".format(fileName)
            LegendTitle = "Absolute Error (persons)"
            #plot_mapVectorPolygons(city,'mae', src, exportPath, title, LegendTitle, 'mean_', districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
        
        src = gpd.read_file(aggr_outfileDiv)
        #src = src.loc[src['BU_CODE'].str.contains('BU0363')]
        exportPath = outputPath + "/div_{}_Polyg.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Mean Percentage Accuracy by Neighborhood (%)\n({})(2018)".format(fileName)
            LegendTitle = "Mean Accuracy (%)"
            #plot_mapVectorPolygons(city,'div', src, exportPath, title, LegendTitle, 'mean_', districtPath=districtPath, neighPath=polyPath, waterPath=waterPath, invertArea= None, addLabels=True)
                  
        # Calculate the sum of population by neighborhood 
        # Write Zonal Statistics file and csv
        print("----- Step #5: Calculating the sum of the population by neighborhood ZSTAT -----")
        aggr_outfileSUM = outputPath+ "/ams_{}.geojson".format(fileName)
        statistics = "sum"
        print("----- Step #5A: Calculating ZSTAT (sum)-----")
        if not os.path.exists(aggr_outfileSUM):
            print('NO ZONAL STAT CALCULATED')
            #zonalStat(outputfile, aggr_outfileSUM, polyPath, statistics)
        
        print("----- Step #5B: Plotting the total population by neighborhood for predictions -----")
        src = gpd.read_file(aggr_outfileSUM)
        exportPath = outputPath + "{}_Polyg.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Population Distribution (persons)\n({})(2018)".format(fileName)
            LegendTitle = "Population (persons)"
            #plot_mapVectorPolygons(city,'popdistributionPolyg', src, exportPath, title, LegendTitle, 'sum_', districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)

        print("----- Step #5C: Plotting the difference and the quotient of the sum by neighborhood for predictions to the original -----")
        frame = gpd.read_file(aggr_outfileSUMGT) 
        frame = frame.set_index('Buurtcode').join(src.set_index('Buurtcode'), lsuffix='_l')
        frame["dif_{}".format(attr_value)] = frame['sum_'] - frame["{}".format(attr_value)]
        frame["prop_{}".format(attr_value)] = (frame["{}".format(attr_value)] / frame['sum_'])*100
        exportPath = outputPath + "/mae0_{}_Polyg.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Error by Neighborhood (persons)\n({})(2018)".format(fileName)
            LegendTitle = "Error (persons)"
            #plot_mapVectorPolygons(city,'mae', frame, exportPath, title, LegendTitle, "dif_{}".format(attr_value), districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
            
        exportPath = outputPath + "/div0_{}_Polyg.png".format(fileName)
        if not os.path.exists(exportPath):
            title ="Percentage Accuracy by Neighborhood (%)\n({})(2018)".format(fileName)
            LegendTitle = "Accuracy (%)"
            #plot_mapVectorPolygons(city,'div', frame, exportPath, title, LegendTitle, "prop_{}".format(attr_value), districtPath=districtPath, neighPath=polyPath, waterPath=waterPath, invertArea= None, addLabels=True)
        """
    
    print("----- Step #6: Calculating and Plotting the total population by neighborhood for ground truth-----")   
    src = gpd.read_file(aggr_outfileSUMGT)   
    exportPath = evalPath + "{0}_{1}_{2}_Polyg.png".format(year,city,attr_value)
    if not os.path.exists(exportPath):
        title ="Population Distribution (persons)\n(source:OIS, buurt)(2018)"
        LegendTitle = "Population (persons)"
        #plot_mapVectorPolygons(city,'popdistributionPolyg', src, exportPath, title, LegendTitle, '{}'.format(attr_value), districtPath = districtPath, neighPath = polyPath, waterPath = waterPath, invertArea = None, addLabels=True)
    


