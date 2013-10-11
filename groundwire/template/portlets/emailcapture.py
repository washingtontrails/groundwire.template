from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize
from plone.memoize import ram

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from Products.PloneFormGen.interfaces import IPloneFormGenForm

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('groundwire.template')

class IEmailCapturePortlet(IPortletDataProvider):
    """
    A portlet that posts an e-mail address to a full e-mail capture form.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Enter the title of the portlet."),
        default=u"E-mail Sign-up",
        required=True
    )
    
    text = schema.Text(
        title=_(u"Introduction"),
        required=False
    )
    
    target_form = schema.Choice(
        title=_(u"Target form"),
        description=_(u"Find the PloneFormGen form that contains the full sign-up, \
            or enter a custom form action URL below."),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : IPloneFormGenForm.__identifier__},
            default_query='path:'
        )
    )
                       
    embed = schema.Bool(
        title=_(u"Embed the full form"),
        description=_(u"If enabled, the full sign-up form will be displayed in the \
        portlet. Otherwise only the e-mail address field will appear."),
        required=True,
        default=False
    )
    
    email_field_id = schema.TextLine(
        title=_(u"E-mail field ID"),
        description=_(u"Enter the ID of the e-mail field. If the full form is \
            embedded, this setting is ignored."),
        default=u"email",
        required=False
    )
    
    email_field_label = schema.TextLine(
        title=_(u"E-mail field label"),
        description=_(u"Enter the label for the e-mail field. If the full form is \
            embedded, this setting is ignored."),
        default=u"Your E-mail",
        required=False
    )
    
    conclusion = schema.Text(
        title=_(u"Conclusion"),
        required=False
    )

class Assignment(base.Assignment):
    """
    Portlet assignment.    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IEmailCapturePortlet)

    header = u""
    text = u""
    target_form = None
    embed = False
    email_field_id = u""
    email_field_label = u""
    conclusion = u""

    def __init__(self, header=u"", text=u"", target_form=None,
        embed=False, email_field_id=u"", email_field_label=u"", conclusion=u""):
        self.header = header
        self.text = text
        self.target_form = target_form
        self.embed = embed
        self.email_field_id = email_field_id
        self.email_field_label = email_field_label
        self.conclustion = conclusion

    @property
    def title(self):
        """
        This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


def form_url_cachekey(func, instance):
    return hash((func.__name__, instance.data.target_form))
        
class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('emailcapture.pt')
    render = _template

    @ram.cache(form_url_cachekey)
    def form_url(self):
        form = self.form()
        if form is None:
            return None
        else:
            return form.absolute_url()
            
    def embedded_form(self):
        if self.data.embed:
            return self.form().restrictedTraverse('@@embedded', default=None)()
        return None
        
    @memoize
    def form(self):
        """
        Get the target form folder.
        """
        
        form_path = self.data.target_form
        if not form_path:
            return None

        if form_path.startswith('/'):
            form_path = form_path[1:]
        
        if not form_path:
            return None

        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )
        portal = portal_state.portal()
        return portal.restrictedTraverse(form_path, default=None)
        
class AddForm(base.AddForm):
    """
    Portlet add form.
    """
    
    form_fields = form.Fields(IEmailCapturePortlet)
    form_fields['target_form'].custom_widget = UberSelectionWidget
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['conclusion'].custom_widget = WYSIWYGWidget
    
    label = _(u"Add E-mail Capture Portlet")
    description = _(u"This portlet display an e-mail sign-up form.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """
    Portlet edit form.
    """

    form_fields = form.Fields(IEmailCapturePortlet)
    form_fields['target_form'].custom_widget = UberSelectionWidget
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['conclusion'].custom_widget = WYSIWYGWidget

    label = _(u"Edit E-mail Capture Portlet")
    description = _(u"This portlet display an e-mail sign-up form.")
