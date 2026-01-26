import typing
import os

from ....sdk.recording.common.model.video_model import VideoModel


from ....sdk.recording.server.recording_service import RecordingService
class TektonianService:

    def __init__(self, recording_service: RecordingService):
        self.API_KEY = os.environ.get("TEKTONIAN_API_KEY")

        self.recording_service = recording_service
        
    def init(self, project_name: str):
        ...
    
    def log(self, path: str, data: VideoModel):
        self.recording_service.record(path, data)