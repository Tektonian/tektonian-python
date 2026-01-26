import typing
import cv2
from .recording_model import RecordingModel

class VideoModel(RecordingModel):
    """
    
    frame = 
[[[ 90 117 106]
  [ 90 117 106]
  [ 90 117 106]
  ...
  [ 83 109 102]
  [ 83 109 102]
  [ 83 109 102]]]
  frame.shape = (1080, 1920, 3)
    """

    @typing.overload
    def __init__(self, frame: cv2.typing.MatLike): ...
    @typing.overload
    def __init__(self, frame: cv2.typing.MatLike, frame_idx: None | int = None, timestamp: None | int = None, duration: None | int = None): ...
    @typing.overload
    def __init__(self, frame: cv2.typing.MatLike, frame_idx: None | int = None, timestamp: None | int = None, fps: None | int = None): ...

    def __init__(self, frame: cv2.typing.MatLike, frame_idx: None | int = None, timestamp: None | int = None, duration: None | int = None, fps: None | int = None): 
        self.frame = frame

        self.height, self.width, self.channel = self.frame.shape
        
        self.frame_idx = frame_idx

        # duration and fps will be ignored for now
    
    @property
    def id(self) -> str:
        return ''
        
    @property
    def type_name(self) -> str:
        return ''
    
    @property
    def timestamp(self) -> int:
        return 0
    
    @property
    def tick(self) -> int:
        return 0
        
    @property
    def seq_idx(self) -> int:
        return 0