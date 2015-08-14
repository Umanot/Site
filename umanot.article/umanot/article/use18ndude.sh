#!/bin/bash 

PRODUCT="umanot.article"

touch locales/manual.pot

/srv/zope/umanot/plone/bin/i18ndude rebuild-pot --pot locales/$PRODUCT.pot --create $PRODUCT --merge locales/manual.pot ./

for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        /srv/zope/umanot/plone/bin/i18ndude sync --pot locales/$PRODUCT.pot $lang/LC_MESSAGES/$PRODUCT.po
    fi
done
