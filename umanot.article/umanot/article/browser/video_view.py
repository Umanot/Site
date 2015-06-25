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
        info = self.context.getInfo(scale="preview")

        if info['embed'].startswith('http'):
            video_id = info['embed'].split('v=')[-1]
            info['embed'] = "https://www.youtube.com/embed/%s" % video_id

        return info