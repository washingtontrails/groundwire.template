#!/usr/bin/python
"""Looks through the current directory and creates metadata files for all perceived image files
that don't already have one.  (The metadata files set cache settings for the image to be used in
tandem with Cache Fu to optimize the site using this skin.) """

import os

metadata_template = "[default]\ncache=HTTPCache"
img_extensions = ('bmp', 'gif', 'ico', 'jpg', 'jpeg', 'png', 'tiff',)

dir_listing = os.listdir(os.getcwd())
img_files = [name for name in dir_listing if name.split('.')[-1] in img_extensions]

if not img_files:
    print """\
No image files were found -- be sure that you're calling \
this script within the context of a skin directory"""

for img_file in img_files:
    metaname = "%s.metadata" % img_file
    if metaname not in dir_listing:
        metafile = open(metaname, 'w')
        metafile.write(metadata_template)
        metafile.close()
        print "Created metadata file for %s" % img_file