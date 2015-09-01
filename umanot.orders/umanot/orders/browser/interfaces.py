from zope.interface import Interface
from zope import schema


class IEcomSettings(Interface):
    """Ecom Settings.
    """

    cambio = schema.Float(
        title = u"Cambioeuro/dollaro",
        required = True,
        default = 1.11933
    )

    round_net = schema.Bool(
        title = u"Arrotonda il netto",
        default = True
    )

    threshold = schema.Int(
        title = u"Arrotonda a",
        required = True,
        default = 5
    )