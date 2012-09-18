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

class DERItem:
    def __init__(self, stream):
        self.tag, self.structured = self._decodeT(stream)
        self.length = self._decodeL(stream)

        if self.structured is True:
            self.value = []     # create a list

            l = self.length
            while l>0:
                subitem = DERItem(stream)
                self.value.append(subitem) # add the subitem
                l -= subitem.length
                print("content={0}".format(subitem))
                print("l={0}".format(l))

        else:
            self.value = self._decodeV(stream, self.length) # get value
            
    def __str__(self):
        if self.structured is True:
            return ','.join(str(item) for item in self.value)
        else:
            return self.value.encode('hex')

         
    def _decodeT(self, stream):
        
        firstbyte = ord(stream.read(1)[0]) # read 1 byte

        structured = firstbyte & 0b00100000 == 0b00100000
        
        if firstbyte & 0b00011111 == 0b00011111:
            # we are in long form. Fetch each subsequent byte, base 128, until
            # we stumble upon last byte, (which has bit8 set to 0)
            tag = 0
            while True:
                nextbyte = stream.read(1)
                tag = (tag<<7) + nextbyte & 0x7f # shift and add base 128
                if nextbyte & 0x80 == 0:
                    break       # exit when bit 8 is null

        else:
            # we are in the short form (easiest)
            tag = firstbyte & 0b00011111
        
        return tag, structured



    def _decodeL(self, stream):

        firstbyte = ord(stream.read(1)[0]) # read 1 byte
        length = 0

        if firstbyte & 0x80 == 0x80:
            # long form
            for x in range(firstbyte & 0x7f):
                length <<= 8
                length += ord(stream.read(1)[0])

        else:
            # short form
            length = firstbyte & 0x7f
 
        print("Length found:{0}".format(length))
        return length

    def _decodeV(self, stream, length):
        return stream.read(length)
        

if __name__ == '__main__':
    
    with open('csr.der', 'rb') as p10:
        D = DERItem(p10)
        
        print(D)

