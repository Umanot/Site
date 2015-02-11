## Script (Python) "print_request"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
lines = list()

for k, v in context.REQUEST.form.items():
    line = '%s -> %s' % (k, v)
    lines.append(line)

return '\n'.join(lines)
