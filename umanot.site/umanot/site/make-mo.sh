#!/bin/bash

PRODUCT="umanot.site"

msgfmt -o locales/en/LC_MESSAGES/$PRODUCT.mo locales/en/LC_MESSAGES/$PRODUCT.po
msgfmt -o locales/it/LC_MESSAGES/$PRODUCT.mo locales/it/LC_MESSAGES/$PRODUCT.po
msgfmt -o locales/$PRODUCT.mo locales/$PRODUCT.pot