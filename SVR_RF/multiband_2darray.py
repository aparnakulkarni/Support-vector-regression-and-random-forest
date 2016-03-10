

import numpy as np
import ilwisobjects as ilw

def describeRasterCoverage(raster, epsg):
    """Get the properties of a raster coverage
        input: a raster coverage, projection epsg code (we pass the code because of a ilwis bug)
        output:return the properties of a raster coverage (height,width,georeference string)
    """
    height=raster.size().ysize
    print(height)
    width=raster.size().xsize
    g=raster.geoReference()
    topleft=g.pixel2Coord(ilw.Pixel(1,1))
    topleftx=topleft.x
    toplefty=topleft.y
    bottomright=g.pixel2Coord(ilw.Pixel(width-1,height-1))
    bottomrightx=bottomright.x
    bottomrighty=bottomright.y
    pixelsizeh=abs(((bottomright.x-topleftx)/(width-1)/2))
    topleftx=topleft.x - pixelsizeh
    toplefty=topleft.y + pixelsizeh    #this might not work in the southern emisphere
    bottomrightx=bottomright.x + pixelsizeh
    bottomrighty=bottomright.y - pixelsizeh   #this might not work in the southern emisphere
    name=raster.name().split('.')[0]
    georeference="code=georef:type=corners,csy=epsg:"+str(epsg)+",envelope="+str(topleftx)+" "+str(toplefty)+" "+str(bottomrightx)+" "+str(bottomrighty)+",gridsize="+str(width)+" "+str(height)+",cornerofcorners=yes,name="+name

    return width,height,name,georeference

def singleBandToIndexedNumpy(rasteriterator,nodata=-1e+308, returnIndex=True):
    """ Convert an raster coverage band into an indexed array
        input: ilwis raster coverage band,no data value, a bool to return the array index
        output: the tuple with the index as numpy array (if returnindex=True), the indexed numpy array
    """
    try:
        band = np.fromiter(rasteriterator, np.float, rasteriterator.box().size().xsize * rasteriterator.box().size().ysize)
        index=np.nonzero(band > nodata)
        rIndexed=band[index]
        if returnIndex:
            return index,rIndexed
        else:
            return rIndexed
    except Exception as e:
        raise e

def rasterCoverageToIndexedNumpy(raster,epsgcode, maxbands=100, bandLocation='bycolumn', nodata=-1e+308):
    """Convert a multiband raster coverage into an indexed array
        input: raster coverage,the epsg code, the number of bands to consider, how to store bands (possible values: 'byrow' , 'bycolumn')
        output: the index, the 2D indexed array, dictionary with raster properties (the properties of the first band)
    """
    if maxbands<1: raise Exception('number of bands should be >=1!!!')
    if not (bandLocation=='byrow' or bandLocation=='bycolumn'):
        raise Exception("you need the specify the correct 'bandLocation' argument!!!")
    try:
        #describe the band and set a dictionary with the raster properties
        width,height,name,georeference=describeRasterCoverage(raster,epsgcode)
        properties={'columns': width,'rows':height,'name':name,'spatialref':georeference}
        #get the number of bands
        nbands=raster.size().zsize
        print ('This raster has '+str(nbands)+' bands')
        # set the number of bands to process
        if maxbands<=nbands: nbands=100
        print ('STOP')
        print ('We are processing '+str(nbands)+' bands')
        properties['nbands']=100  #store the number of bands
        #create a pixel iterator
        print ("Preparing to process bands....")
        it = iter(raster)
        rIndexed=list()
        print ("Processing rasters")
        #for the first raster I get also the index (this is supposed to be the same for all the bands)
        i,rI=singleBandToIndexedNumpy(it,nodata)
        index=i
        print ('1')
        rIndexed.append(rI)
        #now loop the remaining bands
        for band in range(1,101):
            #for the other bands I don't take the index because it is always the same
            rI=singleBandToIndexedNumpy(it,nodata,returnIndex=False)
            print (str(band+1))
            rIndexed.append(rI)
        if bandLocation=='bycolumn':
            # create a 2darray, each row is a pixel, each column is a band
            rIndexed=np.vstack(rIndexed).T
        else:
            # create a 2darray, each row is a band, each column is a pixel
            rIndexed=np.vstack(rIndexed)
        #store the band structure (byrow or bycolumn)
        properties['band']=bandLocation
        return index,rIndexed,properties
    except Exception as e:
        raise e

