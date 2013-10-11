from collective.recaptcha.settings import getRecaptchaSettings
from groundwire.template.setuphandlers import expected_mailhost
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

class TemporaryContentViewlet(ViewletBase):
    
    render = ViewPageTemplateFile('temporary_content.pt')
    
    def getItems(self):
        
        cat = getToolByName(self.context, 'portal_catalog')
        return cat.searchResults(
            SearchableText='TK',
            )

class PerformanceChecksViewlet(ViewletBase):
    
    render = ViewPageTemplateFile('performance.pt')
    
    def cssDebugModeStatus(self):
        tool = getToolByName(self.context, 'portal_css')
        status = tool.getDebugMode() and 'On' or 'Off'
        return status
        
    def javascriptDebugModeStatus(self):
        tool = getToolByName(self.context, 'portal_javascripts')
        status = tool.getDebugMode() and 'On' or 'Off'
        return status
        
    def kssDebugModeStatus(self):
        tool = getToolByName(self.context, 'portal_kss')
        status = tool.getDebugMode() and 'On' or 'Off'
        return status

    def cachingStatus(self):
        try:
            from plone.registry.interfaces import IRegistry
            from plone.caching.interfaces import ICacheSettings
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ICacheSettings)
            status = settings.enabled and 'On' or 'Off'
        except (AttributeError,KeyError,ComponentLookupError):
            status = 'Not Installed'
        return status
        
    def customFolderCount(self):
        tool = getToolByName(self.context, 'portal_skins')
        return len(tool.custom.objectIds())

class ConfigurationChecksViewlet(ViewletBase):

    render = ViewPageTemplateFile('configuration.pt')

    def recaptchaStatus(self):
        """
        Returns True if collective.recaptcha is properly configured.
        """
        
        settings = getRecaptchaSettings()
        if settings.public_key and settings.private_key:
            return True
        return False

    def expectedMailHost(self):
        """
        Returns the expected mail host.
        """

        return expected_mailhost()