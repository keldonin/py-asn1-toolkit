#!/usr/bin/pyhon
#
#


from __future__ import print_function
import operator


class ASN1:
    
    # typeclass possible values
    PRIMITIVE=1
    CONSTRUCTED=2
    ANY=3
    
    _typeclassname = { PRIMITIVE : 'ASN1.PRIMITIVE', CONSTRUCTED : 'ASN1.CONSTRUCTED', ANY : 'ASN1.ANY' }

        
    def __init__(self, name, tag, typeclass, value=None, optional=False ):

        self._name = name.upper() # ASN1 is always in capital letters
        self._tag  = tag

        if typeclass not in ASN1._typeclassname.keys():
            raise ValueError("typeclass argument must be one of (ASN1.PRIMITIVE, ASN1.CONSTRUCTED, ASN1.ANY)")

        self._typeclass = typeclass
        
        if value is None:
            self.value = None

        elif typeclass == ASN1.PRIMITIVE:
            self.value = value

        else: #  typeclass == ASN1.CONSTRUCTED
            self.value = list() 
            if hasattr(value,'__iter__'):
                for item in value: # iterate and assign
                    self.value.append(item)

            else:       # assign the singleton
                self.value.append(value)

        self._optional = optional

    def __str__(self):
        if self._typeclass == ASN1.PRIMITIVE or self.value is None:
            
            rcval = self.value
        else:
            rcval = ', '.join( str(item) for item in self.value)
            
            
        rcstr = 'ASN1(name={0}, tag={1}, typeclass={2}, value={3}, optional={4})'

        return rcstr.format( self._name,
                             self._tag,
                             ASN1.typeclassname(self._typeclass),
                             rcval,
                             self._optional)

    def complieswith(self, other):
        """
        check if the object can comply with given ASN.1 structure
        passed as an argument.
        returns True or False.
        """
        pass
# TODO

    @property
    def name(self):
        return self._name

    @property
    def typeclass(self):
        return ASN1.typeclassname[self._typeclass]

    @property
    def tag(self):
        return self._tag

    @property
    def optional(self):
        return self._optional

    @property
    def isabstract(self):
        """
        isabstract: object is abstract if it has no value
        """

        # An object is abstract in the following cases:
        # * there is an attribute _abstract, set to True
        # * the type is PRIMITIVE, and the value is not None
        # * the type is CONSTRUCTED, and :
        #   - value attribute is None
        #   - at least one item from value is abstract.

        if hasattr(self,'_abstract'):
            if self._abstract is True:
                return True

        if self._typeclass is ASN1.PRIMITIVE:
            return self.value is None
        else: #  typeclass == ASN1.CONSTRUCTED
            if self.value is None:
                return True
            else:
                return reduce( operator.or_, [ elem.isabstract for elem in self.value ] )
            


class Integer(ASN1):
    """ASN1 Integer"""

    def __init__(self, tag=0x02, value=None, optional=False):
        ASN1.__init__(self, 'INTEGER', tag, ASN1.PRIMITIVE, int(value), optional=optional)


class PrintableString(ASN1):
    """ASN1 PrintableString"""
    def __init__(self, tag=0x13, value=None, optional=False):
        ASN1.__init__(self, 'PRINTABLESTRING', tag, ASN1.PRIMITIVE, str(value))


class Sequence(ASN1):
    """ASN1 Sequence"""
    
    def __init__(self, value=None, optional=False, sizemax=1000):
        ASN1.__init__(self, 'SEQUENCE', ASN1.CONSTRUCTED, value)
        self._sizemin=1
        self._sizemax=sizemax

class SequenceOf(ASN1):
    """ASN1 Sequence Of"""
    
    def __init__(self, value=None, optional=False, sizemax=1000):
        ASN1.__init__(self, 'SEQUENCEOF', ASN1.CONSTRUCTED, value)
        self._sizemin=1
        self._sizemax=sizemax


class Set(ASN1):
    """ASN1 Sequence"""
    
    def __init__(self, value, optional=False, sizemax=1000):
        ASN1.__init__(self, 'SEQUENCE', ASN1.CONSTRUCTED, value)
        self._sizemin=1
        self._sizemax=sizemax

class SetOf(ASN1):
    """ASN1 Sequence Of"""
    
    def __init__(self, value=None, optional=False):
        ASN1.__init__(self, 'SEQUENCEOF', ASN1.CONSTRUCTED, value)
        self._sizemin=1
        self._sizemax=sizemax
    

class Choice(ASN1):
    """ASN1 Choice"""

    def __init__(self, value=None, optional=False):
        ASN1.__init__(self, 'SEQUENCEOF', ASN1.CONSTRUCTED, value)

        # for this object, we set self._abstract to force it to remain abstract
        # even if value is not None.
        self._abstract = True


class Any(ASN1):
    """ASN1 Any"""

    def __init__(self, optional=False):
        ASN1.__init__(self, 'ANY', ASN1.CONSTRUCTED, value=None)

        # for this object, we set self._abstract to force it to remain abstract
        # even if value is not None.
        self._abstract = True
    
