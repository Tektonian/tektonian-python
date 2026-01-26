from abc import ABC, abstractmethod

from .model.recording_model import RecordingModel

class IRecordingService(ABC):
    
    @abstractmethod
    def record(self, path: str, model: RecordingModel):
        ...