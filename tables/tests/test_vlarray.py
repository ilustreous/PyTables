# Eh! python!, We are going to include isolatin characters here
# -*- coding: latin-1 -*-

# Comments: Adapted to the new set of flavors:
# "numarray", "numpy", "numeric", "python", "Object" and "VLString"

import sys
import unittest
import os
import tempfile
import warnings

from numarray import *
import numarray.strings as strings
from tables import *

try:
    import Numeric
    numeric = 1
except:
    numeric = 0

try:
    import numpy
    numpy_imported = 1
except:
    numpy_imported = 0

import common
from common import verbose, allequal, cleanup
# To delete the internal attributes automagically
unittest.TestCase.tearDown = cleanup

class C:
    c = (3,4.5)

class BasicTestCase(unittest.TestCase):
    compress = 0
    complib = "zlib"
    shuffle = 0
    fletcher32 = 0
    flavor = "numarray"

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, "w")
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def populateFile(self):
        group = self.rootgroup
        filters = Filters(complevel = self.compress,
                          complib = self.complib,
                          shuffle = self.shuffle,
                          fletcher32 = self.fletcher32)
        vlarray = self.fileh.createVLArray(group, 'vlarray1',
                                           Int32Atom(flavor=self.flavor),
                                           "ragged array if ints",
                                           filters = filters,
                                           expectedsizeinMB = 1)

        # Fill it with 5 rows
        vlarray.append([1, 2])
        if self.flavor == "numarray":
            vlarray.append(array([3, 4, 5], type=Int32))
            vlarray.append(array([], type=Int32))    # Empty entry
        elif self.flavor == "numpy":
            vlarray.append(numpy.array([3, 4, 5], dtype='int32'))
            vlarray.append(numpy.array([], dtype='int32'))     # Empty entry
        elif self.flavor == "numeric":
            vlarray.append(Numeric.array([3, 4, 5], typecode='i'))
            vlarray.append(Numeric.array([], typecode='i'))     # Empty entry
        elif self.flavor == "python":
            vlarray.append((3, 4, 5))
            vlarray.append(())         # Empty entry
        vlarray.append([6, 7, 8, 9])
        vlarray.append([10, 11, 12, 13, 14])

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test01_readVLArray(self):
        """Checking vlarray read"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_readVLArray..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.getNode("/vlarray1")

        # Choose a small value for buffer size
        vlarray._v_maxTuples = 3
        # Read some rows
        row = vlarray[0]
        row2 = vlarray[2]
        if verbose:
            print "Flavor:", vlarray.flavor
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row

        nrows = 5
        assert nrows == vlarray.nrows
        if self.flavor == "numarray":
            assert allequal(row, array([1, 2], type=Int32))
            assert allequal(row2, array([], type=Int32))
        elif self.flavor == "numpy":
            assert type(row) == type(numpy.array([1, 2]))
            assert allequal(row, numpy.array([1, 2], dtype='int32'), self.flavor)
            assert allequal(row2, numpy.array([], dtype='int32'), self.flavor)
        elif self.flavor == "numeric":
            assert type(row) == type(Numeric.array([1, 2]))
            # The next two lines has been corrected by Ciro Catutto
            # (2004-04-20)
            assert allequal(row, (1, 2), self.flavor)
            assert allequal(row2, Numeric.array([], typecode='i'), self.flavor)
        elif self.flavor == "python":
            assert row == [1, 2]
            assert row2 == []
        assert len(row) == 2

        # Check filters:
        if self.compress <> vlarray.filters.complevel and verbose:
            print "Error in compress. Class:", self.__class__.__name__
            print "self, vlarray:", self.compress, vlarray.filters.complevel
        tinfo = whichLibVersion(self.complib)
        if tinfo is None:
            self.complib = "zlib"
        assert vlarray.filters.complib == self.complib
        assert vlarray.filters.complevel == self.compress
        if self.shuffle <> vlarray.filters.shuffle and verbose:
            print "Error in shuffle. Class:", self.__class__.__name__
            print "self, vlarray:", self.shuffle, vlarray.filters.shuffle
        assert self.shuffle == vlarray.filters.shuffle
        if self.fletcher32 <> vlarray.filters.fletcher32 and verbose:
            print "Error in fletcher32. Class:", self.__class__.__name__
            print "self, vlarray:", self.fletcher32, vlarray.filters.fletcher32
        assert self.fletcher32 == vlarray.filters.fletcher32

    def test02_appendVLArray(self):
        """Checking vlarray append"""

        rootgroup = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_appendVLArray..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.getNode("/vlarray1")
        # Append a new row
        vlarray.append([7, 8, 9, 10])

        # Choose a small value for buffer size
        vlarray._v_maxTuples = 3
        # Read some rows:
        row1 = vlarray[0]
        row2 = vlarray[2]
        row3 = vlarray[-1]
        if verbose:
            print "Flavor:", vlarray.flavor
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row1

        nrows = 6
        assert nrows == vlarray.nrows
        if self.flavor == "numarray":
            assert allequal(row1, array([1, 2], type=Int32))
            assert allequal(row2, array([], type=Int32))
            assert allequal(row3, array([7, 8, 9, 10], type=Int32))
        elif self.flavor == "numpy":
            assert type(row1) == type(numpy.array([1, 2]))
            assert allequal(row1, numpy.array([1, 2], dtype='int32'), self.flavor)
            assert allequal(row2, numpy.array([], dtype='int32'), self.flavor)
            assert allequal(row3, numpy.array([7, 8, 9, 10], dtype='int32'),
                            self.flavor)
        elif self.flavor == "numeric":
            assert type(row1) == type(Numeric.array([1, 2]))
            # The next two lines has been corrected by Ciro Catutto
            # (2004-04-20)
            assert allequal(row1, (1, 2), self.flavor)
            assert allequal(row2, Numeric.array([], typecode='i'), self.flavor)
            assert allequal(row3, Numeric.array([7, 8, 9, 10], typecode='i'),
                            self.flavor)
        elif self.flavor == "python":
            assert row1 == [1, 2]
            assert row2 == []
            assert row3 == [7, 8, 9, 10]
        assert len(row3) == 4


class BasicNumArrayTestCase(BasicTestCase):
    flavor = "numarray"

class BasicNumpyTestCase(BasicTestCase):
    flavor = "numpy"

class BasicNumericTestCase(BasicTestCase):
    flavor = "numeric"

class BasicPythonTestCase(BasicTestCase):
    flavor = "python"

class ZlibComprTestCase(BasicTestCase):
    compress = 1
    complib = "zlib"

class LZOComprTestCase(BasicTestCase):
    compress = 1
    complib = "lzo"

class BZIP2ComprTestCase(BasicTestCase):
    compress = 1
    complib = "bzip2"

class ShuffleComprTestCase(BasicTestCase):
    compress = 1
    shuffle = 1

class Fletcher32TestCase(BasicTestCase):
    fletcher32 = 1

class AllFiltersTestCase(BasicTestCase):
    compress = 1
    shuffle = 1
    fletcher32 = 1

class TypesTestCase(unittest.TestCase):
    mode  = "w"
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test01_StringAtom(self):
        """Checking vlarray with numarray string atoms (numarray flavor)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, flavor="numarray"),
                                           "Ragged array of strings")
        vlarray.append(strings.array(["1", "12", "123", "1234", "12345"]))
        vlarray.append(strings.array(["1", "12345"]))

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], strings.array(["1", "12", "123", "123", "123"]))
        assert allequal(row[1], strings.array(["1", "123"]))
        assert len(row[0]) == 5
        assert len(row[1]) == 2

    def test01_1_StringAtom(self):
        """Checking vlarray with numarray string atoms (numpy flavor)"""

        if not numpy_imported:
            return

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_1_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, flavor="numpy"),
                                           "Ragged array of strings")
        vlarray.append(numpy.array(["1", "12", "123", "1234", "12345"], dtype="S"))
        vlarray.append(numpy.array(["1", "12345"], dtype="S"))

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], numpy.array(["1", "12", "123", "123", "123"],
                                            dtype="S"), flavor="numpy")
        assert allequal(row[1], numpy.array(["1", "123"], dtype="S"), flavor="numpy")
        assert len(row[0]) == 5
        assert len(row[1]) == 2

    def test01a_StringAtom(self):
        """Checking vlarray with numarray string atoms (numarray flavor, strided)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01a_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, flavor="numarray"),
                                           "Ragged array of strings")
        vlarray.append(strings.array(["1", "12", "123", "1234", "12345"][::2]))
        vlarray.append(strings.array(["1", "12345","2", "321"])[::3])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], strings.array(["1", "123", "123"]))
        assert allequal(row[1], strings.array(["1", "321"]))
        assert len(row[0]) == 3
        assert len(row[1]) == 2

    def test01a_2_StringAtom(self):
        """Checking vlarray with numarray string atoms (numarray flavor, no conv)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01a_2_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, flavor="numarray"),
                                           "Ragged array of strings")
        vlarray.append(strings.array(["1", "12", "123", "123"]))
        vlarray.append(strings.array(["1", "2", "321"]))

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], strings.array(["1", "12", "123", "123"]))
        assert allequal(row[1], strings.array(["1", "2", "321"]))
        assert len(row[0]) == 4
        assert len(row[1]) == 3

    def test01b_StringAtom(self):
        """Checking vlarray with numarray string atoms (python flavor)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom2',
                                           StringAtom(length=3,
                                                      flavor="python"),
                                           "Ragged array of strings")
        vlarray.append(["1", "12", "123", "1234", "12345"])
        vlarray.append(["1", "12345"])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Testing String flavor"
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert row[0] == ["1", "12", "123", "123", "123"]
        assert row[1] == ["1", "123"]
        assert len(row[0]) == 5
        assert len(row[1]) == 2

    def test01c_StringAtom(self):
        """Checking updating vlarray with numarray string atoms (numarray flavor)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01c_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, flavor="numarray"),
                                           "Ragged array of strings")
        vlarray.append(strings.array(["1", "12", "123", "1234", "12345"]))
        vlarray.append(strings.array(["1", "12345"]))

        # Modify the rows
        vlarray[0] = strings.array(["1", "123", "12", "", "12345"])
        vlarray[1] = strings.array(["44", "4"])  # This should work as well

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], strings.array(["1", "123", "12", "", "123"]))
        assert allequal(row[1], strings.array(["44", "4"]))
        assert len(row[0]) == 5
        assert len(row[1]) == 2

    def test01d_StringAtom(self):
        """Checking updating vlarray with string atoms (String flavor)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01d_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom2',
                                           StringAtom(length=3,
                                                      flavor="python"),
                                           "Ragged array of strings")
        vlarray.append(["1", "12", "123", "1234", "12345"])
        vlarray.append(["1", "12345"])

        # Modify the rows
        vlarray[0] = ["1", "123", "12", "", "12345"]
        vlarray[1] = ["44", "4"]

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Testing String flavor"
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert row[0] == ["1", "123", "12", "", "123"]
        assert row[1] == ["44", "4"]
        assert len(row[0]) == 5
        assert len(row[1]) == 2

    # Strings Atoms with UString (unicode strings) flavor can't be safely
    # implemented because the strings can be cut in the middle of a utf-8
    # codification and that can lead to errors like:
    #     >>> print 'a\xc3'.decode('utf-8')
    # Traceback (most recent call last):
    #   File "<stdin>", line 1, in ?
    # UnicodeDecodeError: 'utf8' codec can't decode byte 0xc3 in position 1: unexpected end of data

#     def test01c_StringAtom(self):
#         """Checking vlarray with numarray string atoms (UString flavor)"""

#         root = self.rootgroup
#         if verbose:
#             print '\n', '-=' * 30
#             print "Running %s.test01c_StringAtom..." % self.__class__.__name__

#         # Create an string atom
#         vlarray = self.fileh.createVLArray(root, 'stringAtom2',
#                                            StringAtom(length=3,
#                                                       flavor="UString"),
#                                            "Ragged array of unicode strings")
#         vlarray.append(["���", "����", "�"])
#         vlarray.append(["�����", "asa����"])

#         # Read all the rows:
#         row = vlarray.read()
#         if verbose:
#             print "Testing String flavor"
#             print "Object read:", row
#             print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
#             print "First row in vlarray ==>", row[0]

#         assert vlarray.nrows == 2
#         assert row[0] == ("123", "456", "3")
#         assert row[1] == ("456", "3")
#         assert len(row[0]) == 3
#         assert len(row[1]) == 2

    def test02_BoolAtom(self):
        """Checking vlarray with boolean atoms"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_BoolAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'BoolAtom',
                                           BoolAtom(),
                                           "Ragged array of Booleans")
        vlarray.append([1,0,3])
        vlarray.append([-1,0])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], array([1,0,1], type=Bool))
        assert allequal(row[1], array([1,0], type=Bool))
        assert len(row[0]) == 3
        assert len(row[1]) == 2

    def test02b_BoolAtom(self):
        """Checking setting vlarray with boolean atoms"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02b_BoolAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'BoolAtom',
                                           BoolAtom(),
                                           "Ragged array of Booleans")
        vlarray.append([1,0,3])
        vlarray.append([-1,0])

        # Modify the rows
        vlarray[0] = (0,1,3)
        vlarray[1] = (0,-1)

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert allequal(row[0], array([0,1,1], type=Bool))
        assert allequal(row[1], array([0,1], type=Bool))
        assert len(row[0]) == 3
        assert len(row[1]) == 2

    def test03_IntAtom(self):
        """Checking vlarray with integer atoms"""

        ttypes = {"Int8": Int8,
                  "UInt8": UInt8,
                  "Int16": Int16,
                  "UInt16": UInt16,
                  "Int32": Int32,
                  "UInt32": UInt32,
                  "Int64": Int64,
                  #"UInt64": UInt64,  # Unavailable in some platforms
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_IntAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype]))
            vlarray.append([1,2,3])
            vlarray.append([-1,0])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([1,2,3], type=ttypes[atype]))
            assert allequal(row[1], array([-1,0], type=ttypes[atype]))
            assert len(row[0]) == 3
            assert len(row[1]) == 2

    def test03b_IntAtom(self):
        """Checking updating vlarray with integer atoms"""

        ttypes = {"Int8": Int8,
                  "UInt8": UInt8,
                  "Int16": Int16,
                  "UInt16": UInt16,
                  "Int32": Int32,
                  "UInt32": UInt32,
                  "Int64": Int64,
                  #"UInt64": UInt64,  # Unavailable in some platforms
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_IntAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype]))
            vlarray.append([1,2,3])
            vlarray.append([-1,0])

            # Modify rows
            vlarray[0] = (3,2,1)
            vlarray[1] = (0,-1)

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([3,2,1], type=ttypes[atype]))
            assert allequal(row[1], array([0,-1], type=ttypes[atype]))
            assert len(row[0]) == 3
            assert len(row[1]) == 2

    def test04_FloatAtom(self):
        """Checking vlarray with floating point atoms"""

        ttypes = {"Float32": Float32,
                  "Float64": Float64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_FloatAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype]))
            vlarray.append([1.3,2.2,3.3])
            vlarray.append([-1.3e34,1.e-32])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([1.3,2.2,3.3], ttypes[atype]))
            assert allequal(row[1], array([-1.3e34,1.e-32], ttypes[atype]))
            assert len(row[0]) == 3
            assert len(row[1]) == 2

    def test04a_FloatAtom(self):
        """Checking updating vlarray with floating point atoms"""

        ttypes = {"Float32": Float32,
                  "Float64": Float64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_FloatAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype]))
            vlarray.append([1.3,2.2,3.3])
            vlarray.append([-1.3e34,1.e-32])

            # Modifiy some rows
            vlarray[0] = (4.3,2.2,4.3)
            vlarray[1] = (-1.1e34,1.3e-32)

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([4.3,2.2,4.3], ttypes[atype]))
            assert allequal(row[1], array([-1.1e34,1.3e-32], ttypes[atype]))
            assert len(row[0]) == 3
            assert len(row[1]) == 2

    def test04b_ComplexAtom(self):
        """Checking vlarray with numerical complex atoms"""

        ttypes = {"Complex32": Complex32,
                  "Complex64": Complex64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04b_ComplexAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype]))
            vlarray.append([(1.3+0j),(0+2.2j),(3.3+3.3j)])
            vlarray.append([(0-1.3e34j),(1.e-32+0j)])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([(1.3+0j),(0+2.2j),(3.3+3.3j)],
                                          ttypes[atype]))
            assert allequal(row[1], array([(0-1.3e34j),(1.e-32+0j)],
                                          ttypes[atype]))
            assert len(row[0]) == 3
            assert len(row[1]) == 2

    def test04c_ComplexAtom(self):
        """Checking modifying vlarray with numerical complex atoms"""

        ttypes = {"Complex32": Complex32,
                  "Complex64": Complex64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04c_ComplexAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype]))
            vlarray.append([(1.3+0j),(0+2.2j),(3.3+3.3j)])
            vlarray.append([(0-1.3e34j),(1.e-32+0j)])

            # Modify the rows
            vlarray[0] = ((1.4+0j),(0+4.2j),(3.3+4.3j))
            vlarray[1] = ((4-1.3e34j),(1.e-32+4j))

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([(1.4+0j),(0+4.2j),(3.3+4.3j)],
                                          ttypes[atype]))
            assert allequal(row[1], array([(4-1.3e34j),(1.e-32+4j)],
                                          ttypes[atype]))
            assert len(row[0]) == 3
            assert len(row[1]) == 2

    def test05_VLStringAtom(self):
        """Checking vlarray with variable length strings"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_VLStringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "VLStringAtom", VLStringAtom())
        vlarray.append(u"asd")
        vlarray.append(u"aaa��")

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert row[0] == u"asd"
        assert row[1] == u"aaa��"
        assert len(row[0]) == 3
        assert len(row[1]) == 5

    def test05b_VLStringAtom(self):
        """Checking updating vlarray with variable length strings"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05b_VLStringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "VLStringAtom", VLStringAtom())
        vlarray.append(u"asd")
        vlarray.append(u"aaa��")

        # Modify values
        # We have the problem here that we can only update values with
        # *exactly* the same bytes than in the original row. With
        # UTF-8 encoding this is problematic because 'c' takes 1 byte,
        # but '�' takes at least two (!). Perhaps another codification
        # does not have this problem, I don't know.
        vlarray[0] = u"as4"
        vlarray[1] = u"aaa��"

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", `row[0]`
            print "Second row in vlarray ==>", `row[1]`

        assert vlarray.nrows == 2
        assert row[0] == u"as4"
        assert row[1] == u"aaa��"
        assert len(row[0]) == 3
        assert len(row[1]) == 5

    def test06_Object(self):
        """Checking vlarray with object atoms """

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06_Object..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "Object", ObjectAtom())
        vlarray.append([[1,2,3], "aaa", u"aaa���"])
        vlarray.append([3,4, C()])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert row[0] == [[1,2,3], "aaa", u"aaa���"]
        list1 = list(row[1])
        obj = list1.pop()
        assert list1 == [3,4]
        assert obj.c == C().c
        assert len(row[0]) == 3
        assert len(row[1]) == 3


    def test06b_Object(self):
        """Checking updating vlarray with object atoms """

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06_Object..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "Object", ObjectAtom())
        vlarray.append(([1,2,3], "aaa", u"aaa���"))
        # When updating an object, this seems to change the number
        # of bytes that cPickle.dumps generates
        #vlarray.append([3,4, C()])
        vlarray.append([3,4, [24]])

        # Modify the rows
        vlarray[0] = ([1,2,4], "aa4", u"aaa��4")
        #vlarray[1] = (3,4, C())
        vlarray[1] = [4,4, [24]]

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 2
        assert row[0] == ([1,2,4], "aa4", u"aaa��4")
        list1 = list(row[1])
        obj = list1.pop()
        assert list1 == [4,4]
        #assert obj.c == C().c
        assert obj == [24]
        assert len(row[0]) == 3
        assert len(row[1]) == 3


class TypesNumArrayTestCase(TypesTestCase):
    title = "Types"

class MDTypesTestCase(unittest.TestCase):
    mode  = "w"
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test01_StringAtom(self):
        """Checking vlarray with MD numarray string atoms"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, shape=(2,)),
                                           "Ragged array of strings")
        vlarray.append([["123", "45"],["45", "123"]])
        vlarray.append([["s", "abc"],["abc", "f"],
                        ["s", "ab"],["ab", "f"]])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert allequal(row[0], strings.array([["123", "45"],["45", "123"]]))
        assert allequal(row[1], strings.array([["s", "abc"],["abc", "f"],
                                              ["s", "ab"],["ab", "f"]]))
        assert len(row[0]) == 2
        assert len(row[1]) == 4

    def test01b_StringAtom(self):
        """Checking vlarray with MD numarray string atoms (String flavor)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, shape=(2,),
                                                      flavor="python"),
                                           "Ragged array of strings")
        vlarray.append([["123", "45"],["45", "123"]])
        vlarray.append([["s", "abc"],["abc", "f"],
                        ["s", "ab"],["ab", "f"]])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert row[0] == [["123", "45"],["45", "123"]]
        assert row[1] == [["s", "abc"],["abc", "f"],
                          ["s", "ab"],["ab", "f"]]
        assert len(row[0]) == 2
        assert len(row[1]) == 4


    def test01c_StringAtom(self):
        """Checking vlarray with MD numarray string atoms (with offset)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01c_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, shape=(2,),
                                                      flavor="python"),
                                           "Ragged array of strings")
        a=strings.array([["a","b"],["123", "45"],["45", "123"]], itemsize=3)
        vlarray.append(a[1:])
        a=strings.array([["s", "a"],["ab", "f"],
                         ["s", "abc"],["abc", "f"],
                         ["s", "ab"],["ab", "f"]])
        vlarray.append(a[2:])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert row[0] == [["123", "45"],["45", "123"]]
        assert row[1] == [["s", "abc"],["abc", "f"],
                          ["s", "ab"],["ab", "f"]]
        assert len(row[0]) == 2
        assert len(row[1]) == 4

    def test01d_StringAtom(self):
        """Checking vlarray with MD numarray string atoms (with stride)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01d_StringAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'stringAtom',
                                           StringAtom(length=3, shape=(2,),
                                                      flavor="python"),
                                           "Ragged array of strings")
        a=strings.array([["a","b"],["123", "45"],["45", "123"]], itemsize=3)
        vlarray.append(a[1::2])
        a=strings.array([["s", "a"],["ab", "f"],
                         ["s", "abc"],["abc", "f"],
                         ["s", "ab"],["ab", "f"]])
        vlarray.append(a[::3])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert row[0] == [["123", "45"]]
        assert row[1] == [["s", "a"],["abc", "f"]]
        assert len(row[0]) == 1
        assert len(row[1]) == 2

    def test02_BoolAtom(self):
        """Checking vlarray with MD boolean atoms"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_BoolAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'BoolAtom',
                                           BoolAtom(shape = (3,)),
                                           "Ragged array of Booleans")
        vlarray.append([(1,0,3), (1,1,1), (0,0,0)])
        vlarray.append([(-1,0,0)])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert allequal(row[0], array([[1,0,1],[1,1,1],[0,0,0]], type=Bool))
        assert allequal(row[1], array([[1,0,0]], type=Bool))
        assert len(row[0]) == 3
        assert len(row[1]) == 1

    def test02b_BoolAtom(self):
        """Checking vlarray with MD boolean atoms (with offset)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02b_BoolAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'BoolAtom',
                                           BoolAtom(shape = (3,)),
                                           "Ragged array of Booleans")
        a=array([(0,0,0), (1,0,3), (1,1,1), (0,0,0)], type=Bool)
        vlarray.append(a[1:])  # Create an offset
        a=array([(1,1,1), (-1,0,0)], type=Bool)
        vlarray.append(a[1:])  # Create an offset

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert allequal(row[0], array([[1,0,1],[1,1,1],[0,0,0]], type=Bool))
        assert allequal(row[1], array([[1,0,0]], type=Bool))
        assert len(row[0]) == 3
        assert len(row[1]) == 1

    def test02c_BoolAtom(self):
        """Checking vlarray with MD boolean atoms (with strides)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02c_BoolAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'BoolAtom',
                                           BoolAtom(shape = (3,)),
                                           "Ragged array of Booleans")
        a=array([(0,0,0), (1,0,3), (1,1,1), (0,0,0)], type=Bool)
        vlarray.append(a[1::2])  # Create an strided array
        a=array([(1,1,1), (-1,0,0), (0,0,0)], type=Bool)
        vlarray.append(a[::2])  # Create an strided array

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == 2
        assert allequal(row[0], array([[1,0,1],[0,0,0]], type=Bool))
        assert allequal(row[1], array([[1,1,1],[0,0,0]], type=Bool))
        assert len(row[0]) == 2
        assert len(row[1]) == 2

    def test03_IntAtom(self):
        """Checking vlarray with MD integer atoms"""

        ttypes = {"Int8": Int8,
                  "UInt8": UInt8,
                  "Int16": Int16,
                  "UInt16": UInt16,
                  "Int32": Int32,
                  "UInt32": UInt32,
                  "Int64": Int64,
                  #"UInt64": UInt64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_IntAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype],
                                                    shape = (2,3)))
            vlarray.append([ones((2,3), ttypes[atype]),
                            zeros((2,3), ttypes[atype])])
            vlarray.append([ones((2,3), ttypes[atype])*100])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "Second row in vlarray ==>", repr(row[1])

            assert vlarray.nrows == 2
            assert allequal(row[0], array([ones((2,3)),
                                          zeros((2,3))], ttypes[atype]))
            assert allequal(row[1], array([ones((2,3))*100], ttypes[atype]))
            assert len(row[0]) == 2
            assert len(row[1]) == 1

    def test04_FloatAtom(self):
        """Checking vlarray with MD floating point atoms"""

        ttypes = {"Float32": Float32,
                  "Float64": Float64,
                  "Complex32": Complex32,
                  "Complex64": Complex64
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_FloatAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype],
                                                    shape=(5,2,6)))
            vlarray.append([ones((5,2,6), ttypes[atype])*1.3,
                            zeros((5,2,6), ttypes[atype])])
            vlarray.append([ones((5,2,6), ttypes[atype])*2.e4])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing type:", atype
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "Second row in vlarray ==>", row[1]

            assert vlarray.nrows == 2
            assert allequal(row[0], array([ones((5,2,6))*1.3,
                                          zeros((5,2,6))], ttypes[atype]))
            assert allequal(row[1], array([ones((5,2,6))*2.e4], ttypes[atype]))
            assert len(row[0]) == 2
            assert len(row[1]) == 1


