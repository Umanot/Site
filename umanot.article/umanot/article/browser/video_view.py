from Products.Five import BrowserView
from zope.interface import implements, Interface

class IVideoView(Interface):
    """
    Video view interface
    """


class VideoView(BrowserView):
    """
    Video browser view
    """
    implements(IVideoView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def title(self):
        return self.context.Title()
        
    @property
    def description(self):
        return self.context.Description()
        
    @property
    def info(self):
        return self.context.getInfo(scale="preview")
        