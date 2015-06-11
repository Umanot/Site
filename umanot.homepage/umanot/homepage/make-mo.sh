#!/bin/bash

PRODUCT="umanot.homepage"

msgfmt -o locales/de/LC_MESSAGES/$PRODUCT.mo locales/de/LC_MESSAGES/$PRODUCT.po
msgfmt -o locales/en/LC_MESSAGES/$PRODUCT.mo locales/en/LC_MESSAGES/$PRODUCT.po
msgfmt -o locales/it/LC_MESSAGES/$PRODUCT.mo locales/it/LC_MESSAGES/$PRODUCT.po
msgfmt -o locales/$PRODUCT.mo locales/$PRODUCT.pot