class MDTypesNumArrayTestCase(MDTypesTestCase):
    title = "MDTypes"

class AppendShapeTestCase(unittest.TestCase):
    mode  = "w"

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test00_difinputs(self):
        """Checking vlarray.append() with different inputs"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test00_difinputs..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'vlarray',
                                           Int32Atom(flavor="python"),
                                           "Ragged array of ints")

        # Check different ways to input
        ## Strange filtering behaviour... (Python #1191104).
        ## warnings.filterwarnings("error", category=DeprecationWarning)
        ## self.assertRaises(DeprecationWarning, vlarray.append, 1, 2, 3)
        ## warnings.filterwarnings("default", category=DeprecationWarning)

        # All of the next should lead to the same rows
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        vlarray.append(1,2,3) # a list of parameters
        warnings.filterwarnings("default", category=DeprecationWarning)
        vlarray.append((1,2,3)) # a tuple
        vlarray.append([1,2,3]) # a unique list
        vlarray.append(array([1,2,3], type=Int32)) # and array

        if self.close:
            if verbose:
                print "(closing file version)"
            self.fileh.close()
            self.fileh = openFile(self.file, mode = "r")
            vlarray = self.fileh.root.vlarray

        # Read all the vlarray
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 4
        assert row[0] == [1,2,3]
        assert row[1] == [1,2,3]
        assert row[2] == [1,2,3]
        assert row[3] == [1,2,3]

    def test01_toomanydims(self):
        """Checking vlarray.append() with too many dimensions"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_toomanydims..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'vlarray',
                                           StringAtom(length=3),
                                           "Ragged array of strings")
        # Adding an array with one dimensionality more than allowed
        try:
            vlarray.append([["123", "456", "3"]])
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next RuntimeError was catched!"
                print value
        else:
            self.fail("expected a ValueError")

        if self.close:
            if verbose:
                print "(closing file version)"
            self.fileh.close()
            self.fileh = openFile(self.file, mode = "r")
            vlarray = self.fileh.root.vlarray

        # Read all the rows (there should be none)
        row = vlarray.read()
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows

        assert vlarray.nrows == 0

    def test02_zerodims(self):
        """Checking vlarray.append() with a zero-dimensional array"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_zerodims..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'vlarray',
                                           Int32Atom(),
                                           "Ragged array of ints")
        vlarray.append(zeros(type=Int32, shape=(6,0)))

        if self.close:
            if verbose:
                print "(closing file version)"
            self.fileh.close()
            self.fileh = openFile(self.file, mode = "r")
            vlarray = self.fileh.root.vlarray

        # Read the only row in vlarray
        row = vlarray.read(0)[0]
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row.info()

        assert vlarray.nrows == 1
        assert allequal(row, zeros(type=Int32, shape=(0,)))
        assert len(row) == 0

    def test03a_cast(self):
        """Checking vlarray.append() with a casted array (upgrading case)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03a_cast..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'vlarray',
                                           Int32Atom(),
                                           "Ragged array of ints")
        # This type has to be upgraded
        vlarray.append(array([1,2], type=Int16))

        if self.close:
            if verbose:
                print "(closing file version)"
            self.fileh.close()
            self.fileh = openFile(self.file, mode = "r")
            vlarray = self.fileh.root.vlarray

        # Read the only row in vlarray
        row = vlarray.read(0)[0]
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row.info()

        assert vlarray.nrows == 1
        assert allequal(row, array([1,2], type=Int32))
        assert len(row) == 2

    def test03b_cast(self):
        """Checking vlarray.append() with a casted array (downgrading case)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03b_cast..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, 'vlarray',
                                           Int32Atom(),
                                           "Ragged array of ints")
        # This type has to be dowgraded
        vlarray.append(array([1,2], type=Float64))

        if self.close:
            if verbose:
                print "(closing file version)"
            self.fileh.close()
            self.fileh = openFile(self.file, mode = "r")
            vlarray = self.fileh.root.vlarray

        # Read the only row in vlarray
        row = vlarray.read(0)[0]
        if verbose:
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row.info()

        assert vlarray.nrows == 1
        assert allequal(row, array([1,2], type=Int32))
        assert len(row) == 2

class OpenAppendShapeTestCase(AppendShapeTestCase):
    close = 0

class CloseAppendShapeTestCase(AppendShapeTestCase):
    close = 1

class FlavorTestCase(unittest.TestCase):
    mode  = "w"
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):

        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #----------------------------------------

    def test01a_EmptyVLArray(self):
        """Checking empty vlarrays with different flavors (closing the file)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_EmptyVLArray..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "vlarray",
                                           IntAtom(itemsize=4,
                                                   flavor=self.flavor))
        self.fileh.close()
        self.fileh = openFile(self.file, "r")
        # Read all the rows (it should be empty):
        vlarray = self.fileh.root.vlarray
        row = vlarray.read()
        if verbose:
            print "Testing flavor:", self.flavor
            print "Object read:", row, repr(row)
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
        # Check that the object read is effectively empty
        assert vlarray.nrows == 0
        assert row == []

    def test01b_EmptyVLArray(self):
        """Checking empty vlarrays with different flavors (no closing file)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_EmptyVLArray..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "vlarray",
                                           IntAtom(itemsize=4,
                                                   flavor=self.flavor))
        # Read all the rows (it should be empty):
        row = vlarray.read()
        if verbose:
            print "Testing flavor:", self.flavor
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
        # Check that the object read is effectively empty
        assert vlarray.nrows == 0
        assert row == []

    def test02_BooleanAtom(self):
        """Checking vlarray with different flavors (boolean versions)"""

        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_BoolAtom..." % self.__class__.__name__

        # Create an string atom
        vlarray = self.fileh.createVLArray(root, "Bool",
                                           BoolAtom(flavor=self.flavor))
        vlarray.append([1,2,3])
        vlarray.append(())   # Empty row
        vlarray.append([100,0])

        # Read all the rows:
        row = vlarray.read()
        if verbose:
            print "Testing flavor:", self.flavor
            print "Object read:", row
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]

        assert vlarray.nrows == 3
        assert len(row[0]) == 3
        assert len(row[1]) == 0
        assert len(row[2]) == 2
        if self.flavor == "python":
            arr1 = [1,1,1]
            arr2 = []
            arr3 = [1,0]
        elif self.flavor == "numpy":
            arr1 = numpy.array([1,1,1], dtype="bool8")
            arr2 = numpy.array([], dtype="bool8")
            arr3 = numpy.array([1,0], dtype="bool8")
        elif self.flavor == "numeric":
            arr1 = Numeric.array([1,1,1], typecode="1")
            arr2 = Numeric.array([], typecode="1")
            arr3 = Numeric.array([1,0], typecode="1")
        else:  # Default (NumArray)
            arr1 = array([1,1,1], type=Bool)
            arr2 = array([], type=Bool)
            arr3 = array([1,0], type=Bool)

        if self.flavor == "numeric":
            allequal(row[0], arr1, "numeric")
            allequal(row[1], arr2, "numeric")
            allequal(row[2], arr3, "numeric")
        elif self.flavor == "numpy":
            allequal(row[0], arr1, "numpy")
            allequal(row[1], arr2, "numpy")
            allequal(row[2], arr3, "numpy")
        elif self.flavor == "numarray":
            allequal(row[0], arr1)
            allequal(row[1], arr2)
            allequal(row[1], arr2)
        else:
            # Tuple or List flavors
            assert row[0] == arr1
            assert row[1] == arr2
            assert row[2] == arr3

    def test03_IntAtom(self):
        """Checking vlarray with different flavors (integer versions)"""

        ttypes = {"Int8": Int8,
                  "UInt8": UInt8,
                  "Int16": Int16,
                  "UInt16": UInt16,
                  "Int32": Int32,
                  # Not checked because of Numeric <-> numarray
                  # conversion problems
                  #"UInt32": UInt32,
                  #"Int64": Int64,
                  # Not checked because some platforms does not support it
                  #"UInt64": UInt64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_IntAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype],
                                                    flavor=self.flavor))
            vlarray.append([1,2,3])
            vlarray.append(())
            vlarray.append([100,0])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing flavor:", self.flavor
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 3
            assert len(row[0]) == 3
            assert len(row[1]) == 0
            assert len(row[2]) == 2
            if self.flavor == "python":
                arr1 = [1,2,3]
                arr2 = []
                arr3 = [100,0]
            elif self.flavor == "numpy":
                arr1 = numpy.array([1,2,3], dtype=numpy.typeNA[ttypes[atype]])
                arr2 = numpy.array([], dtype=numpy.typeNA[ttypes[atype]])
                arr3 = numpy.array([100,0], dtype=numpy.typeNA[ttypes[atype]])
            elif self.flavor == "numeric":
                arr1 = Numeric.array([1,2,3], typecode=typecode[ttypes[atype]])
                arr2 = Numeric.array([], typecode=typecode[ttypes[atype]])
                arr3 = Numeric.array([100,0], typecode=typecode[ttypes[atype]])
            else:  # Default (NumArray)
                arr1 = array([1,2,3], type=ttypes[atype])
                arr2 = array([], type=ttypes[atype])
                arr3 = array([100, 0], type=ttypes[atype])

            if self.flavor == "numeric":
                allequal(row[0], arr1, "numeric")
                allequal(row[1], arr2, "numeric")
                allequal(row[2], arr3, "numeric")
            elif self.flavor == "numpy":
                allequal(row[0], arr1, "numpy")
                allequal(row[1], arr2, "numpy")
                allequal(row[2], arr3, "numpy")
            elif self.flavor == "numarray":
                allequal(row[0], arr1)
                allequal(row[1], arr2)
                allequal(row[2], arr3)
            else:
                # Tuple or List flavors
                assert row[0] == arr1
                assert row[1] == arr2
                assert row[2] == arr3

    def test03b_IntAtom(self):
        """Checking vlarray flavors (integer versions and closed file)"""

        ttypes = {"Int8": Int8,
                  "UInt8": UInt8,
                  "Int16": Int16,
                  "UInt16": UInt16,
                  "Int32": Int32,
                  # Not checked because of Numeric <-> numarray
                  # conversion problems
                  #"UInt32": UInt32,
                  #"Int64": Int64,
                  # Not checked because some platforms does not support it
                  #"UInt64": UInt64,
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_IntAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype],
                                                    flavor=self.flavor))
            vlarray.append([1,2,3])
            vlarray.append(())
            vlarray.append([100,0])
            self.fileh.close()
            self.fileh = openFile(self.file, "a")  # open in "a"ppend mode
            root = self.fileh.root  # Very important!
            vlarray = self.fileh.getNode(root, str(atype))
            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing flavor:", self.flavor
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 3
            assert len(row[0]) == 3
            assert len(row[1]) == 0
            assert len(row[2]) == 2
            if self.flavor == "python":
                arr1 = [1,2,3]
                arr2 = []
                arr3 = [100,0]
            elif self.flavor == "numpy":
                arr1 = numpy.array([1,2,3], dtype=numpy.typeNA[ttypes[atype]])
                arr2 = numpy.array([], dtype=numpy.typeNA[ttypes[atype]])
                arr3 = numpy.array([100,0], dtype=numpy.typeNA[ttypes[atype]])
            elif self.flavor == "numeric":
                arr1 = Numeric.array([1,2,3], typecode=typecode[ttypes[atype]])
                arr2 = Numeric.array([], typecode=typecode[ttypes[atype]])
                arr3 = Numeric.array([100,0], typecode=typecode[ttypes[atype]])
            else:  # Default (NumArray)
                arr1 = array([1,2,3], type=ttypes[atype])
                arr2 = array([], type=ttypes[atype])
                arr3 = array([100, 0], type=ttypes[atype])

            if self.flavor == "numeric":
                allequal(row[0], arr1, "numeric")
                allequal(row[1], arr2, "numeric")
                allequal(row[2], arr3, "numeric")
            elif self.flavor == "numpy":
                allequal(row[0], arr1, "numpy")
                allequal(row[1], arr2, "numpy")
                allequal(row[2], arr3, "numpy")
            elif self.flavor == "numarray":
                allequal(row[0], arr1)
                allequal(row[1], arr2)
                allequal(row[2], arr3)
            else:
                # Tuple or List flavors
                assert row[0] == arr1
                assert row[1] == arr2
                assert row[2] == arr3

    def test04_FloatAtom(self):
        """Checking vlarray with different flavors (floating point versions)"""


        ttypes = {"Float32": Float32,
                  "Float64": Float64,
                  "Complex32": Complex32,
                  "Complex64": Complex64
                  }
        root = self.rootgroup
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_FloatAtom..." % self.__class__.__name__

        # Create an string atom
        for atype in ttypes.iterkeys():
            vlarray = self.fileh.createVLArray(root, atype,
                                               Atom(ttypes[atype],
                                                    flavor=self.flavor))
            vlarray.append([1.3,2.2,3.3])
            vlarray.append(())
            vlarray.append([-1.3e34,1.e-32])

            # Read all the rows:
            row = vlarray.read()
            if verbose:
                print "Testing flavor:", self.flavor
                print "Object read:", row
                print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
                print "First row in vlarray ==>", row[0]

            assert vlarray.nrows == 3
            assert len(row[0]) == 3
            assert len(row[1]) == 0
            assert len(row[2]) == 2
            if self.flavor == "python":
                arr1 = list(array([1.3,2.2,3.3], typecode[ttypes[atype]]))
                arr2 = list(array([], typecode[ttypes[atype]]))
                arr3 = list(array([-1.3e34,1.e-32], typecode[ttypes[atype]]))
            elif self.flavor == "numpy":
                arr1 = numpy.array([1.3,2.2,3.3], dtype=numpy.typeNA[ttypes[atype]])
                arr2 = numpy.array([], dtype=numpy.typeNA[ttypes[atype]])
                arr3 = numpy.array([-1.3e34,1.e-32], dtype=numpy.typeNA[ttypes[atype]])
            elif self.flavor == "numeric":
                arr1 = Numeric.array([1.3,2.2,3.3], typecode[ttypes[atype]])
                arr2 = Numeric.array([], typecode[ttypes[atype]])
                arr3 = Numeric.array([-1.3e34,1.e-32], typecode[ttypes[atype]])
            else:   # Default (NumArray)
                arr1 = array([1.3,2.2,3.3], type=ttypes[atype])
                arr2 = array([], type=ttypes[atype])
                arr3 = array([-1.3e34,1.e-32], type=ttypes[atype])

            if self.flavor == "numeric":
                allequal(row[0], arr1, "numeric")
                allequal(row[1], arr2, "numeric")
                allequal(row[2], arr3, "numeric")
            elif self.flavor == "numpy":
                allequal(row[0], arr1, "numpy")
                allequal(row[1], arr2, "numpy")
                allequal(row[2], arr3, "numpy")
            elif self.flavor == "numarray":
                allequal(row[0], arr1)
                allequal(row[1], arr2)
                allequal(row[2], arr3)
            else:
                # Tuple or List flavors
                assert row[0] == arr1
                assert row[1] == arr2
                assert row[2] == arr3

class NumArrayFlavorTestCase(FlavorTestCase):
    flavor = "numarray"

class NumpyFlavorTestCase(FlavorTestCase):
    flavor = "numpy"

class NumericFlavorTestCase(FlavorTestCase):
    flavor = "numeric"

class PythonFlavorTestCase(FlavorTestCase):
    flavor = "python"

class ReadRangeTestCase(unittest.TestCase):
    nrows = 100
    mode  = "w"
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):
        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def populateFile(self):
        group = self.rootgroup
        filters = Filters(complevel = self.compress,
                          complib = self.complib)
        vlarray = self.fileh.createVLArray(group, 'vlarray', Int32Atom(),
                                           "ragged array if ints",
                                           filters = filters,
                                           expectedsizeinMB = 1)

        # Fill it with 100 rows with variable length
        for i in range(self.nrows):
            vlarray.append(range(i))

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #------------------------------------------------------------------

    def test01_start(self):
        "Checking reads with only a start value"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_start..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32))
        assert allequal(row[1], arange(10, type=Int32))
        assert allequal(row[2], arange(99, type=Int32))

    def test01b_start(self):
        "Checking reads with only a start value in a slice"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_start..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        # Read some rows:
        row = []
        row.append(vlarray[0])
        row.append(vlarray[10])
        row.append(vlarray[99])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32))
        assert allequal(row[1], arange(10, type=Int32))
        assert allequal(row[2], arange(99, type=Int32))

    def test01np_start(self):
        "Checking reads with only a start value in a slice (numpy indexes)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01np_start..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        # Read some rows:
        row = []
        row.append(vlarray[numpy.int8(0)])
        row.append(vlarray[numpy.int32(10)])
        row.append(vlarray[numpy.int64(99)])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32))
        assert allequal(row[1], arange(10, type=Int32))
        assert allequal(row[2], arange(99, type=Int32))

    def test02_stop(self):
        "Checking reads with only a stop value"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_stop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray.read(stop=1))
        row.append(vlarray.read(stop=10))
        row.append(vlarray.read(stop=99))
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 1
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0][0], arange(0, type=Int32))
        for x in range(10):
            assert allequal(row[1][x], arange(x, type=Int32))
        for x in range(99):
            assert allequal(row[2][x], arange(x, type=Int32))

    def test02b_stop(self):
        "Checking reads with only a stop value in a slice"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02b_stop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[:1])
        row.append(vlarray[:10])
        row.append(vlarray[:99])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 1
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        for x in range(1):
            assert allequal(row[0][x], arange(0, type=Int32))
        for x in range(10):
            assert allequal(row[1][x], arange(x, type=Int32))
        for x in range(99):
            assert allequal(row[2][x], arange(x, type=Int32))


    def test03_startstop(self):
        "Checking reads with a start and stop values"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_startstop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray.read(0,10))
        row.append(vlarray.read(5,15))
        row.append(vlarray.read(0,100))  # read all the array
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 10
        assert len(row[1]) == 10
        assert len(row[2]) == 100
        for x in range(0,10):
            assert allequal(row[0][x], arange(x, type=Int32))
        for x in range(5,15):
            assert allequal(row[1][x-5], arange(x, type=Int32))
        for x in range(0,100):
            assert allequal(row[2][x], arange(x, type=Int32))

    def test03b_startstop(self):
        "Checking reads with a start and stop values in slices"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03b_startstop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[0:10])
        row.append(vlarray[5:15])
        row.append(vlarray[:])  # read all the array
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 10
        assert len(row[1]) == 10
        assert len(row[2]) == 100
        for x in range(0,10):
            assert allequal(row[0][x], arange(x, type=Int32))
        for x in range(5,15):
            assert allequal(row[1][x-5], arange(x, type=Int32))
        for x in range(0,100):
            assert allequal(row[2][x], arange(x, type=Int32))

    def test04_startstopstep(self):
        "Checking reads with a start, stop & step values"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_startstopstep..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray.read(0,10,2))
        row.append(vlarray.read(5,15,3))
        row.append(vlarray.read(0,100,20))
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 5
        assert len(row[1]) == 4
        assert len(row[2]) == 5
        for x in range(0,10,2):
            assert allequal(row[0][x/2], arange(x, type=Int32))
        for x in range(5,15,3):
            assert allequal(row[1][(x-5)/3], arange(x, type=Int32))
        for x in range(0,100,20):
            assert allequal(row[2][x/20], arange(x, type=Int32))

    def test04np_startstopstep(self):
        "Checking reads with a start, stop & step values (numpy indices)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04np_startstopstep..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray.read(numpy.int8(0),numpy.int8(10),numpy.int8(2)))
        row.append(vlarray.read(numpy.int8(5),numpy.int8(15),numpy.int8(3)))
        row.append(vlarray.read(numpy.int8(0),numpy.int8(100),numpy.int8(20)))
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 5
        assert len(row[1]) == 4
        assert len(row[2]) == 5
        for x in range(0,10,2):
            assert allequal(row[0][x/2], arange(x, type=Int32))
        for x in range(5,15,3):
            assert allequal(row[1][(x-5)/3], arange(x, type=Int32))
        for x in range(0,100,20):
            assert allequal(row[2][x/20], arange(x, type=Int32))

    def test04b_slices(self):
        "Checking reads with start, stop & step values in slices"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04b_slices..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[0:10:2])
        row.append(vlarray[5:15:3])
        row.append(vlarray[0:100:20])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 5
        assert len(row[1]) == 4
        assert len(row[2]) == 5
        for x in range(0,10,2):
            assert allequal(row[0][x/2], arange(x, type=Int32))
        for x in range(5,15,3):
            assert allequal(row[1][(x-5)/3], arange(x, type=Int32))
        for x in range(0,100,20):
            assert allequal(row[2][x/20], arange(x, type=Int32))

    def test04bnp_slices(self):
        "Checking reads with start, stop & step values in slices (numpy indices)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04bnp_slices..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[numpy.int16(0):numpy.int16(10):numpy.int32(2)])
        row.append(vlarray[numpy.int16(5):numpy.int16(15):numpy.int64(3)])
        row.append(vlarray[numpy.uint16(0):numpy.int32(100):numpy.int8(20)])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 5
        assert len(row[1]) == 4
        assert len(row[2]) == 5
        for x in range(0,10,2):
            assert allequal(row[0][x/2], arange(x, type=Int32))
        for x in range(5,15,3):
            assert allequal(row[1][(x-5)/3], arange(x, type=Int32))
        for x in range(0,100,20):
            assert allequal(row[2][x/20], arange(x, type=Int32))

    def test05_out_of_range(self):
        "Checking out of range reads"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_out_of_range..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows

        try:
            row = vlarray.read(1000)[0]
            print "row-->", row
        except IndexError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next IndexError was catched!"
                print value
            self.fileh.close()
        else:
            (type, value, traceback) = sys.exc_info()
            self.fail("expected a IndexError and got:\n%s" % value)

class GetItemRangeTestCase(unittest.TestCase):
    nrows = 100
    mode  = "w"
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):
        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def populateFile(self):
        group = self.rootgroup
        filters = Filters(complevel = self.compress,
                          complib = self.complib)
        vlarray = self.fileh.createVLArray(group, 'vlarray', Int32Atom(),
                                           "ragged array if ints",
                                           filters = filters,
                                           expectedsizeinMB = 1)

        # Fill it with 100 rows with variable length
        for i in range(self.nrows):
            vlarray.append(range(i))

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #------------------------------------------------------------------

    def test01_start(self):
        "Checking reads with only a start value"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_start..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        # Read some rows:
        row = []
        row.append(vlarray[0])
        row.append(vlarray[10])
        row.append(vlarray[99])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32))
        assert allequal(row[1], arange(10, type=Int32))
        assert allequal(row[2], arange(99, type=Int32))

    def test01b_start(self):
        "Checking reads with only a start value in a slice"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01b_start..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        # Read some rows:
        row = []
        row.append(vlarray[0])
        row.append(vlarray[10])
        row.append(vlarray[99])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32))
        assert allequal(row[1], arange(10, type=Int32))
        assert allequal(row[2], arange(99, type=Int32))

    def test02_stop(self):
        "Checking reads with only a stop value"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_stop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[:1])
        row.append(vlarray[:10])
        row.append(vlarray[:99])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "First row in vlarray ==>", row[0]
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 1
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0][0], arange(0, type=Int32))
        for x in range(10):
            assert allequal(row[1][x], arange(x, type=Int32))
        for x in range(99):
            assert allequal(row[2][x], arange(x, type=Int32))

    def test02b_stop(self):
        "Checking reads with only a stop value in a slice"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02b_stop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[:1])
        row.append(vlarray[:10])
        row.append(vlarray[:99])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 1
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        for x in range(1):
            assert allequal(row[0][x], arange(0, type=Int32))
        for x in range(10):
            assert allequal(row[1][x], arange(x, type=Int32))
        for x in range(99):
            assert allequal(row[2][x], arange(x, type=Int32))


    def test03_startstop(self):
        "Checking reads with a start and stop values"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_startstop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[0:10])
        row.append(vlarray[5:15])
        row.append(vlarray[0:100])  # read all the array
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 10
        assert len(row[1]) == 10
        assert len(row[2]) == 100
        for x in range(0,10):
            assert allequal(row[0][x], arange(x, type=Int32))
        for x in range(5,15):
            assert allequal(row[1][x-5], arange(x, type=Int32))
        for x in range(0,100):
            assert allequal(row[2][x], arange(x, type=Int32))

    def test03b_startstop(self):
        "Checking reads with a start and stop values in slices"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03b_startstop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[0:10])
        row.append(vlarray[5:15])
        row.append(vlarray[:])  # read all the array
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 10
        assert len(row[1]) == 10
        assert len(row[2]) == 100
        for x in range(0,10):
            assert allequal(row[0][x], arange(x, type=Int32))
        for x in range(5,15):
            assert allequal(row[1][x-5], arange(x, type=Int32))
        for x in range(0,100):
            assert allequal(row[2][x], arange(x, type=Int32))

    def test04_slices(self):
        "Checking reads with a start, stop & step values"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_slices..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[0:10:2])
        row.append(vlarray[5:15:3])
        row.append(vlarray[0:100:20])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 5
        assert len(row[1]) == 4
        assert len(row[2]) == 5
        for x in range(0,10,2):
            assert allequal(row[0][x/2], arange(x, type=Int32))
        for x in range(5,15,3):
            assert allequal(row[1][(x-5)/3], arange(x, type=Int32))
        for x in range(0,100,20):
            assert allequal(row[2][x/20], arange(x, type=Int32))

    def test04bnp_slices(self):
        "Checking reads with start, stop & step values (numpy indices)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04np_slices..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray
        # Choose a small value for buffer size
        vlarray._nrowsinbuf = 3

        # Read some rows:
        row = []
        row.append(vlarray[numpy.int8(0):numpy.int8(10):numpy.int8(2)])
        row.append(vlarray[numpy.int8(5):numpy.int8(15):numpy.int8(3)])
        row.append(vlarray[numpy.int8(0):numpy.int8(100):numpy.int8(20)])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 5
        assert len(row[1]) == 4
        assert len(row[2]) == 5
        for x in range(0,10,2):
            assert allequal(row[0][x/2], arange(x, type=Int32))
        for x in range(5,15,3):
            assert allequal(row[1][(x-5)/3], arange(x, type=Int32))
        for x in range(0,100,20):
            assert allequal(row[2][x/20], arange(x, type=Int32))

    def test05_out_of_range(self):
        "Checking out of range reads"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_out_of_range..." % self.__class__.__name__

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows

        try:
            row = vlarray[1000]
            print "row-->", row
        except IndexError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next IndexError was catched!"
                print value
            self.fileh.close()
        else:
            (type, value, traceback) = sys.exc_info()
            self.fail("expected a IndexError and got:\n%s" % value)

    def test05np_out_of_range(self):
        "Checking out of range reads (numpy indexes)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05np_out_of_range..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "r")
        vlarray = self.fileh.root.vlarray

        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows

        try:
            row = vlarray[numpy.int32(1000)]
            print "row-->", row
        except IndexError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next IndexError was catched!"
                print value
            self.fileh.close()
        else:
            (type, value, traceback) = sys.exc_info()
            self.fail("expected a IndexError and got:\n%s" % value)

class SetRangeTestCase(unittest.TestCase):
    nrows = 100
    mode  = "w"
    compress = 0
    complib = "zlib"  # Default compression library

    def setUp(self):
        # Create an instance of an HDF5 Table
        self.file = tempfile.mktemp(".h5")
        self.fileh = openFile(self.file, self.mode)
        self.rootgroup = self.fileh.root
        self.populateFile()
        self.fileh.close()

    def populateFile(self):
        group = self.rootgroup
        filters = Filters(complevel = self.compress,
                          complib = self.complib)
        vlarray = self.fileh.createVLArray(group, 'vlarray', Int32Atom(),
                                           "ragged array if ints",
                                           filters = filters,
                                           expectedsizeinMB = 1)

        # Fill it with 100 rows with variable length
        for i in range(self.nrows):
            vlarray.append(range(i))

    def tearDown(self):
        self.fileh.close()
        os.remove(self.file)
        cleanup(self)

    #------------------------------------------------------------------

    def test01_start(self):
        "Checking updates that modifies a complete row"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_start..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[0] = vlarray[0]*2+3
        vlarray[10] = vlarray[10]*2+3
        vlarray[99] = vlarray[99]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], arange(10, type=Int32)*2+3)
        assert allequal(row[2], arange(99, type=Int32)*2+3)

    def test01np_start(self):
        "Checking updates that modifies a complete row"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01np_start..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[numpy.int8(0)] = vlarray[numpy.int16(0)]*2+3
        vlarray[numpy.int8(10)] = vlarray[numpy.int8(10)]*2+3
        vlarray[numpy.int32(99)] = vlarray[numpy.int64(99)]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(numpy.int8(0))[0])
        row.append(vlarray.read(numpy.int8(10))[0])
        row.append(vlarray.read(numpy.int8(99))[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], arange(10, type=Int32)*2+3)
        assert allequal(row[2], arange(99, type=Int32)*2+3)

    def test02_start(self):
        "Checking updates with only a part of a row (start, None)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_start..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[0] = vlarray[0]*2+3
        vlarray[10,0:] = vlarray[10]*2+3
        #print "shape1, shape2-->", vlarray[99].shape, vlarray[96].shape
        vlarray[99,3:] = vlarray[96]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], arange(10, type=Int32)*2+3)
        a = arange(99, type=Int32); a[3:] = a[:96]*2+3
        assert allequal(row[2], a)

    def test03_stop(self):
        "Checking updates with only a part of a row (None, stop)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_stop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[0] = vlarray[0]*2+3
        vlarray[10,:10] = vlarray[10]*2+3
        #print "shape1, shape2-->", vlarray[99].shape, vlarray[96].shape
        vlarray[99,:3] = vlarray[3]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], arange(10, type=Int32)*2+3)
        a = arange(99, type=Int32); a[:3] = a[:3]*2+3
        assert allequal(row[2], a)

    def test04_start_stop(self):
        "Checking updates with only a part of a row (start, stop)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_start_stop..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[0] = vlarray[0]*2+3
        vlarray[10,0:9] = vlarray[9]*2+3
        #print "vlarray[10]-->", `vlarray[10]`
        vlarray[99,3:5] = vlarray[2]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], concatenate([arange(9, type=Int32)*2+3,
                                             array(9,type=Int32)]))
        a = arange(99, type=Int32); a[3:5] = a[:2]*2+3
        assert allequal(row[2], a)

    def test05_start_stop(self):
        "Checking updates with only a part of a row (-start, -stop)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_start_stop_step..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[0] = vlarray[0]*2+3
        vlarray[10,-10:-1] = vlarray[9]*2+3
        #print "shape1, shape2-->", vlarray[99].shape, vlarray[96].shape
        vlarray[99,-99:-89:2] = vlarray[5]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], concatenate([arange(9, type=Int32)*2+3,
                                             array(9,type=Int32)]))
        a = arange(99, type=Int32); a[-99:-89:2] = a[:5]*2+3
        assert allequal(row[2], a)

    def test06_start_stop_step(self):
        "Checking updates with only a part of a row (start, stop, step)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06_start_stop_step..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[0] = vlarray[0]*2+3
        vlarray[10,0:10:1] = vlarray[10]*2+3
        #print "shape1, shape2-->", vlarray[99].shape, vlarray[96].shape
        vlarray[99,1:11:2] = vlarray[5]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], arange(10, type=Int32)*2+3)
        a = arange(99, type=Int32); a[1:11:2] = a[:5]*2+3
        assert allequal(row[2], a)

    def test06np_start_stop_step(self):
        "Checking updates with only a part of a row (start, stop, step). numpy idx"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test06np_start_stop_step..." % self.__class__.__name__

        if not numpy_imported:
            return

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        # Modify some rows:
        vlarray[numpy.int8(0)] = vlarray[numpy.int8(0)]*2+3
        vlarray[10,numpy.int8(0):numpy.int8(10):numpy.int8(1)] = vlarray[10]*2+3
        #print "shape1, shape2-->", vlarray[99].shape, vlarray[96].shape
        vlarray[numpy.int8(99),numpy.int8(1):numpy.int8(11):2] = vlarray[5]*2+3

        # Read some rows:
        row = []
        row.append(vlarray.read(0)[0])
        row.append(vlarray.read(10)[0])
        row.append(vlarray.read(99)[0])
        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows
            print "Second row in vlarray ==>", row[1]

        assert vlarray.nrows == self.nrows
        assert len(row[0]) == 0
        assert len(row[1]) == 10
        assert len(row[2]) == 99
        assert allequal(row[0], arange(0, type=Int32)*2+3)
        assert allequal(row[1], arange(10, type=Int32)*2+3)
        a = arange(99, type=Int32); a[1:11:2] = a[:5]*2+3
        assert allequal(row[2], a)

    def test07_out_of_range(self):
        "Checking out of range updates (first index)"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test07_out_of_range..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows

        try:
            vlarray[1000] = [1]
            print "row-->", row
        except IndexError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next IndexError was catched!"
                print value
            self.fileh.close()
        else:
            (type, value, traceback) = sys.exc_info()
            self.fail("expected a IndexError and got:\n%s" % value)

    def test08_value_error(self):
        "Checking out value errors"
        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test08_value_error..." % self.__class__.__name__

        self.fileh = openFile(self.file, "a")
        vlarray = self.fileh.root.vlarray

        if verbose:
            print "Nrows in", vlarray._v_pathname, ":", vlarray.nrows

        try:
            vlarray[10,1:100] = [1]*10
            print "row-->", row
        except ValueError:
            if verbose:
                (type, value, traceback) = sys.exc_info()
                print "\nGreat!, the next ValueError was catched!"
                print value
            self.fileh.close()
        else:
            (type, value, traceback) = sys.exc_info()
            self.fail("expected a ValueError and got:\n%s" % value)

class CopyTestCase(unittest.TestCase):

    def test01_copy(self):
        """Checking VLArray.copy() method """

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an Vlarray
        arr = Int16Atom(shape=2, flavor="python")
        array1 = fileh.createVLArray(fileh.root, 'array1', arr, "title array1")
        array1.append([[2,3]])
        array1.append(())  # an empty row
        array1.append([[3, 457],[2,4]])

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy it to another location
        array2 = array1.copy('/', 'array2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        if verbose:
            print "array1-->", repr(array1.read())
            print "array2-->", repr(array2.read())
            #print "dirs-->", dir(array1), dir(array2)
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Check that all the elements are equal
        assert array1.read() == array2.read()

        # Assert other properties in array
        assert array1.nrows == array2.nrows
        assert array1.shape == array2.shape
        assert array1.atom.flavor == array2.atom.flavor
        assert array1.atom.type == array2.atom.type
        assert array1.atom.itemsize == array2.atom.itemsize
        assert repr(array1.atom) == repr(array1.atom)

        assert array1.title == array2.title

        # Close the file
        fileh.close()
        os.remove(file)

    def test02_copy(self):
        """Checking VLArray.copy() method (where specified)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test02_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        arr = Int16Atom(shape=2, flavor="python")
        array1 = fileh.createVLArray(fileh.root, 'array1', arr, "title array1")
        array1.append([[2,3]])
        array1.append(())  # an empty row
        array1.append([[3, 457],[2,4]])

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy to another location
        group1 = fileh.createGroup("/", "group1")
        array2 = array1.copy(group1, 'array2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.group1.array2

        if verbose:
            print "array1-->", array1.read()
            print "array2-->", array2.read()
            #print "dirs-->", dir(array1), dir(array2)
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Check that all the elements are equal
        assert array1.read() == array2.read()

        # Assert other properties in array
        assert array1.nrows == array2.nrows
        assert array1.shape == array2.shape
        assert array1.atom.flavor == array2.atom.flavor
        assert array1.atom.type == array2.atom.type
        assert array1.atom.itemsize == array2.atom.itemsize
        assert repr(array1.atom) == repr(array1.atom)
        assert array1.title == array2.title

        # Close the file
        fileh.close()
        os.remove(file)

    def test03_copy(self):
        """Checking VLArray.copy() method (NumPy flavor)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        if numpy_imported:
            arr = Int16Atom(shape=2, flavor="numpy")
        else:
            arr = Int16Atom(shape=2, flavor="numarray")
        array1 = fileh.createVLArray(fileh.root, 'array1', arr,
                                     "title array1")
        array1.append([[2,3]])
        array1.append(())  # an empty row
        array1.append([[3, 457],[2,4]])

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy to another location
        array2 = array1.copy('/', 'array2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        if verbose:
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Assert other properties in array
        assert array1.nrows == array2.nrows
        assert array1.shape == array2.shape
        assert array1.atom.flavor == array2.atom.flavor  # Very important here
        assert array1.atom.type == array2.atom.type
        assert array1.atom.itemsize == array2.atom.itemsize
        assert repr(array1.atom) == repr(array1.atom)
        assert array1.title == array2.title

        # Close the file
        fileh.close()
        os.remove(file)

    def test03a_copy(self):
        """Checking VLArray.copy() method (Numeric flavor)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03a_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        if numeric:
            arr = Int16Atom(shape=2, flavor="numeric")
        else:
            arr = Int16Atom(shape=2, flavor="numarray")
        array1 = fileh.createVLArray(fileh.root, 'array1', arr,
                                     "title array1")
        array1.append([[2,3]])
        array1.append(())  # an empty row
        array1.append([[3, 457],[2,4]])

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy to another location
        array2 = array1.copy('/', 'array2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        if verbose:
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Assert other properties in array
        assert array1.nrows == array2.nrows
        assert array1.shape == array2.shape
        assert array1.atom.flavor == array2.atom.flavor  # Very important here
        assert array1.atom.type == array2.atom.type
        assert array1.atom.itemsize == array2.atom.itemsize
        assert repr(array1.atom) == repr(array1.atom)
        assert array1.title == array2.title

        # Close the file
        fileh.close()
        os.remove(file)

    def test03b_copy(self):
        """Checking VLArray.copy() method (Python flavor)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test03_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        arr = Int16Atom(shape=2, flavor="python")
        array1 = fileh.createVLArray(fileh.root, 'array1', arr,
                                     "title array1")
        array1.append(((2,3),))
        array1.append(())  # an empty row
        array1.append(((3, 457),(2,4)))

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy to another location
        array2 = array1.copy('/', 'array2')

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        if verbose:
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Assert other properties in array
        assert array1.nrows == array2.nrows
        assert array1.shape == array2.shape
        assert array1.atom.flavor == array2.atom.flavor  # Very important here
        assert array1.atom.type == array2.atom.type
        assert array1.atom.itemsize == array2.atom.itemsize
        assert repr(array1.atom) == repr(array1.atom)
        assert array1.title == array2.title

        # Close the file
        fileh.close()
        os.remove(file)

    def test04_copy(self):
        """Checking VLArray.copy() method (checking title copying)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test04_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        atom = Int16Atom(shape=2)
        array1 = fileh.createVLArray(fileh.root, 'array1', atom,
                                     "title array1")
        array1.append(((2,3),))
        array1.append(())  # an empty row
        array1.append(((3, 457),(2,4)))
        # Append some user attrs
        array1.attrs.attr1 = "attr1"
        array1.attrs.attr2 = 2

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy it to another Array
        array2 = array1.copy('/', 'array2', title="title array2")

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        # Assert user attributes
        if verbose:
            print "title of destination array-->", array2.title
        array2.title == "title array2"

        # Close the file
        fileh.close()
        os.remove(file)

    def test05_copy(self):
        """Checking VLArray.copy() method (user attributes copied)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an Array
        atom=Int16Atom(shape=2)
        array1 = fileh.createVLArray(fileh.root, 'array1', atom,
                                     "title array1")
        array1.append(((2,3),))
        array1.append(())  # an empty row
        array1.append(((3, 457),(2,4)))
        # Append some user attrs
        array1.attrs.attr1 = "attr1"
        array1.attrs.attr2 = 2

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy it to another Array
        array2 = array1.copy('/', 'array2', copyuserattrs=1)

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        if verbose:
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Assert user attributes
        array2.attrs.attr1 == "attr1"
        array2.attrs.attr2 == 2

        # Close the file
        fileh.close()
        os.remove(file)

    def notest05b_copy(self):
        """Checking VLArray.copy() method (user attributes not copied)"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test05b_copy..." % self.__class__.__name__

        # Create an instance of an HDF5 Table
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        atom=Int16Atom(shape=2)
        array1 = fileh.createVLArray(fileh.root, 'array1', atom,
                                     "title array1")
        array1.append(((2,3),))
        array1.append(())  # an empty row
        array1.append(((3, 457),(2,4)))
        # Append some user attrs
        array1.attrs.attr1 = "attr1"
        array1.attrs.attr2 = 2

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy it to another Array
        array2 = array1.copy('/', 'array2', copyuserattrs=0)

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "r")
            array1 = fileh.root.array1
            array2 = fileh.root.array2

        if verbose:
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)

        # Assert user attributes
        array2.attrs.attr1 == None
        array2.attrs.attr2 == None

        # Close the file
        fileh.close()
        os.remove(file)


