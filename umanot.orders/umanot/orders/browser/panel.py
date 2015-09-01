from plone.app.controlpanel.form import ControlPanelForm
from umanot.orders.browser.interfaces import IEcomSettings
from zope.component import getUtility

from zope.formlib import form

def ecom_settings(context):
    return getUtility(IEcomSettings, name='umanot.ecom_settings')

class EcomControlPanel(ControlPanelForm):
    form_fields = form.FormFields(IEcomSettings)

    form_name = u"ecom"
    label = u"E-Commerce"
    description = u""