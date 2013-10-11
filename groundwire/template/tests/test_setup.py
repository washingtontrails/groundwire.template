import unittest
from zope.component import getUtility
from plone.browserlayer import utils as browserlayer_utils

from groundwire.template.interfaces import IGroundwireTemplateLayer
from groundwire.template.tests.base import FunctionalTestCase

class TestInstallation(FunctionalTestCase):
    """Ensure product is properly installed"""

    def afterSetUp(self):
        self.css        = self.portal.portal_css
        self.skins      = self.portal.portal_skins
        self.properties = self.portal.portal_properties

    def testSkinLayersInstalled(self):
        """We install two skin layers"""
        self.failUnless('groundwire_template' in self.skins.objectIds())

    def testCSSisRegistered(self):
        """We register our own style sheet: groundwire_template.css"""
        self.failUnless('groundwire_template.css' in self.css.getResourceIds())
    
    def testOurStylesheetIsAbovePloneCustom(self):
        """ploneCustom.css should take precedence over groundwire_template.css"""
        self.failUnless('ploneCustom.css' in self.css.getResourceIds())
        self.failUnless('groundwire_template.css' in self.css.getResourceIds())
        self.failUnless(self.css.getResourceIds()[-1] == 'ploneCustom.css')

    def testAutomaticInitialSnapshotCreated(self):
        """We create an initial GS snapshot to allow future comparisons"""
        self.failUnless('groundwire-template-initial' in \
            map(lambda a: a['id'], self.portal.portal_setup.listSnapshotInfo()))
        