class CloseCopyTestCase(CopyTestCase):
    close = 1

class OpenCopyTestCase(CopyTestCase):
    close = 0

import sys

class CopyIndexTestCase(unittest.TestCase):

    def test01_index(self):
        """Checking VLArray.copy() method with indexes"""

        if verbose:
            print '\n', '-=' * 30
            print "Running %s.test01_index..." % self.__class__.__name__

        # Create an instance of an HDF5 Array
        file = tempfile.mktemp(".h5")
        fileh = openFile(file, "w")

        # Create an VLArray
        atom = Int32Atom(shape=(2,), flavor="python")
        array1 = fileh.createVLArray(fileh.root, 'array1', atom, "t array1")
        # The next creates 20 rows of variable length
        r = []
        for row in range(20):
            r.append([[row, row+1]])
            array1.append([row, row+1])

        if self.close:
            if verbose:
                print "(closing file version)"
            fileh.close()
            fileh = openFile(file, mode = "a")
            array1 = fileh.root.array1

        # Copy to another array
        array2 = array1.copy("/", 'array2',
                             start=self.start,
                             stop=self.stop,
                             step=self.step)

        r2 = r[self.start:self.stop:self.step]
        if verbose:
            print "r2-->", r2
            print "array2-->", array2[:]
            print "attrs array1-->", repr(array1.attrs)
            print "attrs array2-->", repr(array2.attrs)
            print "nrows in array2-->", array2.nrows
            print "and it should be-->", len(r2)
        # Check that all the elements are equal
        assert r2 == array2[:]
        # Assert the number of rows in array
        assert len(r2) == array2.nrows

        # Close the file
        fileh.close()
        os.remove(file)