def rasterListToIndexedNumpy(rasterlist,epsgcode,bandLocation='bycolumn', nodata=-1e+308):
    """Convert a list of single band raster coverages into in indexed array
        input: list of raster coverage, the epsg code, how to store bands (possible values: 'byrow' , 'bycolumn')
        output: the index, the 2d indexed array , dictionary with raster properties  (the properties of the first raster coverage in the list)
    """
    if len(rasterlist)<2: raise Exception('number of bands should be >=2!!!')
    if not (bandLocation=='byrow' or bandLocation=='bycolumn'): raise Exception("you need the specify the correct 'bandLocation' argument!!!")
    try:
        #describe the first raster coverage and set a dictionary with the raster properties
        width,height,name,georeference=describeRasterCoverage(rasterlist[0],epsgcode)
        properties={'columns': width,'rows':height,'name':name,'spatialref':georeference}
        #get the number of rasters
        nrasters=len(rasterlist)
        print ('This list has '+str(nrasters)+' rasters')
        #store the number of bands
        properties['nbands']= nrasters
        #create a pixel iterator
        print ("Preparing to process rasters....")
        raster=rasterlist[0]
        it = iter(raster)
        rIndexed=list()
        print ("Processing bands")
        #for the first raster I get also the index (this are supposed to be the same for all the bands)
        i,rI=singleBandToIndexedNumpy(it,nodata)
        index=i
        print ('1')
        rIndexed.append(rI)
        idx=1
        #now loop the remaining rasters
        for rast in range(1,nrasters):
            raster=rasterlist[idx]
            #create a new pixel iterator
            it = iter(raster)
            #for the other rasters I don't take the index because it is always the same
            rI=singleBandToIndexedNumpy(it,nodata,returnIndex=False)
            print (str(rast+1))
            rIndexed.append(rI)
            idx+=1
        if bandLocation=='bycolumn':
            # create a 2darray, each row is a pixel, each column is a band
            rIndexed=np.vstack(rIndexed).T
        else:
            # create a 2darray, each row is a band, each column is a pixel
            rIndexed=np.vstack(rIndexed)
        #store the band structure (byrow or bycolumn)
        properties['band']=bandLocation
        return index,rIndexed,properties
    except Exception as e:
        raise e

def indexedNumpyToRasterDataset(c, nodata=-1e+308, returnlist=True):
    """Create a raster dataset from an indexed numpy array
        input:  input tuple (index+indexed array+properties dictionary), nodata value, return a list with the bands?
        output: a raster coverage, may return a list where each element as a 1dimensional array for each raster band
    """
    try:
        print('initializing new raster...')
        #Create range
        nr = ilw.NumericRange(0.0, 100000000.0, 0.00001)
        #Create empty Numeric Domain
        numdom = ilw.NumericDomain()
        #Set range of new domain
        numdom.setRange(nr)
        df = ilw.DataDefinition(numdom, nr)
        #initialize new raster coverage
        rc = ilw.RasterCoverage()
        georef = ilw.GeoReference(c[2]['spatialref'])
        rc.setGeoReference(georef)
        rc.setDataDef(df)
        #initialize a support raster coverage
        rc2 = ilw.RasterCoverage()
        rc2.setGeoReference(georef)
        rc2.setDataDef(df)

        #get the number of bands
        if c[1].ndim==1: nbands=1
        #else: nbands=c[1].shape[1]

        # bands were stores bycolumn or byrow
        else:
            if c[2]['band'] == 'byrow':
                nbands=c[1].shape[0]
            else: nbands=c[1].shape[1]

        print ('This array has '+str(nbands)+' bands')
        #create a list to store the bands
        if returnlist:bands=[]
        #create band by band
        print('getting band data....')
        for i in range(nbands):
            itNew = rc2.begin()



            #set an empty numpy array for the band
            a = np.zeros((c[2]['rows']*c[2]['columns']))+nodata
            #fill np array with data from the indexed np array using the index
            if c[1].ndim>1:
                if c[2]['band']=='bycolumn':
                    #a[c[0]] = c[1][:,i].flatten() #flatten will always make a copy
                    a[c[0]] = c[1][:,i].ravel()
                else: #byrows
                    #a[c[0]] = c[1][i,:].flatten()
                    a[c[0]] = c[1][i,:].ravel()
            else: #single band raster
                a[c[0]] = c[1][:].flatten()
            #print (a)
            #print (a.shape[0])

            if returnlist:bands.append(a)
            #fill iterator with pixel data
            for y in range(a.shape[0]):
                itNew[y] = a[y]

            print ('adding band'+ str(i))
            #for bands other than the first add the band


            '''
            if i > 0:
                rc.addBand(i+1, rc2.begin())
            else: rc.addBand(1, rc.begin())
            '''

            rc.addBand(i, rc2.begin())


        if returnlist:
            return bands,rc
        else:
            return rc

    except Exception as e:
        raise e

