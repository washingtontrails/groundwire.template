from Products.Five import BrowserView
from DateTime import DateTime

class ChangeDate(BrowserView):
    """Quicky to allow one to change a last modification date or creation date
    (though not time, atm)
    """
    
    def __call__(self, d, f):
        """We're expecting d to be a string looking like YYYY-MM-DD
            f is the mutator for the desired field
             (setModificationDate or setCreationDate)
        """
        # yeah, not even an re
        year, month, day = [int(s) for s in d.split('-')]
        date = DateTime(year, month, day)
        mutator = getattr(self.context, f)
        mutator(date)
        # for some reason, passing indexes explicitly means that 
        # (in Products.Archetypes.CatalogMultiplex.reindexObject at least)
        # reindexObject won't call notifyModified, which resets Mod Date
        self.context.reindexObject(idxs=['modified', 'created'])
        return "Changed the last %s date for %s to %s" % (
                    f.replace('set',''), self.context.absolute_url(), date)