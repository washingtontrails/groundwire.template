from Products.CMFCore.DirectoryView import registerDirectory
product_globals = globals()
# Make the skins available as DirectoryViews
registerDirectory('skins', globals())

def initialize(context):
    """Intializer called when used as a Zope 2 product."""

# patch plone.locking to have a timeout of an hour
from plone.locking import lockable
lockable.MAXTIMEOUT = 60 * 60L
