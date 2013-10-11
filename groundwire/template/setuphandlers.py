"""
Groundwire Template setup handlers.

Note that this is now being called only on Product install, so we 
don't blow away existing content.
"""
import socket
import logging
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry import MimeTypeItem
from zope.component import getUtility
from plone.app.controlpanel.filter import IFilterSchema
from plone.contentrules.engine.interfaces import IRuleStorage

logger = logging.getLogger('groundwire.template')

def expected_mailhost():
    ip = socket.gethostbyname(socket.gethostname())
    try:
        if socket.gethostbyaddr(ip)[0].endswith('ec2.internal'):
            return 'relay.groundwire.org'
        else:
            return '127.0.0.1'
    # Unknown host
    except socket.herror:
        return '127.0.0.1'

class GroundwireTemplateGenerator:
    
    def publishContent(self, p):
        """Publish content that was created private"""
        wftool = getToolByName(p, 'portal_workflow')
        
        for folder_name in ("about", "images", "files", "contact-form", "front-page"):
            folder = getattr(p, folder_name, None)
            if folder:
                wf_state = wftool.getInfoFor(folder, 'review_state')
                if wf_state == 'private':
                    wftool.doActionFor(folder, 'publish')
    
    def hideInternalContent(self, portal):
        """If we're using two-state WF, we want certain published content to not
           show up in nav"""
        for folder_name in ("images", "files", 'Members', "contact-form"):
            folder = getattr(portal, folder_name, None)
            if folder is not None and hasattr(folder.aq_inner, "setExcludeFromNav"):
                folder.setExcludeFromNav(True)
        logger.info("Internal content suppressed from navigation")

    def constrainAddableTypes(self, p, folder_id, allowed_types, immediately_addable_types=[]):
        """
        Constrain the allowed and immediately addable types for a single folder
        """
        existing = p.objectIds()
        
        if folder_id in existing:
            f = getattr(p, folder_id)
            f.setConstrainTypesMode(1)
            f.setLocallyAllowedTypes(allowed_types)
            if immediately_addable_types:
                f.setImmediatelyAddableTypes(immediately_addable_types)
            logger.info("Addable types jiggered at /%s" % folder_id)

    def setSiteHelpHome(self, p):
        """Can't figure out how to designate home pages in GS"""

        if 'site-help' in p.objectIds():
            sh = getattr(p, 'site-help')
            sh.setLayout('folder_summary_view')
            logger.info("Site help homepage designated")

    def configureVersioning(self, portal):
        """We want to disable versioning, and set the defaults to be sane
        if it's re-enabled in the future"""
        pr = getToolByName(portal, "portal_repository")
        pp = getToolByName(portal, "portal_purgepolicy")
        v_types = pr.setVersionableContentTypes([])
        pp.maxNumberOfVersionsToKeep = 10
        logger.info("Versioning configured")

    def disableContentRules(self, portal):
        """We don't need them.  Hides the tab, too."""
        storage = getUtility(IRuleStorage)
        storage.active = False
        logger.info("Content rules disabled.")

    def createInitialSnapshot(self, portal):
        """ Make a GenericSetup snapshot of the initial portal state, so that we can
            easily see later what has been modified.
        """
        portal_setup = getToolByName(portal, 'portal_setup')
        try:
            portal_setup.createSnapshot('groundwire-template-initial')
        except:
            # yeah, sorry, bald except.
            logger.warn("Generic Setup snapshot failed!")

    def makeEmailAddressesObfuscated(self, portal):
        mimetypes_tool = getToolByName(portal, 'mimetypes_registry')
        newtype = MimeTypeItem.MimeTypeItem('HTML with obfuscated e-mail addresses',
            ('text/x-html-emailobfuscated',), ('html-emailobfuscated',), 0)
        mimetypes_tool.register(newtype)

        transform_tool = getToolByName(portal, 'portal_transforms')
        try:
            transform_tool.manage_delObjects(['html-to-emailobfuscated'])
        except: # XXX: get rid of bare except
            pass
        transform_tool.manage_addTransform('html-to-emailobfuscated',
                                           'groundwire.template.transforms.html_obfuscate_email')

        if not hasattr(transform_tool, 'emailobfuscated-to-html'):
            transform_tool.manage_addTransform('emailobfuscated-to-html', 'Products.PortalTransforms.transforms.identity')
            # Need to commit a subtransaction here, otherwise setting the
            # parameters will cause an exception when the transaction is
            # finally comitted.
            try:
                import transaction
                transaction.savepoint(optimistic=True)
            except ImportError:
                get_transaction().commit(1)

        inverse = transform_tool['emailobfuscated-to-html']
        if inverse.get_parameter_value('inputs') != ['text/x-html-emailobfuscated'] or inverse.get_parameter_value('output') != 'text/html':
            inverse.set_parameters(inputs=['text/x-html-emailobfuscated'], output='text/html')

        target = 'text/x-html-safe'
        transform = 'html-to-emailobfuscated'
        policies = transform_tool.listPolicies()
        policy_keys = [p[0] for p in policies]
        if target not in policy_keys:
            transform_tool.manage_addPolicy(target,
                                 (transform,),
                                 )
        else:
            transforms = [p[1] for p in policies if p[0] == target][0]
            if transform not in transforms:
                transforms += (transform,)
                ## no API for changing a policy :-(
                transform_tool.manage_delPolicies((target,))
                transform_tool.manage_addPolicy(target, transforms)
        logger.info("Email obfuscation transform registered.")

    def setupContactFormFolder(self, portal):
        """
        Set up the contact form.
        """
        
        types_tool = getToolByName(portal, 'portal_types')
        types_tool.constructContent(type_name='FormFolder', container=portal,
            id='contact-form')
            
        folder = portal['contact-form']
        folder.setTitle('Contact Us')
        
        if 'replyto' in folder.objectIds():
            folder['replyto'].setTitle('Email Address')
            folder['replyto'].reindexObject()
            
        types_tool.constructContent(type_name='FormSaveDataAdapter',
            container=folder, id='saved-data')
        adapter = folder['saved-data']
        adapter.setTitle('Saved Data')
        adapter.setUseColumnNames(True)
        adapter.setExtraData('dt')
        adapter.reindexObject()
        
        folder.setSubmitLabel('Send')
        logger.info("Contact form configured.")
        
    def allowEmbedTags(self, portal):
        """
        Allows embed, object, and param tags by default.
        """
        
        adapter = IFilterSchema(portal)
        nasty_tags = adapter.nasty_tags
        if 'object' in nasty_tags:
            nasty_tags.remove('object')
        if 'embed' in nasty_tags:
            nasty_tags.remove('embed')
            
        stripped_tags = adapter.stripped_tags
        if 'object' in stripped_tags:
            stripped_tags.remove('object')
        if 'param' in stripped_tags:
            stripped_tags.remove('param')
            
        custom_tags = adapter.custom_tags
        if not 'embed' in custom_tags:
            custom_tags.append('embed')
            
        adapter.nasty_tags = nasty_tags
        adapter.stripped_tags = stripped_tags
        adapter.custom_tags = custom_tags
        logger.info("Allowing embed, object, param tags in site content.")
        
    def setMailHost(self, portal):
        """
        Set the apprpriate mailhost depending on whether or not this is
        an Amazon server.
        """

        if not portal.MailHost.smtp_host:
            portal.MailHost.smtp_host = expected_mailhost()
            logger.info("Mail Host configured.")
    
def importFinalTemplateSteps(context):
    """
    The last bit of code that runs as part of this setup profile.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('groundwire-template-final.txt') is not None:
        site = context.getSite()
        generator = GroundwireTemplateGenerator()
        generator.setupContactFormFolder(site)
        generator.publishContent(site)
        generator.constrainAddableTypes(site, 'images', ["Image","Folder","Topic",], ["Image","Folder",])
        generator.constrainAddableTypes(site, 'files', ["File","Folder","Topic",], ["File","Folder",])
        generator.setSiteHelpHome(site)
        generator.configureVersioning(site)
        generator.disableContentRules(site)
        generator.hideInternalContent(site)
        generator.makeEmailAddressesObfuscated(site)
        generator.allowEmbedTags(site)
        generator.setMailHost(site)
        generator.createInitialSnapshot(site)