#
# DER encoder - decoder
#

#
# The aim is to create a representation of the DER-encoded object.
# To do that, one bases upon structured bit.
# if the object is a structured, it may contain 0 or more subitems.
# else, we are a primitive. Just parse the content.


#
# step 1: decode tag and length. This sets the maximum size of a file.
#

from __future__ import print_function


class DERAtom(object):
    """
    DERAtom is the subclass for all DERTag, DERLen and DERValue.
    It contains some commodities useful to keep track of eaten bytes
    while progressing through stream.
    """
    def __init__(self, stream):
        self._eaten = 0      # we have read nothing so far
        print("self._eaten = {0}".format(self._eaten))

    def _read(self,stream,size=1):
        """
        _read() is called to get the next byte(s) from stream
        and increase len counter accordingly.
        """
        datum = stream.read(size)
        self._eaten += size
        
        return datum
    

    def __len__(self):
        """allows to perform len() on DERxxx instances."""
        return self._eaten

        

class DERTag(DERAtom):
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
        
    def __int__(self):
        """
        returns DERTag as integer
        """
        return self._tag
    
        
class DERLen(DERAtom):
    
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
 
        print("Length found:{0}".format(self._len))
    
    def __int__(self):
        """
        return DERLen as integer
        """
        return self._len


class DERVal(DERAtom):

    def __init__(self, stream, mytag, mylen):

        super(DERVal, self).__init__(stream)
        
        # simple trick: we either fill _vallist or _val,
        # if the tag is structured or not.

        
        self._vallist = self._val= None
        
        if mytag.structured is True:
            self._vallist = []     # create a list

            l = int(mylen)
            while l>0:
                subitem = DERItem(stream)
                self._vallist.append(subitem) # add the subitem
                l -= len(subitem)
                print("content={0}".format(subitem))
                print("l={0}".format(l))

        else:
            self._val = self._read(stream,int(mylen)) # get value

    def __str__(self):
        if self._vallist is not None:
            return '[' + ','.join(str(item) for item in self._val) + ']'
        else:
            assert(self._val is not None)
            return self._val

        
class DERObject(object):
    def __init__(self, stream):
        self.tag = DERTag(stream)
        self.len = DERLen(stream)
        self.val = DERVal(stream, self.tag, self.len)
            
    
    def __len__(self):
        return len(self.tag) + len(self.len) + len(self.val)
    

    def __str__(self):
        if self.tag.structured is True:
            return ','.join(str(item) for item in self.val)
        else:
            return self.val.encode('hex')

         

if __name__ == '__main__':
    
    with open('csr.der', 'rb') as p10:
        D = DERObject(p10)
        
        print(D)

