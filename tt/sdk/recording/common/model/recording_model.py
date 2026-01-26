from abc import ABC, abstractmethod

class RecordingModel(ABC):

    @property
    @abstractmethod
    def id(self) -> str:
        ...
        
    @property
    @abstractmethod
    def type_name(self) -> str:
        ...
    
    @property
    @abstractmethod
    def timestamp(self) -> int:
        ...
    
    @property
    @abstractmethod
    def tick(self) -> int:
        ...
        
    @property
    @abstractmethod
    def seq_idx(self) -> int:
        ...