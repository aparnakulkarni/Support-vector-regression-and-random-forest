import fileIO
import ilwisRasterIO
import visualization
#import utility

from sklearn import metrics
from sklearn import tree

import ilwisobjects as ilwis
import numpy as np
import matplotlib.pyplot as plt

#do not visualize the ilwis messages
ilwis.disconnectIssueLogger()

means=[]
bandmeans=[]
ndvinodatavalue=-10
rdnew=28992
for ndviname in ['T_2009.tif']:
    print ('loading raster')
    ilwis.Engine.setWorkingCatalog(r'D:\xxx\new')
    ndvi=ilwis.RasterCoverage(ndviname)
    csynew=ilwis.CoordinateSystem('epsg:'+str(rdnew))
    ndvi.geoReference().setCoordinateSystem(csynew)
    #georeference="code=georef:type=corners,csy=epsg:"+str(epsg)+",envelope="+str(topleftx)+" "+str(toplefty)+" "+str(bottomrightx)+" "+str(bottomrighty)+",gridsize="+str(width)+" "+str(height)+",cornerofcorners=yes,name="+name

    nbands=ndvi.size().zsize
    print('ndvi has '+str(nbands)+' bands')

    b=ilwisRasterIO.rasterCoverageToIndexedNumpy(ndvi,rdnew, nbands,'bycolumn',ndvinodatavalue)
    print (b[0][0].shape)
    print (b[1].shape)
        
    means.append(b[1].mean())
    xxx=[]
    #dividing the raster into 30 bands each and calculating the mean
    xxx.append(b[1][:,0:30].mean(axis=1))
    xxx.append(b[1][:,30:61].mean(axis=1))    
    xxx.append(b[1][:,61:].mean(axis=1))    
       

    j=0
    for i in xxx:
        c =  b[:1] + (i,)  + b[2:]        
        rc = ilwisRasterIO.indexedNumpyToRasterDataset(c, nodata=-10, returnlist=False)      
        ilwis.Engine.setWorkingCatalog("file:///D:/xxx/new")
        rc.store(ndviname+'_newraster_'+str(j), 'GTiff', 'gdal')
        j+=1
    print (xxx)



   

    
