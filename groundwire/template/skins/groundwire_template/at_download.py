## Script (Python) "at_download"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Download a file keeping the original uploaded filename
##

# We want things like PDFs to display inline if possible, so we
# use the index_html method for files.
if traverse_subpath == ['file'] and context.portal_type == 'File':
    request = container.REQUEST
    return context.index_html(request, request.RESPONSE)

if traverse_subpath:
    field = context.getWrappedField(traverse_subpath[0])
else:
    field = context.getPrimaryField()
return field.download(context)
