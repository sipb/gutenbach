from .value import Value
import sys
import struct
import logging

# initialize logger
logger = logging.getLogger(__name__)

class Attribute(object):
    """In addition to what the RFC reports, an attribute has an
    'attribute tag', which specifies what type of attribute it is.  It
    is 1 bytes long, and comes before the list of values.

    From RFC 2565:

    Each attribute consists of:
    -----------------------------------------------
    |                   value-tag                 |   1 byte
    -----------------------------------------------
    |               name-length  (value is u)     |   2 bytes
    -----------------------------------------------
    |                     name                    |   u bytes
    -----------------------------------------------
    |              value-length  (value is v)     |   2 bytes
    -----------------------------------------------
    |                     value                   |   v bytes
    -----------------------------------------------

    An additional value consists of:
    -----------------------------------------------------------
    |                   value-tag                 |   1 byte  |
    -----------------------------------------------           |
    |            name-length  (value is 0x0000)   |   2 bytes |
    -----------------------------------------------           |-0 or more
    |              value-length (value is w)      |   2 bytes |
    -----------------------------------------------           |
    |                     value                   |   w bytes |
    -----------------------------------------------------------

    """

    def __init__(self, name=None, values=None):
        """Initialize an Attribute.  This function can be called in
        three different ways:

            Attribute() -- creates an empty Attribute

            Attribute(name) -- creates an empty Attribute with a name

            Attribute(name, values) -- creates an Attribute
            initialized with a name and list of values
        
        Arguments:

            name -- the name of the attribute

            values -- a list of Values.  May not be empty.

        """

        if name is not None and not isinstance(name, str):
            raise ValueError("attribute name must be a string")
        if values is None:
            values = []
        for value in values:
            if not isinstance(value, Value):
                raise ValueError("value %s must be of type Value" % (value,))

        self.name = name
        self.values = values

    def __cmp__(self, other):
        eq = self.name == other.name
        for v1, v2 in zip(self.values, other.values):
            eq = eq and (v1 == v2)
        return 0 if eq else 1

    @property
    def packed_value(self):
        """Packs the attribute data into binary data.
        
        """

        if self.name is None:
            raise ValueError, "cannot pack unnamed attribute"
        if len(self.values) == 0:
            raise ValueError, "cannot pack empty attribute"

        # get the binary data for all the values
        values = []
        for v, i in zip(self.values, xrange(len(self.values))):

            # get the name length (0 for everything but the first
            # value)
            name_length = len(self.name) if i == 0 else 0

            logger.debug("dumping name : %s" % self.name)
            logger.debug("dumping name_length : %i" % name_length)
            logger.debug("value tag : 0x%x" % v.tag)

            # get the binary value
            value_bin = v.packed_value
            # get the value length
            value_length = len(value_bin)

            logger.debug("dumping value : %s" % v.value)
            logger.debug("dumping value_length : %i" % value_length)

            # the value tag in binary
            tag_bin = struct.pack('>b', v.tag)
            # the name length in binary
            name_length_bin = struct.pack('>h', name_length)
            # the name in binary
            name_bin = self.name
            # the value length in binary
            value_length_bin = struct.pack('>h', value_length)

            # add the binary value to the list of values
            vlist = [tag_bin, name_length_bin, value_length_bin, value_bin]
            if i == 0:
                vlist.insert(2, name_bin)
            values.append(''.join(vlist))

        # concatenate everything together and return it along with the
        # total length of the attribute
        return ''.join(values)

    @property
    def packed_value_size(self):
        """Gets the total size of the attribute.
        
        """

        return len(self.packed_value)

    total_size = packed_value_size

    def __str__(self):
        if len(self.values) > 0:
            values = [str(v) for v in self.values]
        else:
            values = "None"

        if self.name is None:
            name = "None"
        else:
            name = self.name
        
        return "%s: %s" % (name, str(values))

    def __repr__(self):
        return '<IPPAttribute (%r, %r)>' % (self.name, self.values)
