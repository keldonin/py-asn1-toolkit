#
# DER encoder - decoder
#

#
# The aim is to create a representation of the DER-encoded object.
# To do that, one bases upon structured bit.
# if the object is a structured, it may contain 0 or more subitems.
# else, we are a primitive. Just parse the content.

from __future__ import print_function
import operator

# Number of times to indent output
# A list is used to force access by reference

__report_indent = [0]

def instrument(fn):
    """Decorator to print information about a function
    call for use while debugging.
    Prints function name, arguments, and call number
    when the function is called. Prints this information
    again along with the return value when the function
    returns.
    """

    def wrap(*params,**kwargs):
        call = wrap.callcount = wrap.callcount + 1
        indent_len = 2
        
        indent = '-' * __report_indent[0] * indent_len + '+ '

        fc = "%s(%s)" % (fn.__name__, ', '.join(
            [a.__repr__() for a in params] +
            ["%s = %s" % (a, repr(b)) for a,b in kwargs.items()]
        ))

        print ("%s%s called C[#%s] L[#%s]" % (indent, fc, call, __report_indent[0]))
        __report_indent[0] += 1
        ret = fn(*params,**kwargs)
        __report_indent[0] -= 1
        print ("%s%s returned %s C[#%s] L[#%s]" % (indent, fc, repr(ret), call, __report_indent[0]))
        
        return ret
    
    wrap.callcount = 0    
    return wrap

######################################################################
#
# step 1: decode tag and length. This sets the maximum size of a file.
#


class DERAtom(object):
    """
    DERAtom is the subclass for all DERTag, DERLen and DERValue.
    It contains some commodities useful to keep track of eaten bytes
    while progressing through stream.
    """
    
    def __init__(self, stream):
        self._eaten = 0      # we have read nothing so far
        self._bytes = bytearray()
        
    def _read(self,stream,size=1):
        """
        _read() is called to get the next byte(s) from stream
        and increase len counter accordingly.
        """
        datum = stream.read(size)
                    
        self._eaten += size
        self._bytes.extend(datum)        
        return datum
    
    def __len__(self):
        """allows to perform len() on DERxxx instances."""
        return self._eaten

    @property
    def raw(self):
        """recover raw bytes"""
        return self._bytes
    

class DERTag(DERAtom):

#    @instrument
    def __init__(self, stream):
        
        super(DERTag, self).__init__(stream)
        
        firstbyte = ord(self._read(stream)[0]) # read 1 byte
        self.structured = firstbyte & 0b00100000 == 0b00100000
        
        if firstbyte & 0b00011111 == 0b00011111:
            # we are in long form. Fetch each subsequent byte, base 128, until
            # we stumble upon last byte, (which has bit8 set to 0)
            self._tag = 0
            while True:
                nextbyte = self._read(stream)
                self._tag = (self._tag<<7) + nextbyte & 0x7f # shift and add base 128
                if nextbyte & 0x80 == 0:
                    break       # exit when bit 8 is null
        else:
            # we are in the short form (easiest)
            self._tag = firstbyte & 0b00011111
            
    @property
    def asint(self):
        """
        returns DERTag as integer
        """
        return self._tag
    
    @property
    def ashex(self):
        """
        returns DERTag as hex string
        """
        return hex(self._tag)
    
        
class DERLen(DERAtom):
    
#    @instrument
    def __init__(self,stream):

        super(DERLen, self).__init__(stream)

        firstbyte = ord(self._read(stream)[0]) # read 1 byte
        self._len = 0

        if firstbyte & 0x80 == 0x80:
            # long form
            for x in range(firstbyte & 0x7f):
                self._len <<= 8
                self._len += ord(self._read(stream)[0])

        else:
            # short form
            self._len = firstbyte & 0x7f
 
    @property
    def asint(self):
        """
        return DERLen as integer
        """
        return self._len

    @property
    def ashex(self):
        """
        return DERLen as hex string
        """
        return hex(self._len)


class DERVal(DERAtom):

#    @instrument
    def __init__(self, stream, tag, datalen):

        super(DERVal, self).__init__(stream)
        
        # simple trick: we either fill _vallist or _val,
        # if the tag is structured or not.

        self._vallist = self._val= None
        
        if tag.structured is True:
            self._vallist = []     # create a list

            l = datalen
            while l>0:
                subitem = DERObject(stream)
                self._vallist.append(subitem) # add the subitem
                l -= len(subitem)

        else:
            self._val = self._read(stream,datalen) # get value
    
    def __len__(self):
        # __len__ of DERVal must be overridden,
        # to turn it into a recursive sum of subitems.
        if self._vallist is not None:
            if len(self._vallist)==0:
                return 0
            else:
                return reduce(operator.add, [len(subitem) for subitem in self._vallist])
            pass
        else:
            return super(DERVal, self).__len__()

#    @instrument
    def __repr__(self):
        if self._vallist is not None:
            return '[' + ','.join(repr(item) for item in self._vallist) + ']'
        else:
            assert(self._val is not None)
            return self._val.encode('hex')

        
class DERObject(object):

#    @instrument
    def __init__(self, stream):
        self.tag = DERTag(stream)
        self.len = DERLen(stream)
        self.val = DERVal(stream, self.tag, self.len.asint)
            
#    @instrument    
    def __len__(self):
        return len(self.tag) + len(self.len) + len(self.val)
    
#    @instrument
    def __repr__(self):
        try:
            return "<DERObject at {3:#08x} T={0:s} L={1} V=<{2:s}>".format( self.tag.ashex, self.len.asint, self.val, id(self))
        except AttributeError:
            return "<{0} object at {1:#08x}>".format(self.__class__.__name__, id(self))
        
if __name__ == '__main__':
    
    print('-'*72)
    with open('csr.der', 'rb') as p10:
        D = DERObject(p10)
        print(D)

