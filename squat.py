import numpy as np
import mediapipe as mp
from util import Util
import time


class squat_PoseAnalyzer:
    def __init__(self, tolerance):
        self.tolerance = tolerance
        self.mp_pose = mp.solutions.pose
        self.knee_angles = []
        self.squat_ratios = []
        self.knee_distance = []
        self.back_up_flag = True
        self.smooth_util = Util()

    def calculate_hip_line_direction(self, landmarks):
        # Get the positions of the left and right hip
        left_hip = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].z])
        right_hip = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                              landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y,
                              landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].z])

        # Calculate the direction of the line from the left hip to the right hip
        hip_line_direction = right_hip - left_hip

        # Normalize the direction vector
        hip_line_direction /= np.linalg.norm(hip_line_direction)

        return hip_line_direction

    def calculate_hip_angle(self, landmarks):
        # Calculate the direction of the line formed by the left and right hip
        hip_direction = self.calculate_hip_line_direction(landmarks)

        # We consider the line perpendicular to the image plane, i.e., the line of sight from the camera
        camera_line = np.array([0, 0, 1])  # Adjust this according to your coordinate system

        # Calculate the angle between the hip line and the camera line
        cos_angle = np.dot(hip_direction, camera_line) / (np.linalg.norm(hip_direction) * np.linalg.norm(camera_line))

        # Calculate the angle in degrees
        angle = np.degrees(np.arccos(cos_angle))

        # Subtract the angle from 180 to get 0 degrees when facing the camera
        angle = 180 - angle

        # Take the absolute value to avoid negative angles
        angle = abs(angle)

        return angle

    def knee_calculate_angle(self, landmarks, side):
        sides = {'left': [self.mp_pose.PoseLandmark.LEFT_HIP.value,
                          self.mp_pose.PoseLandmark.LEFT_KNEE.value,
                          self.mp_pose.PoseLandmark.LEFT_ANKLE.value],
                 'right': [self.mp_pose.PoseLandmark.RIGHT_HIP.value,
                           self.mp_pose.PoseLandmark.RIGHT_KNEE.value,
                           self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]}

        if side in sides:
            hip = np.array([landmarks[sides[side][0]].x, landmarks[sides[side][0]].y])
            knee = np.array([landmarks[sides[side][1]].x, landmarks[sides[side][1]].y])
            ankle = np.array([landmarks[sides[side][2]].x, landmarks[sides[side][2]].y])

            radians = np.arctan2(ankle[1] - knee[1], ankle[0] - knee[0]) - np.arctan2(hip[1] - knee[1],
                                                                                      hip[0] - knee[0])
            angle = np.abs(radians * 180.0 / np.pi)

            if angle > 180.0:
                angle = 360 - angle

            # Subtract the angle from 180 to "invert" it
            angle = 180 - angle

            return angle
        else:
            raise ValueError("Invalid side. Choose 'left' or 'right'.")

    def ankle_calculate_angle(self, landmarks, side):
        sides = {'left': [self.mp_pose.PoseLandmark.LEFT_KNEE.value,
                          self.mp_pose.PoseLandmark.LEFT_ANKLE.value,
                          np.array([0, landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y])],
                 'right': [self.mp_pose.PoseLandmark.RIGHT_KNEE.value,
                           self.mp_pose.PoseLandmark.RIGHT_ANKLE.value,
                           np.array([0, landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y])]
                 }

        if side in sides:
            b = np.array([landmarks[sides[side][0]].x, landmarks[sides[side][0]].y])
            a = np.array([landmarks[sides[side][1]].x, landmarks[sides[side][1]].y])
            c = sides[side][2]
            ba = a - b  # vector from b to a
            bc = c - b  # vector from b to c

            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)

            # Convert to degrees
            angle = np.degrees(angle)

            # Adjust so that 90 degrees becomes 0
            angle -= 90

            # Make sure angle is not negative
            if angle < 0:
                angle = 0

            return angle

        else:
            raise ValueError("Invalid side. Choose 'left' or 'right'.")

    def distance_between_knees(self, landmarks):
        left_knee = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                              landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y])

        right_knee = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y])

        return round(np.linalg.norm(left_knee - right_knee), 2)

    def calculate_shoulder_distance(self, landmarks):
        # Get the coordinates of the left and right shoulder
        left_shoulder = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])

        right_shoulder = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])

        # Calculate the Euclidean distance
        distance = round(np.linalg.norm(left_shoulder - right_shoulder),2)

        return distance

    def check_knee_intorsion(self, landmarks):
        left_knee = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                              landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y])

        right_knee = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y])

        left_ankle = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                               landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y])

        right_ankle = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y])

        knee_distance = np.linalg.norm(left_knee - right_knee)
        ankle_distance = np.linalg.norm(left_ankle - right_ankle)

        if knee_distance < ankle_distance:
            return "Possible knee intorsion detected"
        else:
            return "No knee intorsion detected"

    def calculate_center(self, landmarks):
        left_knee = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                              landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y])

        right_knee = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y])

        left_hip = np.array([landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y])

        right_hip = np.array([landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                              landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y])

        hip_center = (left_hip + right_hip) / 2

        # Calculate the center point between the knees
        knee_center = (left_knee[0] + right_knee[0]) / 2

        # Check if the hip_center's x-coordinate is near to the knee's center
        if abs(knee_center - hip_center[0]) < self.tolerance:  # tolerance can be set depending on your needs
            return "Centered"
        elif knee_center > hip_center[0]:
            return "Leaning to the right"  # Hip is to the left of the center, so person is leaning to the right
        else:
            return "Leaning to the left"  # Hip is to the right of the center, so person is leaning to the left

    def check_lowest(self, landmarks, side):
        knee_angle = int(self.knee_calculate_angle(landmarks, side))
        self.knee_angles.append(knee_angle)
        turning_points = self.smooth_util.find_turning_points(self.knee_angles, window=15)

        if turning_points and 20 < knee_angle < 160:
            index = len(self.knee_angles) - 1  # Start at the current knee angle
            while index > 0:  # Continue as long as there is a previous knee angle
                previous_angle = self.knee_angles[index - 1]
                if knee_angle <= previous_angle:
                    # Update the current knee angle with the previous one
                    knee_angle = previous_angle
                    index -= 1  # Move to the previous knee angle
                else:
                    break  # Exit the loop once we find an angle smaller than the current knee angle

            current_time = time.time()

            check_knee_intorsion = self.check_knee_intorsion(landmarks)
            calculate_center = self.calculate_center(landmarks)

            # Only append new squat record if back_up_flag is True
            if self.back_up_flag:
                self.squat_ratios.append((knee_angle, current_time, check_knee_intorsion, calculate_center))
                self.back_up_flag = False  # Reset the flag as the person is squatting again

        # Update back_up_flag to True when the person is standing up
        if knee_angle <= 20:
            self.back_up_flag = True

        return self.squat_ratios

