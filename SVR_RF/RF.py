#-------------------------------------------------------------------------------
# Name:        SVR
# Purpose:     import training data, train SVR regressor,
#               and perform regression
#


import fileIO
import ilwisRasterIO
import importData
from sklearn.svm import SVR
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVR
from sklearn.ensemble import RandomForestRegressor

import ilwisobjects as ilwis
import numpy as np
import matplotlib.pyplot as plt

#####setting varialbes########

#input raster folder
workingcatalog = "D:/"
#output folder
workingcatalog2 = "D:/"

inputraster='2003.bsq'

bandstoimport=100
innodatavalue = -10

#binaryfile='2003'

outnodatavalue = 0

#classified image outputs
#outname='chl'
##outname2='lai'
##outname3='fcover'
frmt='GTiff'
outname='DOY_RF'

#code for UTM30/ED50
epsg = 28992


#do not visualize the ilwis messages
ilwis.disconnectIssueLogger()

print('importing training data...')
training,trainingLabels,test,testLabels = importData.shuffleData(r'D:\matrix_trainning.csv',percentage=25,sep=',',label=True)


#############train regressor##############

def rmse(predictions, targets):
    return '%.2f'% np.sqrt(((predictions - targets) ** 2).mean())


def train(samples,labels,test,testLabels):
    print('train regressor...')
    #we are using the default rbf kernel



    #define a gridsearch  (the parameters of the regressor used to predict are optimized by cross-validation)
    rf=RandomForestRegressor(n_estimators=20,n_jobs=-1)
    rf.fit(samples,labels)

    #predict the value using the samples....
    y_pred = rf.predict(test)
    plt.plot( testLabels - y_pred)
    plt.title('RMSE ='+ rmse(y_pred, testLabels))
    plt.show()

    return rf

chTrained = train(training,np.array(trainingLabels).astype(int),test,np.array(testLabels).astype(int))

#####import multiband image#######

'''
print ('indexing multiband raster...')
def saveimage():
    ilwis.Engine.setWorkingCatalog('file:///'+workingcatalog)
    raster = ilwis.RasterCoverage(inputraster)
    b=ilwisRasterIO.rasterCoverageToIndexedNumpy(raster, epsg, bandstoimport, 'bycolumn', innodatavalue)
    print ('saving object to disk')
    fileIO.saveObject(workingcatalog2+'/'+binaryfile,b)

#you can comment this out once is done once
saveimage()
'''
ilwis.Engine.setWorkingCatalog('file:///'+workingcatalog)
raster = ilwis.RasterCoverage(inputraster)
inputdata=ilwisRasterIO.rasterCoverageToIndexedNumpy(raster, epsg, bandstoimport, 'bycolumn', innodatavalue)
print ("loading the indexed array from disk...")
#load the indexed array from disk (you created one with ilwisRasterIO.py)
#inputdata=fileIO.loadObject(workingcatalog2+'/'+binaryfile)

####classify image; export image##########

def classify(inputdata, classifier, outnodatavalue, outputpath, outname, frmt):

    print ('classify raster, wait...')

    #use only the indexed array inputdata[0] is the index, inputdata[1] the indexed array,
    #inputdata[2] the raster properties
    y_predKNN = classifier.predict(inputdata[1])

    #set negative values to zero
    y_predKNN[y_predKNN <0] = 0

    #export back to raster
    #replace the indexed array with the classifiction result
    c = inputdata[:1]+(y_predKNN,)+inputdata[2:]

    print ("saving the result to raster....")

    #save the indexed array as an array, get a list of bands arrays, here I use -10 as the nodata
    raster= ilwisRasterIO.indexedNumpyToRasterDataset(c, nodata=outnodatavalue, returnlist=True)

    #visualize the result with matplotlib
    print ("visualizing result....")
    rows=inputdata[2]['rows']
    columns=inputdata[2]['columns']
    gg=raster[0][0].reshape((rows,columns))

    plt.imshow(gg)
    plt.show()

    print ('exporting raster to disk')
    #to export is necessary to set the working catalog
    ilwis.Engine.setWorkingCatalog('file:///'+outputpath)
    raster[1].store(outname, frmt, 'gdal')

#chl
classify(inputdata, chTrained, outnodatavalue, workingcatalog2, outname, frmt)
