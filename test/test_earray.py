# Eh! python!, We are going to include isolatin characters here
# -*- coding: latin-1 -*-

import sys
import unittest
import os
import tempfile

from numarray import *
from numarray import strings
from tables import *

try:
    import Numeric
    numeric = 1
except:
    numeric = 0

from test_all import verbose

def allequal(a,b):
    """Checks if two numarrays are equal"""

    if not hasattr(b, "shape"):
        return a == b

    if a.shape <> b.shape:
        if verbose:
            print "Shape is not equal"
        return 0

    if hasattr(b, "type") and a.type() <> b.type():
        return 0

    # Rank-0 case
    if len(a.shape) == 0:
        if str(equal(a,b)) == '1':
            return 1
        else:
            if verbose:
                print "Shape is not equal"
            return 0

    # Null arrays
    if len(a._data) == 0:  # len(a) is not correct for generic shapes
        if len(b._data) == 0:
            return 1
        else:
            if verbose:
                print "length is not equal"
                print "len(a._data) ==>", len(a._data)
                print "len(b._data) ==>", len(b._data)
            return 0

    # Multidimensional case
    result = (a == b)
    for i in range(len(a.shape)):
        result = logical_and.reduce(result)
    if not result and verbose:
        print "The elements are not equal"
        
    return result

