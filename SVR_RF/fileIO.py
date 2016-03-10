#-------------------------------------------------------------------------------
# Name:        fileIO.py for python 3.3
# Purpose:     fuctions to save/load python objects to/from disk
#

#import sys
#set module path for pydoc documentation
#sys.path.append(r'')

import pickle

def saveObject(f,ob):
    """Save an object on disk
        input: file path, object to save
    """
    out=None
    try:
        out=open(f,'wb')
        pickle.dump(ob,out)
    except Exception as e:
        raise e
    finally:
        if out!=None:
            out.close()

def loadObject(f):
    """Load an object from disk
        input:file path
        output: an object
    """
    a=None
    b=None
    try:
        a=open(f,'rb')
        b=pickle.load(a)
        a.close()
    except Exception as e:
        raise e
    finally:
         if a!=None:
            a.close()
         if b!=None:
            return b
