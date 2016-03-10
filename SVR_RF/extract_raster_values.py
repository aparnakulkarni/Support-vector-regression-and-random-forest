

#points folder
workingcatalog=r'D:\spatial_temporal analytics\Project\Geodatabase'
pointfile='speenkruif_final.shp'
reprojected = 'reprojetedpoints4' #the new folder name with the reprojected points



#raster folder
workingcatalog3=r'D:\xxx\new'
workingcatalog4=r'D:\xxx\new\regressers'
rastername='Ev_2003.tif'

rasternodatavalue=-10
novaluefilter=-10

#projections
ETRS1989=3035
rdnew=28992
#set reprojectpoint to True if you want to reproject points to Rd_new
reprojectpoint=True

import fileIO
import ilwisRasterIO
import visualization
#import utility

from sklearn import metrics
from sklearn import tree

import ilwisobjects as ilwis
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

#do not visualize the ilwis messages
ilwis.disconnectIssueLogger()

try:
    #load the the points
    print('loading points...')
    ilwis.Engine.setWorkingCatalog('file:///'+ workingcatalog)
    pointmap = ilwis.FeatureCoverage(pointfile)
    print(pointmap.coordinateSystem().name())
    print(pointmap.featureCount())
    #reproject the points from WGS84 lat/lon to ETRS1989
##    csynew = ilwis.CoordinateSystem('epsg:'+str(ETRS1989))
##    pointmap.reprojectFeatures(csynew) #this will reprojrct the featurecoverage, does not return a new featurecoverage
##
##    print(pointmap.coordinateSystem().name())
##    print(pointmap.featureCount())
##    pointmap.name('pointfile_reprojected')
##    #save the reproject featurecoverage to the reprojectd folder
##    pointmap.store('file:///'+ workingcatalog4+'/' + reprojected, 'ESRI Shapefile', 'gdal')
##
    #load the raster
    print('loading land cover map...')
    ilwis.Engine.setWorkingCatalog('file:///'+workingcatalog3)
    raster = ilwis.RasterCoverage(rastername)

    # perform the pointrastercrossing operation between points and
    print('crossing points with land use map to get the labels...')
    print('getting values...')

    #get the raster value for each point;
    rastervalues=[]

    for fc in pointmap:
        x = fc.geometry().envelope().maxCorner().x
        y = fc.geometry().envelope().maxCorner().y
        rastervalues.append(raster.coord2value(ilwis.Coordinate(x,y)))

    #import the raster
    print('loading raster...')
    ilwis.Engine.setWorkingCatalog('file:///'+workingcatalog3)
    raster = ilwis.RasterCoverage(rastername)

    #set the raster projection, to fix the problem with some GTiff files
    csynew = ilwis.CoordinateSystem('epsg:'+str(rdnew))
    raster.geoReference().setCoordinateSystem(csynew)

    nbands=raster.size().zsize
    print('raster has '+str(nbands)+' bands')

    if reprojectpoint:
        #reproject the points from ETRS1989  to RD_new
        print('reprojecting points...')

        pointmap.reprojectFeatures(csynew)
        print('crossing points with raster to get the samples ...')

        print('getting values...')
        #get the raster value for each point
        rasterValues=[]
        for fc in pointmap:
            x = fc.geometry().envelope().maxCorner().x
            y = fc.geometry().envelope().maxCorner().y

            print('.', sep=' ',end='')

            #get the pixel object for the x,y coordinates
            pix = raster.geoReference().coord2Pixel(ilwis.Coordinate(x,y))
            #create a list with the band values an append to the main list
            rasterValues.append([raster.pix2value(pix) for b in range(nbands) if not pix.setZ(b)])   # the if not pix.setZ(b) is a trick....

    else:
        #reproject raster to etrs1989
        #raster = utility.reprojectRaster(raster,rdnew,ETRS1989, raster.geoReference().name())
        rasterRepr = raster.reprojectRaster(raster.name()+'_reprojected', 3035, "nearestneighbour")  #possible algorithms "nearestneighbour", "bilinear" , "bicubic"

        print('crossing points with raster to get the samples ...')

        #get the raster value for each point
        rasterValues=[]
        for fc in pointmap:
            x = fc.geometry().envelope().maxCorner().x
            y = fc.geometry().envelope().maxCorner().y

            print('.', end='')

            #get the pixel object for the x,y coordinates
            pix = rasterRepr.geoReference().coord2Pixel(ilwis.Coordinate(x,y))
            #create a list with the band values an append to the main list
            rasterValues.append([rasterRepr.pix2value(pix) for b in range(nbands) if not pix.setZ(b)])   # the if not pix.setZ(b) is a trick....

    print(pointmap.coordinateSystem().name())
    print('there are '+str(pointmap.featureCount())+' crossing points')

    #now we get rid of those points that were outside of the AOI
    print('filtering points...')

    #converting the raster value 1D list to a 2d array with shape ( number of points, 1)
    ValuesArr = np.array(rasterValues).reshape(pointmap.featureCount(),1)
    #converting the ndvi value 2D list to a 2d array with shape (number of points, 23)
    rasterValuesArr = np.array(rasterValues)
    #horizontal stack the 2 arrays to get a 2D array with shape (number of points, 24)
    ar =  np.hstack((ValuesArr, rasterValuesArr))

except Exception as e:
    print (e)