class BasicTestCase(unittest.TestCase):
    # Default values
    type = Int32
    shape = (2,0)
    start = 0
    stop = 10
    step = 1
    length = 1
    chunksize = 5
    nappends = 10
    compress = 0
    complib = "zlib"  # Default compression library
    shuffle = 0

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")
        self.rootgroup = self.fileh.root
        self.populateFile()
        # Close the file (eventually destroy the extended type)
        self.fileh.close()
        
    def populateFile(self):
        group = self.rootgroup
        if str(self.type) == "CharType":
            object = strings.array(None, itemsize=self.length,
                                   shape=self.shape)
        else:
            object = zeros(type=self.type, shape=self.shape)
        title = self.__class__.__name__
        earray = self.fileh.createArray(group, 'earray1', object, title,
                                        compress = self.compress,
                                        complib = self.complib,
                                        shuffle = self.shuffle,
                                        expectedrows = 1)

        # Fill it with rows
        self.rowshape = list(earray.shape)
        self.objsize = self.length
        for i in self.rowshape:
            if i <> 0:
                self.objsize *= i
        self.extdim = earray.extdim
        self.objsize *= self.chunksize
        self.rowshape[earray.extdim] = self.chunksize
        if str(self.type) == "CharType":
            object = strings.array("a"*self.objsize, shape=self.rowshape,
                                   itemsize=earray.itemsize)
        else:
            object = arange(self.objsize, shape=self.rowshape,
                            type=earray.type)
        if verbose:
            print "Object to append -->", object.info()
        for i in range(self.nappends):
            if str(self.type) == "CharType":
                earray.append(object)
            else:
                earray.append(object*i)

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        
    #----------------------------------------

    def test01_iterArray(self):
        """Checking enlargeable array iterator"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_iterArray..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "Array descr:", repr(earray)
            print "shape of read array ==>", earray.shape
        # Build the array to do comparisons
        if str(self.type) == "CharType":
            object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                   itemsize=earray.itemsize)
        else:
            object_ = arange(self.objsize, shape=self.rowshape,
                             type=earray.type)
        object_.swapaxes(earray.extdim, 0)
        # Read all the array
        for row in earray:
            chunk = (earray.nrow % self.chunksize)
            if chunk == 0:
                if str(self.type) == "CharType":
                    object__ = object_
                else:
                    object__ = object_ * (earray.nrow / self.chunksize)
            object = object__[chunk]
            # The next adds much more verbosity
            if verbose and 0:
                print "number of row ==>", earray.nrow
                if hasattr(object, "shape"):
                    print "shape should look as:", object.shape
                print "row in earray ==>", repr(row)
                print "Should look like ==>", repr(object)

            assert self.nappends*self.chunksize == earray.nrows
            assert allequal(row, object)
            if hasattr(row, "shape"):
                assert len(row.shape) == len(self.shape) - 1
            else:
                # Scalar case
                assert len(self.shape) == 1

    def test02_sssArray(self):
        """Checking enlargeable array iterator with (start, stop, step)"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_sssArray..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "Array descr:", repr(earray)
            print "shape of read array ==>", earray.shape
        # Build the array to do comparisons
        if str(self.type) == "CharType":
            object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                   itemsize=earray.itemsize)
        else:
            object_ = arange(self.objsize, shape=self.rowshape,
                             type=earray.type)
        object_.swapaxes(earray.extdim, 0)
        # Read all the array
        for row in earray(start=self.start, stop=self.stop, step=self.step):
            chunk = (earray.nrow % self.chunksize)
            if (chunk - self.start) == 0:
                if str(self.type) == "CharType":
                    object__ = object_
                else:
                    object__ = object_ * (earray.nrow / self.chunksize)
            object = object__[chunk]
            # The next adds much more verbosity
            if verbose and 0:
                print "number of row ==>", earray.nrow
                if hasattr(object, "shape"):
                    print "shape should look as:", object.shape
                print "row in earray ==>", repr(row)
                print "Should look like ==>", repr(object)

            assert self.nappends*self.chunksize == earray.nrows
            assert allequal(row, object)
            if hasattr(row, "shape"):
                assert len(row.shape) == len(self.shape) - 1
            else:
                # Scalar case
                assert len(self.shape) == 1

    def test03_readArray(self):
        """Checking read() of enlargeable arrays"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_readArray..." % self.__class__.__name__
            
        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "Array descr:", repr(earray)
            print "shape of read array ==>", earray.shape

        # Build the array to do comparisons
        if str(self.type) == "CharType":
            object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                   itemsize=earray.itemsize)
        else:
            object_ = arange(self.objsize, shape=self.rowshape,
                             type=earray.type)
        object_.swapaxes(earray.extdim, 0)
        rowshape = self.rowshape
        rowshape[self.extdim] *= self.nappends
        if str(self.type) == "CharType":
            object__ = strings.array(None, shape=rowshape,
                                     itemsize=earray.itemsize)
        else:
            object__ = array(None, shape = rowshape, type=self.type)
        object__.swapaxes(0, self.extdim)
        for i in range(self.nappends):
            j = i * self.chunksize
            if str(self.type) == "CharType":
                object__[j:j+self.chunksize] = object_
            else:
                object__[j:j+self.chunksize] = object_ * i
        stop = self.stop
        if self.nappends:
            # Protection against number of elements less than existing
            if rowshape[self.extdim] < self.stop or self.stop == 0:
                # self.stop == 0 means last row
                stop = rowshape[self.extdim]
            # do a copy() in order to ensure that len(object._data)
            # actually do a measure of its length
            object = object__[self.start:stop:self.step].copy()
            # Swap the axes again to have normal ordering
            object.swapaxes(0, self.extdim)
        else:
            object = array(None, shape = self.shape, type=self.type)

        # Read all the array
        try:
            row = earray.read(self.start,self.stop,self.step)
        except IndexError:
            row = array(None, shape = self.shape, type=self.type)

        if verbose:
            if hasattr(object, "shape"):
                print "shape should look as:", object.shape
            print "Object read ==>", repr(row)
            print "Should look like ==>", repr(object)

        assert self.nappends*self.chunksize == earray.nrows
        assert allequal(row, object)
        if hasattr(row, "shape"):
            assert len(row.shape) == len(self.shape)
        else:
            # Scalar case
            assert len(self.shape) == 1

    def test04_getitemArray(self):
        """Checking enlargeable array __getitem__ special method"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_getitemArray..." % self.__class__.__name__
            
        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        earray = self.fileh.getNode("/earray1")

        # Choose a small value for buffer size
        earray._v_maxTuples = 3
        if verbose:
            print "Array descr:", repr(earray)
            print "shape of read array ==>", earray.shape

        # Build the array to do comparisons
        if str(self.type) == "CharType":
            object_ = strings.array("a"*self.objsize, shape=self.rowshape,
                                   itemsize=earray.itemsize)
        else:
            object_ = arange(self.objsize, shape=self.rowshape,
                             type=earray.type)
        object_.swapaxes(earray.extdim, 0)
        rowshape = self.rowshape
        rowshape[self.extdim] *= self.nappends
        if str(self.type) == "CharType":
            object__ = strings.array(None, shape=rowshape,
                                     itemsize=earray.itemsize)
        else:
            object__ = array(None, shape = rowshape, type=self.type)
        object__.swapaxes(0, self.extdim)
        for i in range(self.nappends):
            j = i * self.chunksize
            if str(self.type) == "CharType":
                object__[j:j+self.chunksize] = object_
            else:
                object__[j:j+self.chunksize] = object_ * i
        stop = self.stop
        if self.nappends:
            # Protection against number of elements less than existing
            if rowshape[self.extdim] < self.stop or self.stop == 0:
                # self.stop == 0 means last row
                stop = rowshape[self.extdim]
            # do a copy() in order to ensure that len(object._data)
            # actually do a measure of its length
            object = object__[self.start:stop:self.step].copy()
            # Swap the axes again to have normal ordering
            object.swapaxes(0, self.extdim)
        else:
            object = array(None, shape = self.shape, type=self.type)

        if (len(range(self.start, stop, self.step)) == 1 and
            self.extdim > 0):
            object.swapaxes(self.extdim, 0)
            object = object[0]
            correction = 1
        else:
            correction = 0
                
        # Read all the array
        try:
            row = earray[self.start:self.stop:self.step]
        except IndexError:
            row = array(None, shape = self.shape, type=self.type)

        if verbose:
            if hasattr(object, "shape"):
                print "shape should look as:", object.shape
            print "Object read ==>", repr(row) #, row.info()
            print "Should look like ==>", repr(object) #, row.info()

        assert self.nappends*self.chunksize == earray.nrows
        assert allequal(row, object)
        if hasattr(row, "shape"):
            assert len(row.shape) == len(self.shape) - correction
        else:
            # Scalar case
            assert len(self.shape) == 1


