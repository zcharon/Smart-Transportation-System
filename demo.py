from detector import DetectorV5
import imutils
import cv2

TEST_VIDEO_PATH = r'video/test/test01.flv'
RESULT_VIDEO_PATH = r'video/result/result.mp4'


def main():
    name = 'demo'
    det = DetectorV5()  # 定义检测器
    cap = cv2.VideoCapture(TEST_VIDEO_PATH)
    fps = int(cap.get(5))
    print('fps:', fps)
    t = int(1000/fps)

    videoWriter = None
    id_tracker = {}
    while True:
        _, im = cap.read()
        if im is None:
            break
        
        result_im, id_tracker = det.feedCap(im, id_tracker)
        result_im = imutils.resize(result_im, height=500)
        if videoWriter is None:
            fourcc = cv2.VideoWriter_fourcc(
                'm', 'p', '4', 'v')  # opencv3.0
            videoWriter = cv2.VideoWriter(RESULT_VIDEO_PATH, fourcc, fps, (result_im.shape[1], result_im.shape[0]))

        videoWriter.write(result_im)
        cv2.imshow(name, result_im)
        cv2.waitKey(t)

        if cv2.getWindowProperty(name, cv2.WND_PROP_AUTOSIZE) < 1:
            # 点x退出
            break
    cap.release()
    videoWriter.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
