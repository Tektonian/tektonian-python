from .tt.common.tektonian_service import TektonianService

from .recording.server.recording_service import RecordingService


from .recording.common.model.recording_model import RecordingModel
from .recording.common.model.video_model import VideoModel

tt = TektonianService(RecordingService())