class BasicWriteTestCase(BasicTestCase):
    type = Int32
    shape = (0,)
    chunksize = 5
    nappends = 10
    step = 1

class EmptyArrayTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0)
    chunksize = 5
    nappends = 0
    start = 0
    step = 1

class MD3WriteTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0, 3)
    chunksize = 4
    step = 2

class MD5WriteTestCase(BasicTestCase):
    type = Int32
    shape = (2, 0, 3, 4, 5)  # ok
    #shape = (1, 1, 0, 1)  # Minimum shape that shows problems with HDF5 1.6.1
    #shape = (2, 3, 0, 4, 5)  # Floating point exception (HDF5 1.6.1)
    #shape = (2, 3, 3, 0, 5, 6) # Segmentation fault (HDF5 1.6.1)
    chunksize = 1
    nappends = 1
    start = 1
    stop = 10
    step = 10

class MD10WriteTestCase(BasicTestCase):
    type = Int32
    shape = (1, 2, 3, 4, 5, 5, 4, 3, 2, 0)
    chunksize = 5
    nappends = 10
    start = -1
    stop = -1
    step = 10

class ZlibComprTestCase(BasicTestCase):
    compress = 1
    complib = "zlib"
    start = 3
    stop = 0   # means last row
    step = 10

class ZlibShuffleTestCase(BasicTestCase):
    shuffle = 1   # That should be enough to activate the compression
    complib = "zlib"
    # case start < stop , i.e. no rows read
    start = 3
    stop = 1
    step = 10

class LZOComprTestCase(BasicTestCase):
    compress = 1
    complib = "lzo"
    chunksize = 10
    nappends = 100
    start = 3
    stop = 10
    step = 3

