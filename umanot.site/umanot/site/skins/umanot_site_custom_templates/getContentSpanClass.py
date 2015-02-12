## Script (Python) "getContentSpanClass"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sl,sr
##title=Get content span class
##

if sr and sl:
    return 'col-md-9'
elif sr:
    return 'col-md-9'
elif sl:
    return 'col-md-12'
else:
    return 'col-md-12'