class CopyIndex1TestCase(CopyIndexTestCase):
    close = 0
    start = 0
    stop = 7
    step = 1

class CopyIndex2TestCase(CopyIndexTestCase):
    close = 1
    start = 0
    stop = -1
    step = 1

class CopyIndex3TestCase(CopyIndexTestCase):
    close = 0
    start = 1
    stop = 7
    step = 1

class CopyIndex4TestCase(CopyIndexTestCase):
    close = 1
    start = 0
    stop = 6
    step = 1

class CopyIndex5TestCase(CopyIndexTestCase):
    close = 0
    start = 3
    stop = 7
    step = 1

class CopyIndex6TestCase(CopyIndexTestCase):
    close = 1
    start = 3
    stop = 6
    step = 2

class CopyIndex7TestCase(CopyIndexTestCase):
    close = 0
    start = 0
    stop = 7
    step = 10

class CopyIndex8TestCase(CopyIndexTestCase):
    close = 1
    start = 6
    stop = -1  # Negative values means starting from the end
    step = 1

class CopyIndex9TestCase(CopyIndexTestCase):
    close = 0
    start = 3
    stop = 4
    step = 1

class CopyIndex10TestCase(CopyIndexTestCase):
    close = 1
    start = 3
    stop = 4
    step = 2