if __name__ == '__main__':

    #import sys
    #sys.path.append('E:\ITC\module13GFM2\module13\exploratoryAnalysis')
    #sys.path.append('E:\ITC\module13GFM2\module13\code\codepy3')
    import fileIO
    import ilwisobjects as ilw

    #test for raster properties
    def describeRaster():
        ilw.Engine.setWorkingCatalog("file:///D:/xxx/new")
        raster = ilw.RasterCoverage("T_2010_all_warp.bsq")
        #raster = ilw.RasterCoverage("2003.tif")
        return describeRasterCoverage(raster,28992)

    #test for 1 band
    def importSingleBand():
        try:
            ilw.Engine.setWorkingCatalog("file:///D:/xxx/new")
            raster = ilw.RasterCoverage("T_2010_all_warp.bsq")
            print ('creating pixel iterator')
            it = iter(raster)
            print ('exporting to indexed numpy array')
            a=singleBandToIndexedNumpy(it)
            print ('saving object to disk')
            fileIO.saveObject('D:/xxx/new/T_2010_single',a)
            print ('loading object from disk')
            c=fileIO.loadObject('D:/xxx/new/T_2010_single')
            return a,c

        except Exception as e:
            print (e)

    #test for multiband
    def importRaster():
        try:
            ilw.Engine.setWorkingCatalog("file:///D:/xxx/new")
            raster = ilw.RasterCoverage("T_2010_all_warp.bsq")
            b=rasterCoverageToIndexedNumpy(raster,28992,366,'bycolumn')
            print ('saving object to disk')
            fileIO.saveObject('D:/xxx/new/T_2010_all_warp',b)
            print ('loading object from disk')
            c=fileIO.loadObject('D:/xxx/new/T_2010_all_warp')
            return b,c

        except Exception as e:
            print (e)

    #test for multiband
    def importSingleBandRaster():
        try:
            ilw.Engine.setWorkingCatalog("file:///D:/xxx/new")
            raster = ilw.RasterCoverage("T_2010_all_warp.bsq")
            b=rasterCoverageToIndexedNumpy(raster,28992,1,'bycolumn')
            print ('saving object to disk')
            fileIO.saveObject('D:/xxx/T_2010_all_warp_1',b)
            print ('loading object from disk')
            c=fileIO.loadObject('D:/xxx/T_2010_all_warp_1')
            return b,c

        except Exception as e:
            print (e)

    #test for exporting indexed array
    def exportRaster():
        try:
            #ilw.Engine.setWorkingCatalog("file:///C:/xxx/new")
            ilw.Engine.setWorkingCatalog("file:///D:/xxx/new")
            print ('loading object from disk')
            c=fileIO.loadObject('D:/xxx/new/T_2010_all_warp')
            #c=fileIO.loadObject('C:/xxx/randomforest')
            bands=indexedNumpyToRasterDataset(c,nodata=-10, returnlist=True)
            bands[1].store('newraster', 'GTiff', 'gdal')
            return bands

        except Exception as e:
            print (e)

    descr=describeRaster()
    single=importSingleBand()
    multi=importRaster()
    single2=importSingleBandRaster()
    raster=exportRaster()
    #toreRaster(raster[1], outputdir='D:/xxx/new', rastername='newraster', form='GTiff')
    #raster[1].store('file:///D:/xxx/new/newraster', 'GTiff', 'gdal')
