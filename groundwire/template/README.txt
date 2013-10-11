About the Groundwire Template

This product is the template that Groundwire uses for each new Plone site.
The general use-case it is applicable for is a small to medium site where site 
membership is a minor feature, if it's an option at all.  We're designing for
small to medium non-profit organizations, although this is not limited in any
way to that sector.

The template includes a browser view to list the largest files and images
in the site.  By default, @@large-files lists both files and images over 
100 kB.  It can also accept two query string arguments:
- size_limit: the smallest file size to return (in kB)
- portal_type: which type of object to include in the query (choices are 
  File or Image)
  
(Note: This product formerly shipped with a skin folder and setup widgets concerned
with email newsletter signup.  This has been split out into two separate products:
WhatCounts Signup and Sympa Signup.  They will eventually live in the Collective.)

In the **docs** folder that accompanying this product you will find more specific
documentation including:

- A note on unittests and how to use them.  See **customizations this product does**.

Standard stuff is in the root of the product, such as:

- Installation notes (INSTALL.txt)

- License information (LICENSE.txt)


Authors:
    **Groundwire** (http://groundwire.org):
    Jon Baldivieso (jonb@groundwire.org)

Version:
    1.0-svn (unreleased)
