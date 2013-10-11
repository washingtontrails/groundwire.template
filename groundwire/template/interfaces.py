from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager

class IGroundwireTemplateLayer(IDefaultBrowserLayer):
    """ Browser layer for the Groundwire template
    """
    
class IPrelaunchViewletManager(IViewletManager):
    """ Marker interface for the viewlet manager for pre-launch status checks
    """
