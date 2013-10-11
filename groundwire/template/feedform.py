from zExceptions import NotFound
from zope.interface import implements
from zope.app.component.hooks import getSite
from collective.simplesocial.feedform.facebookfeedform import IFeedFormDataProvider

class ThankYouFeedFormDataProvider(object):
    """
    Use the URL from the request, not the absolute URL of the context, when
    posting to Facebook from a PFG thank you page.
    """
    
    implements(IFeedFormDataProvider)
    
    def __init__(self, context):
        self.context = context
        
    def getSettings(self, defaults):
        return defaults

    def getAttachment(self):
        href = self.context.REQUEST.get('HTTP_REFERER', '') or \
            self.context.absolute_url()
        
        result = {
            'name': self.context.Title(),
            'href': href,
        }
        if hasattr(self.context, 'Description') and self.context.Description():
            result.update({'description': ' '.join(self.context.Description().split())})
        try:
            self.context.restrictedTraverse('image_tile')
            result.update({
                'media': [{
                    'type': 'image',
                    'src': self.context.absolute_url() + '/image_tile',
                    'href': href,
                }]
            })
        except (AttributeError, KeyError, NotFound):
            portal = getSite()
            base_props = portal.restrictedTraverse('base_properties')
            logo_name = getattr(base_props, 'logoName', None)
            if logo_name:
                result.update({
                    'media': [{
                        'type': 'image',
                        'src': '/'.join([portal.absolute_url(), logo_name, '@@facebook-thumbnail']),
                        'href': href,
                    }]
                })
        return result