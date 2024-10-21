"""
This entity represents the final timeline.
"""


class Timeline():
    def __init__(self, fcpxml):
        self.fcpxml = fcpxml
        self.spine = None
        self.video_assets_refs = []
        self.video_assets = {}