class TestCustomizationPolicy(FunctionalTestCase):
    """Ensure that all the little tweaks have been made.
       
       This is basically just tracking down groundwire.template/profiles/default 
       profile, making sure each thing is done."""

    def afterSetUp(self):
        self.css        = self.portal.portal_css
        self.skins      = self.portal.portal_skins
        self.workflow   = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.site_props = self.properties.site_properties
        self.nav_props  = self.properties.navtree_properties

    def testManagersCanHideContent(self):
        """
        plone_workflow and folder_workflow stipulate that only owner can make something private and show.  
        Now managers can too.
        """
        transitions = ('hide','show')

        for transition in transitions:
            self.failUnless('Manager' in self.workflow.plone_workflow.transitions[transition].getGuard().roles)
            self.failUnless('Manager' in self.workflow.folder_workflow.transitions[transition].getGuard().roles)
    
    def testSitePropsTweaked(self):
        """We want a bunch of minor adjustments to the site_properties:
           time formatting (long and short), number of calendar years to show,
           bylines not shown to anon viewers, and disable folder sections (that is, auto-creation of tabs upon folder creation)"""
        sp = self.site_props
        self.failUnless(sp.localTimeFormat == '%b %d, %Y')
        self.failUnless(sp.localLongTimeFormat == '%b %d, %Y %I:%M %p')
        self.failUnless(sp.calendar_future_years_available == 3)
        self.failUnless(not sp.allowAnonymousViewAbout)
        self.failUnless(sp.disable_folder_sections == 1)
        self.failUnless(sp.icon_visibility=='authenticated',
                        "Icon visibility set to '%s'; we want it to be 'authenticated'." % sp.icon_visibility)
    
    def testNavTreeShowsLimitedCTs(self):
        """We only want a subset of content types shown in the nav tree:
           ('Folder', 'Large Plone Folder', 'Topics', 'Document')"""
        # XXX We really want to show the inverse of this; that everything else
        # is blacklisted (same thing as above)
        self.failUnless('Folder' not in self.nav_props.metaTypesNotToList)
        self.failUnless('Large Plone Folder' not in self.nav_props.metaTypesNotToList)
        self.failUnless('Topics' not in self.nav_props.metaTypesNotToList)
        self.failUnless('Document' not in self.nav_props.metaTypesNotToList)
    
    def testNavTreePropertyTweaks(self):
        """We're making a few minor adjustments to the nav tree properties:
           - don't show site root
           - filtering on WF state
           - only show published
         """
        self.failUnless(self.nav_props.enable_wf_state_filtering==1)
        self.failUnless(self.nav_props.wf_states_to_show == ('published',))
        self.failUnless(not self.nav_props.includeTop)
    
    def testMemberFoldersNotCreated(self):
        """We don't want member folders to be created"""
        self.failUnless(not self.portal.portal_membership.memberareaCreationFlag)

    def testJoiningSiteRestricted(self):
        """We only want managers to be able to add new site members"""
        #portal.manage_permission('Add portal member', ['Manager',], acquire=0)
        portal = self.portal
        mtool = self.portal.portal_membership
        checkPermission = mtool.checkPermission
        
        # should be allowed as Manager
        self.setRoles(['Manager'])
        self.failUnless(checkPermission('Add portal member', portal))
        # should NOT be allowed as Member
        self.setRoles(['Member'])
        self.failIf(checkPermission('Add portal member', portal))
        # should NOT be allowed as anonymous
        self.logout()
        self.failIf(checkPermission('Add portal member', portal))
    
    def testSiteActionsHidden(self):
        """We're hiding all the portal tabs by default"""
        at=self.portal.portal_actions
        actions=at._cloneActions()
        for a in actions:
            if a.category=='portal_tabs':
                self.failUnless(not a.visible)
        
    def testActionsAddedToPersonalBar(self):
        at = self.portal.portal_actions
        for a in ('site_help', 'plone_help', 'groundwire_support'):
            self.failUnless(at['user'][a].visible)

    def testMailHostAddress(self):
        """This is now shipping blank, and we always want it to be
        127.0.0.1 (for our HSR server we need that instead of localhost)"""
        self.failUnless(self.portal.MailHost.smtp_host == '127.0.0.1')        
    
    def testCalendarSettings(self):
        """We want our calendars to start on Sunday."""
        # oddly, Monday is 0; Sunday is 6.
        firstweekday = self.portal.portal_calendar.firstweekday
        self.failUnless(firstweekday == 6,
                        "Calendar's first day is %s; we want it to be 6" % firstweekday)
    
    def testContentRulesDisabled(self):
        """The Content Rules are not relevant for the majority of our sites.  Disabling them
        hides the 'Rules' tab on folderish content"""
        from plone.contentrules.engine.interfaces import IRuleStorage
        storage = getUtility(IRuleStorage)
        self.failUnless(storage.active is False,
                        "Content rules 'global enabled' is set to: %s; we want it to be False" % storage.active)

    def testSitemapXMLExposed(self):
        """We want to expose sitemap.xml.gz for better SEO"""
        
        from Products.CMFCore.interfaces import IPropertiesTool
        ptool = getUtility(IPropertiesTool)
        enable_sitemap = ptool.site_properties.enable_sitemap
        self.failUnless(enable_sitemap is True,
                        "We want the sitemap.xml.gz setting to be True; it's now: %s" % enable_sitemap)

    def testVersioningDisabled(self):
        """We want to disable versioning for all content types"""
        pr = self.portal.portal_repository
        v_types = pr.getVersionableContentTypes()
        self.failUnless(v_types in ((), None, []),
                        "We wanted versionable CTs to be an empty set.  They are: %s" % v_types)
        
    def testVersionsLimited(self):
        """Even though we want versioning disabled by default, we'll set the max number of
        versions so that if they're enabled in the future they don't fill up the site"""
        max_v = self.portal.portal_purgepolicy.maxNumberOfVersionsToKeep
        self.failUnless(max_v == 10,
                        "maxNumberOfVersionsToKeep is %s; we want it to be 10." % max_v)

    def testBrowserLayerInstalled(self):
        """We install plone.browserlayer and register our layer so that we can use our viewlets selectively"""
        self.failUnless(IGroundwireTemplateLayer in browserlayer_utils.registered_layers())
        
    def testEmailAddressesObfuscated(self):
        """ We register a transformation policy so that anything being rendered as text/x-html-safe
            gets filtered to obfuscate e-mail addresses using Plone's standard spamProtect.py script.
        """
        
        # make sure policy is installed
        policies = self.portal.portal_transforms.listPolicies()
        transforms = [p[1] for p in policies if p[0] == 'text/x-html-safe'][0]
        self.failUnless('html-to-emailobfuscated' in transforms)
        
        # create some content with e-mail addresses, and make sure it is obfuscated
        self.folder.invokeFactory('Document', 'obfuscate_me')
        doc = self.folder.obfuscate_me
        doc.setText(
            """<a href="mailto:test@example.com">test@example.com</a>""", 
            mimetype='text/html'
        )
        self.assertEqual(
            doc.getText(), 
            """<a href="&#0109;ailto&#0058;test&#0064;example.com">test&#0064;example.com</a>"""
        )
                
    def testPrelaunchStatusScreen(self):
        # make sure control panel action is installed
        configlets = [a.getId() for a in self.portal.portal_controlpanel.listActions()]
        self.failUnless('groundwire_template_prelaunch' in configlets)
        
        # make sure we can traverse to the status screen
        self.setRoles(['Manager',])
        self.failUnless(self.portal.restrictedTraverse('@@prelaunch-status'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInstallation))
    suite.addTest(unittest.makeSuite(TestCustomizationPolicy))
    return suite
