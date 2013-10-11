from Acquisition import aq_inner, aq_chain
from zope.publisher.browser import BrowserPage
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces.image import IATImage

class SiteBanners(BrowserPage):
    """
    The new Plone 4 way of generating CSS for banners. See
    docs/SITE_BANNERS.txt for more information.
    """

    __call__ = ViewPageTemplateFile("site_banners.css.pt")
    
    banner_id = 'banner'
    
    def banner_brains(self):
        """
        Returns a list of banner brains used the generate the CSS.
        """
        
        catalog = getToolByName(self.context, 'portal_catalog')
        
        return catalog.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'object_provides': IATImage.__identifier__,
            'sort_on': 'getObjPositionInParent',
        })
        
    def subsection_classes(self):
        """
        Returns a list of subsection classes that can be used on a container
        for the banner element to allow for subsection banners.
        """
        
        portal_url = getToolByName(self.context, 'portal_url')
        classes = []
        
        for obj in aq_chain(aq_inner(self.context)):
            if IContentish.providedBy(obj):
                content_path = portal_url.getRelativeContentPath(obj)
                if content_path and len(content_path) > 1:
                    classes.append('section-%s' % '-'.join(content_path))
        return ' '.join(classes)
        