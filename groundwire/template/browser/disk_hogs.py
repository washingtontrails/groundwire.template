from zope.publisher.browser import BrowserPage
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class DiskHogs(BrowserPage):

    __call__ = ViewPageTemplateFile("disk_hogs.pt")
    
    def getSizeLimit(self):
        """
        Returns the value (in kb) that files must be under to 
        escape the disk hogs list.
        """
        
        return int(self.request.get('size_limit', 100) or 100)
        
    def getTypes(self):
        """
        Returns the types (File, Image, or File and Image) to search for
        when locating disk hogs.
        """
        
        allowed_types = ['File', 'Image']
        types = []
        types_string = self.request.get('portal_type', '')
        for content_type in types_string.split(','):
            if content_type in allowed_types:
                types.append(content_type)
        if types:
            return types
        return allowed_types

    def getHogs(self):
        """
        Return a list of disk hogs in the form of dictionaries with these keys:
            - title
            - url
            - size (in kb)
            - human_size
        """
        catalog = getToolByName(self.context, "portal_catalog")
    
        results = []
        
        size_map = {
            'kb': 1,
            'mb': 1024,
            'gb': 1024 * 1024,
        }
        
        for brain in catalog.searchResults(Type=self.getTypes()):
            human_size = brain.getObjSize
            try:
                size, unit = human_size.lower().strip().split(' ')
                size = float(size)
            except ValueError:
                continue
            if size and unit in size_map.keys():
                kb_size = int(size * size_map[unit])
            
                if kb_size > self.getSizeLimit():
                    results.append({
                        'title': brain.Title,
                        'url': brain.getURL(),
                        'size': kb_size,
                        'human_size': human_size,
                    })
        results.sort(key=lambda a:a['size'], reverse=True)
        return results
