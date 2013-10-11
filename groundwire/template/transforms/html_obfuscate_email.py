import re

from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import ITransform

class HTMLObfuscateEmail:
    """Transform enables inline citations and bibitems embedded in text"""
    implements(ITransform)
    __name__ = "html_obfuscate_email"
    inputs = ('text/html',)
    output = "text/x-html-emailobfuscated"

    def __init__(self, name=None):
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, data, idata, filename=None, **kwargs):
        """convert the data, store the result in idata and return that
        optional argument filename may give the original file name of received data
        additional arguments given to engine's convert, convertTo or __call__ are passed back to the transform

        The object on which the translation was invoked is available as context
        (default: None)
        """
        
        # obfuscate mailto links
        r1 = re.compile(r'href="mailto:')
        data = r1.sub('href="&#0109;ailto&#0058;', data)
        
        # obfuscate other e-mail addresses
        r2 = re.compile(r'@')
        data = r2.sub('&#0064;', data)
        
        idata.setData(data)
        return idata


def register():
    return HTMLObfuscateEmail()

def initialize():
    engine = getToolByName(portal, 'portal_transforms', None)
    if engine is not None:
        engine.registerTransform(register())
