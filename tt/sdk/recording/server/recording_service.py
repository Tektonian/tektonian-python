import tempfile
import os.path 
import pathlib

import duckdb
import cv2

from ..common.recording_service import IRecordingService
from ..common.model.video_model import VideoModel



class RecordingService(IRecordingService):
    
    def __init__(self):
        super().__init__()

        
        self.duckdb = duckdb.connect(":memory:")
        # fd, tmp_path = tempfile.mkstemp(".mp4", "tmp", '.')
        # self.video_fd = fd
        # self.video_tmp_path = tmp_path
        self.video_writer: cv2.VideoWriter | None = None
        self.record_set = set()
        
        
    def record(self, path, model):
        path = os.path.normpath(path)
        name = pathlib.Path(path).name
        ext = pathlib.Path(path).suffix

        

        if isinstance(model, VideoModel):
            if ext != '.mp4':
                print("warn: Video extention not matched")
            if self.video_writer is None:
                print(model.frame.shape)
                h, w, _ = model.frame.shape
                print(h)
                fps = cv2.CAP_PROP_FRAME_COUNT
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(name, fourcc, fps, (w, h))
            self.__record_video_model(model=model)
            


    def __record_video_model(self, model: VideoModel):
        print(self.video_writer.isOpened())
        # if not self.video_writer.isOpened():
            # print("error: cannot write video")

        self.video_writer.write(model.frame)




        
