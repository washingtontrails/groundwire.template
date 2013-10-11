import unittest
from groundwire.template.tests.base import FunctionalTestCase

class TestContentCreation(FunctionalTestCase):
    """Ensure that content is being created and configged properly."""

    def afterSetUp(self):
        pass
        
    def testSiteReindexed(self):
        """last call in create_base_content is portal.portal_catalog.clearFindAndRebuild()"""
        self.loginAsPortalOwner() # login as manager if all content is created private
        search = self.portal.portal_catalog.searchResults(id='about')[0]
        # catalog brain's title should be the same as the object's title
        self.failUnless(search.getObject().Title()==search.Title)
        self.failUnless(search.Title=='About Us')

    def testBasicFoldersCreated(self):
        """We add folders for images and files at the root of the site as well 
        as a private "Site Help" folder"""
        # XXX need to test if site-help is private
        portal_objects = self.portal.objectIds()

        self.failUnless('images' in portal_objects)
        self.failUnless('files' in portal_objects)
        self.failUnless('site-help' in portal_objects)

    def testPrivateContentReallyPrivate(self):
        """Site Help folder, privacy policy should be private"""
        wftool = self.portal.portal_workflow
        site_help = getattr(self.portal, 'site-help')
        privacy = self.portal.about.privacy
        self.failUnless(wftool.getInfoFor(site_help,'review_state', None)=='private')
        self.failUnless(wftool.getInfoFor(privacy,'review_state', None)=='private')

    def testPublishedContentReallyPublished(self):
        """If default initial WF state is private, we need
        to make some of our new content published"""
        wftool = self.portal.portal_workflow
        for folder_name in ("about", "images", "files"):
            folder = getattr(self.portal, folder_name)
            wf_state = wftool.getInfoFor(folder, 'review_state')
            self.failUnless(wf_state=='published',
                            "%s isn't published, it's %s" %(folder_name, wf_state))

    def testInternalContentHiddenFromNav(self):
        """If we're using two-state WF, we want certain published content to not
           show up in nav"""
        for folder_name in ("images", "files", 'Members'):
            folder = getattr(self.portal, folder_name)
            nav_setting = folder.exclude_from_nav()
            self.failUnless(nav_setting is True,
                            "%s not excluded from nav (%s)" % (folder_name, nav_setting))

    def testEventsSetup(self):
        """OOTB, Plone creates a smart folder for events. we want it nested in a folder"""
        # check to make sure that it has an events archive
        self.failUnless(hasattr(self.portal.events.aggregator, 'previous'))
        # check to make sure that the events SF is the def page for the folder
        self.failUnless(self.portal.events.getDefaultPage() == 'aggregator')

    def testNewsSetup(self):
        """OOTB, Plone creates a smart folder for news. we want it nested in a folder"""
        # we're using Plone's OOTB Collection within a Folder -- no need to test here anymore
        pass
        # # check to make sure that the news SF is the def page for the folder
        # self.failUnless(self.portal.news.getDefaultPage() == 'news')

    def testAddableImageTypes(self):
        """ Test whether we're making use of Plone's clever preferred and restricted addable types UI """
        self.images = getattr(self.portal,'images')
        self.assertEqual(self.images.getConstrainTypesMode(), 1)
        self.assertEqual(("Image","Folder","Topic"), tuple(self.images.getLocallyAllowedTypes()))
        self.assertEqual(("Image","Folder"), tuple(self.images.getImmediatelyAddableTypes()))

    def testAddableFileTypes(self):
        """ Test whether we're making use of Plone's clever preferred and restricted addable types UI """
        self.files = getattr(self.portal,'files')
        self.assertEqual(self.files.getConstrainTypesMode(), 1)
        self.assertEqual(("File","Folder","Topic"), tuple(self.files.getLocallyAllowedTypes()))
        self.assertEqual(("File","Folder"), tuple(self.files.getImmediatelyAddableTypes()))

    def testAddableNewsTypes(self):
        """ Test whether we're making use of Plone's clever preferred and restricted addable types UI """
        self.news = getattr(self.portal,'news')
        self.assertEqual(self.news.getConstrainTypesMode(), 1)
        # Plone stole our idea!  We'll use they're defaults, which mean just news items are addable ATM
        # self.assertEqual(("News Item","Folder","Topic"), tuple(self.news.getLocallyAllowedTypes()))
        # self.assertEqual(("News Item","Folder"), tuple(self.news.getImmediatelyAddableTypes()))
        self.assertEqual(("News Item",), tuple(self.news.getLocallyAllowedTypes()))

    def testAddableEventTypes(self):
        """ Test whether we're making use of Plone's clever preferred and restricted addable types UI """
        self.events = getattr(self.portal,'events')
        self.assertEqual(self.events.getConstrainTypesMode(), 1)
        # Plone stole our idea!  We'll use they're defaults, which mean just events are addable ATM
        # self.assertEqual(("Event","Folder","Topic"), tuple(self.events.getLocallyAllowedTypes()))
        # self.assertEqual(("Event","Folder"), tuple(self.events.getImmediatelyAddableTypes()))
        self.assertEqual(("Event",), tuple(self.events.getLocallyAllowedTypes()))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentCreation))
    return suite
