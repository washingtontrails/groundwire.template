from zope import schema
from zope.interface import implements
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interface import IATTopic
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlet.collection import collection
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groundwire.template')

class IFeaturedItemPortlet(IPortletDataProvider):
    """
    A portlet that renders a featured item.
    """
    
    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u'Enter a title for the portlet. Otherwise, the title of'
            u' the featured item will be used.'),
        required=False
    )

    target_collection = schema.Choice(
        title=_(u"Source collection"),
        description=_(u'Find the collection that contains the featured item.'),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : IATTopic.__identifier__},
            default_query='path:'
        )
    )
                       
    random = schema.Bool(
        title=_(u'Select a random item'),
        description=_(u'If enabled, an item will be selected randomly from'
        u' the collection. Otherwise, the first result will be used.'),
        required=True,
        default=True
    )
    
    abstract = schema.Bool(
        title=_(u'Show item description instead of body text'),
        required=False,
        default=False
    )
    
    more_text = schema.TextLine(
        title=_(u"More link"),
        description=_(u'If you want a link to the source collection, enter'
            u' the text for it.'),
        required=False
    )

class Assignment(collection.Assignment):
    """
    Assignemnt of a featured item portlet.
    """
    
    implements(IFeaturedItemPortlet)
   
    header = u""
    target_collection=None
    limit = 1
    random = True
    show_more = True
    show_dates = False
    more_text = u''
    abstract = False

    def __init__(self, header=u"", target_collection=None, random=True, more_text=u'', abstract=False):
        self.header = header
        self.target_collection = target_collection
        self.random = random
        self.more_text = more_text
        self.abstract = abstract
        
    @property
    def title(self):
        """
        This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.header or _(u'Featured Item Portlet')
    
class Renderer(collection.Renderer):
    """
    Renderer for a featured item portlet.
    """
    
    _template = ViewPageTemplateFile('featureditem.pt')
    render = _template
    
class AddForm(base.AddForm):
    """
    Add form for a featured item portlet.
    """
    
    form_fields = form.Fields(IFeaturedItemPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    
    label = _(u"Add Featured Item Portlet")
    description = _(u"This portlet displays a featured item from a collection.")

    def create(self, data):
        return Assignment(**data)
    
class EditForm(base.EditForm):
    """
    Edit form for a featured item portlet.
    """
    
    form_fields = form.Fields(IFeaturedItemPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    
    label = _(u"Edit Featured Item Portlet")
    description = _(u"This portlet displays a featured item from a collection.")