class LZOShuffleTestCase(BasicTestCase):
    compress = 1
    shuffle = 1
    complib = "lzo"
    chunksize = 100
    nappends = 10
    start = 3
    stop = 10
    step = 7

class UCLComprTestCase(BasicTestCase):
    compress = 1
    complib = "ucl"
    chunksize = 100
    nappends = 10
    start = 3
    stop = 10
    step = 8

class UCLShuffleTestCase(BasicTestCase):
    compress = 1
    shuffle = 1
    complib = "ucl"
    chunksize = 100
    nappends = 10
    start = 3
    stop = 10
    step = 6

class FloatTypeTestCase(BasicTestCase):
    type = Float64
    shape = (2,0)
    chunksize = 5
    nappends = 10
    start = 3
    stop = 10
    step = 20

class CharTypeTestCase(BasicTestCase):
    type = "CharType"
    length = 20
    shape = (2,0)
    chunksize = 5
    nappends = 10
    start = 3
    stop = 10
    step = 20

class CharType2TestCase(BasicTestCase):
    type = "CharType"
    length = 20
    shape = (0,)
    chunksize = 5
    nappends = 10
    start = 1
    stop = 10
    step = 2

class CharTypeComprTestCase(BasicTestCase):
    type = "CharType"
    length = 20
    shape = (20,0,10)
    compr = 1
    #shuffle = 1  # this should not do nothing on chars
    chunksize = 50
    nappends = 10
    start = -1
    stop = 100
    step = 20


#----------------------------------------------------------------------

def suite():
    theSuite = unittest.TestSuite()
    global numeric
    niter = 1

    #theSuite.addTest(unittest.makeSuite(BasicWriteTestCase))
    #theSuite.addTest(unittest.makeSuite(EmptyArrayTestCase))
    #theSuite.addTest(unittest.makeSuite(MD3WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(MD5WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(MD10WriteTestCase))
    #theSuite.addTest(unittest.makeSuite(ZlibComprTestCase))
    #theSuite.addTest(unittest.makeSuite(ZlibShuffleTestCase))
    #theSuite.addTest(unittest.makeSuite(LZOComprTestCase))
    #theSuite.addTest(unittest.makeSuite(LZOShuffleTestCase))
    #theSuite.addTest(unittest.makeSuite(UCLComprTestCase))
    #theSuite.addTest(unittest.makeSuite(UCLShuffleTestCase))
    #theSuite.addTest(unittest.makeSuite(FloatTypeTestCase))
    #theSuite.addTest(unittest.makeSuite(CharTypeTestCase))
    #theSuite.addTest(unittest.makeSuite(CharType2TestCase))
    #theSuite.addTest(unittest.makeSuite(CharTypeComprTestCase))

    for n in range(niter):
        theSuite.addTest(unittest.makeSuite(BasicWriteTestCase))
        theSuite.addTest(unittest.makeSuite(EmptyArrayTestCase))
        theSuite.addTest(unittest.makeSuite(MD3WriteTestCase))
        theSuite.addTest(unittest.makeSuite(MD5WriteTestCase))
        theSuite.addTest(unittest.makeSuite(MD10WriteTestCase))
        theSuite.addTest(unittest.makeSuite(ZlibComprTestCase))
        theSuite.addTest(unittest.makeSuite(ZlibShuffleTestCase))
        theSuite.addTest(unittest.makeSuite(LZOComprTestCase))
        theSuite.addTest(unittest.makeSuite(LZOShuffleTestCase))
        theSuite.addTest(unittest.makeSuite(UCLComprTestCase))
        theSuite.addTest(unittest.makeSuite(UCLShuffleTestCase))
        theSuite.addTest(unittest.makeSuite(FloatTypeTestCase))
        theSuite.addTest(unittest.makeSuite(CharTypeTestCase))    
        theSuite.addTest(unittest.makeSuite(CharType2TestCase))    
        theSuite.addTest(unittest.makeSuite(CharTypeComprTestCase))

    return theSuite


if __name__ == '__main__':
    unittest.main( defaultTest='suite' )