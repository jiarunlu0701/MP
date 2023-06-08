import cv2
import mediapipe as mp
from squat import squat_PoseAnalyzer,SquatAnalyzer
from display import display
from Coaching import Gpt4Coaching
import threading

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

coach = Gpt4Coaching()

analyzer = squat_PoseAnalyzer(tolerance=0.01)
squat_analyzer = SquatAnalyzer(analyzer)

starting_y = 650
line_spacing = 30
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.90, min_tracking_confidence=0.90) as pose_estimator:
    try:  # start of try block
        while cap.isOpened():
            success, image = cap.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose_estimator.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks is not None:
                landmarks = results.pose_landmarks.landmark
            else:
                landmarks = []

            if landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), circle_radius=2, thickness=2),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2)
                )

                squat_metrics = squat_analyzer.analyze(landmarks)
                check_lowest_list = squat_metrics.get('check_lowest', [])
                squat_count = len(check_lowest_list)
                draw=display(image)
                draw.draw_axis()

                for idx, (metric_name, metric_value) in enumerate(squat_metrics.items()):
                    draw.display_content(metric_name, metric_value, 10, starting_y + idx * line_spacing)

                draw.display_content('Squat count', squat_count, 30,150)

                # Here we call the analyze_metrics method from the coach object
                warning_thread = threading.Thread(target=coach.analyze_metrics, args=("squat", squat_metrics,))
                warning_thread.start()

            cv2.imshow('Pose estimation', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:  # start of finally block
        # This block will be executed no matter how the try block is exited
        coach.stop()  # correctly stop the warning manager
        cap.release()
        cv2.destroyAllWindows()