class CopyIndex11TestCase(CopyIndexTestCase):
    close = 0
    start = -3
    stop = -1
    step = 2

class CopyIndex12TestCase(CopyIndexTestCase):
    close = 1
    start = -1   # Should point to the last element
    stop = None  # None should mean the last element (including it)
    step = 1


#----------------------------------------------------------------------

def suite():
    theSuite = unittest.TestSuite()
    global numeric
    niter = 1

    #theSuite.addTest(unittest.makeSuite(NumericFlavorTestCase))
    #theSuite.addTest(unittest.makeSuite(BasicNumericTestCase))
    #theSuite.addTest(unittest.makeSuite(SetRangeTestCase))
    #theSuite.addTest(unittest.makeSuite(CopyIndex3TestCase))
    #theSuite.addTest(unittest.makeSuite(MDTypesNumArrayTestCase))
    for n in range(niter):
        theSuite.addTest(unittest.makeSuite(BasicNumArrayTestCase))
        if numeric:
            theSuite.addTest(unittest.makeSuite(BasicNumericTestCase))
        if numpy_imported:
            theSuite.addTest(unittest.makeSuite(BasicNumpyTestCase))
        theSuite.addTest(unittest.makeSuite(BasicPythonTestCase))
        theSuite.addTest(unittest.makeSuite(ZlibComprTestCase))
        theSuite.addTest(unittest.makeSuite(LZOComprTestCase))
        theSuite.addTest(unittest.makeSuite(BZIP2ComprTestCase))
        theSuite.addTest(unittest.makeSuite(TypesNumArrayTestCase))
        theSuite.addTest(unittest.makeSuite(MDTypesNumArrayTestCase))
        theSuite.addTest(unittest.makeSuite(OpenAppendShapeTestCase))
        theSuite.addTest(unittest.makeSuite(CloseAppendShapeTestCase))
        theSuite.addTest(unittest.makeSuite(PythonFlavorTestCase))
        if numeric:
            theSuite.addTest(unittest.makeSuite(NumericFlavorTestCase))
        if numpy_imported:
            theSuite.addTest(unittest.makeSuite(NumpyFlavorTestCase))
        theSuite.addTest(unittest.makeSuite(NumArrayFlavorTestCase))
        theSuite.addTest(unittest.makeSuite(ReadRangeTestCase))
        theSuite.addTest(unittest.makeSuite(GetItemRangeTestCase))
        theSuite.addTest(unittest.makeSuite(SetRangeTestCase))
        theSuite.addTest(unittest.makeSuite(ShuffleComprTestCase))
        theSuite.addTest(unittest.makeSuite(Fletcher32TestCase))
        theSuite.addTest(unittest.makeSuite(AllFiltersTestCase))
        theSuite.addTest(unittest.makeSuite(CloseCopyTestCase))
        theSuite.addTest(unittest.makeSuite(OpenCopyTestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex1TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex2TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex3TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex4TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex5TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex6TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex7TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex8TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex9TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex10TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex11TestCase))
        theSuite.addTest(unittest.makeSuite(CopyIndex12TestCase))

    return theSuite

if __name__ == '__main__':
    unittest.main( defaultTest='suite' )