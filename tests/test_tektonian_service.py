import cv2


from tt import tt, VideoModel
def test_tektonian_service():
    cap = cv2.VideoCapture(0)
    
    tt.init("test")
    

    ret, frame = cap.read()
    for i in range(10):
        ret, frame = cap.read()
        tt.log("output.mp4", VideoModel(frame=frame))
    