class SquatAnalyzer:
    def __init__(self, pose_analyzer):
        self.pose_analyzer = squat_PoseAnalyzer(tolerance=0.01)

    def analyze(self, landmarks):
        hip_angle = self.pose_analyzer.calculate_hip_angle(landmarks)
        if 15 <= hip_angle <= 80 or hip_angle > 165:
            self.side = 'left'
            knee_angle = self.pose_analyzer.knee_calculate_angle(landmarks, 'left')
            ankle_angle = self.pose_analyzer.ankle_calculate_angle(landmarks, 'left')
            check_lowest = self.pose_analyzer.check_lowest(landmarks, 'left')
        elif 165 >= hip_angle >= 100 or hip_angle < 15:
            self.side = 'right'
            knee_angle = self.pose_analyzer.knee_calculate_angle(landmarks, 'right')
            ankle_angle = self.pose_analyzer.ankle_calculate_angle(landmarks, 'right')
            check_lowest = self.pose_analyzer.check_lowest(landmarks, 'right')
        else:
            self.side = 'center'
            knee_angle = self.pose_analyzer.knee_calculate_angle(landmarks, 'left')
            ankle_angle = self.pose_analyzer.ankle_calculate_angle(landmarks, 'left')
            check_lowest = self.pose_analyzer.check_lowest(landmarks, 'left')

        distance_between_knees = self.pose_analyzer.distance_between_knees(landmarks)
        calculate_shoulder_distance = self.pose_analyzer.calculate_shoulder_distance(landmarks)
        return {
            'hip_angle': hip_angle,
            'side': self.side,
            'knee_angle': knee_angle,
            'ankle_angle': ankle_angle,
            'distance_between_knees': distance_between_knees,
            'calculate_shoulder_distance': calculate_shoulder_distance,
            'check_lowest': check_lowest
        }





