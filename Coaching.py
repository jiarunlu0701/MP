import openai
import time
from playsound import playsound

openai.api_key = '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'

class Gpt4Coaching:
    def __init__(self):
        self.warning_cooldown = 10  # This is just an example, adjust to your needs
        self.feedback = ''
        self.last_warning_time = {
            'ankle': None,
            'center': None,
            'knee_intorsion': None,
            'stance': None,
            'depth': None,
            'speed': None
        }
        self.issued_warnings = {
            'ankle': False,
            'center': False,
            'knee_intorsion': False,
            'stance': False,
            'depth': False,
            'speed': False
        }

    def analyze_metrics(self, movement, metrics):
        if movement == "squat":
            self.check_knee_position(metrics)
            self.check_centered_squat(metrics)
            self.check_knee_intorsion(metrics)
            self.check_stance_width(metrics)
            self.check_squat_depth(metrics)
            self.check_squat_speed(metrics)
        else:
            return f"No analysis available for movement: {movement}"

    def check_knee_position(self, metrics):
        current_time = time.time()
        if metrics.get('ankle_angle', 0) > 20 and metrics.get('ankle_angle', 0) < 100:
            if self.last_warning_time['ankle'] is None or current_time - self.last_warning_time['ankle'] >= self.warning_cooldown:
                warning = "Warning: Your knee is passing the front toe. Try to maintain a proper form.\n"
                self.warn_user(warning, 'ankle', current_time)
                self.issued_warnings['ankle'] = False

    def check_centered_squat(self, metrics):
        check_lowest_list = metrics.get('check_lowest', [])
        if metrics.get('side') == 'centered' and check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[1]
            calculate_center = last_action[3]
            if calculate_center != 'Centered':
                if self.last_warning_time['center'] is None or action_time - self.last_warning_time['center'] >= self.warning_cooldown:
                    warning = f"Warning: You are not centered. You are {calculate_center}. Try to maintain a proper form.\n"
                    self.warn_user(warning, 'center', action_time)
                    self.issued_warnings['center'] = False

    def check_knee_intorsion(self, metrics):
        check_lowest_list = metrics.get('check_lowest', [])
        if 10 <= metrics.get('hip_angle', 0) <= 160 and check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[1]
            check_knee_intorsion = last_action[2]
            if check_knee_intorsion != "No knee intorsion detected":
                if self.last_warning_time['knee_intorsion'] is None or action_time - self.last_warning_time['knee_intorsion'] >= self.warning_cooldown:
                    warning = f"Warning: Possible knee intorsion detected. Try to maintain a proper form.\n"
                    self.warn_user(warning, 'knee_intorsion', action_time)
                    self.issued_warnings['knee_intorsion'] = False

    def check_stance_width(self, metrics):
        current_time = time.time()
        if 10 <= metrics.get('hip_angle', 0) <= 160:
            knee_distance = metrics.get('distance_between_knees', 0)
            shoulder_distance = metrics.get('calculate_shoulder_distance', 0)
            if knee_distance < shoulder_distance - 0.01:  # giving a grace of 0.01
                if self.last_warning_time['stance'] is None or current_time - self.last_warning_time['stance'] >= self.warning_cooldown:
                    warning = "Warning: Your stance is too narrow. Try to keep your knees at least as far apart as your shoulders.\n"
                    self.warn_user(warning, 'stance', current_time)

    def check_squat_depth(self, metrics):
        check_lowest_list = metrics.get('check_lowest', [])
        if check_lowest_list:
            last_action = check_lowest_list[-1]
            knee_angle = last_action[0]
            action_time = last_action[1]
            if knee_angle <=90:  # Assuming a good squat has knee_angle <= 90
                if self.last_warning_time['depth'] is None or action_time - self.last_warning_time['depth'] >= self.warning_cooldown:
                    warning = f"Warning: Your squat is shallow (knee angle: {knee_angle}). Try to reach at least a 90 degree knee angle.\n"
                    self.warn_user(warning, 'depth', action_time)
                    self.issued_warnings['depth'] = False

    def check_squat_speed(self, metrics):
        check_lowest_list = metrics.get('check_lowest', [])
        if len(check_lowest_list) >= 2:
            last_squat_time = check_lowest_list[-1][1]
            previous_squat_time = check_lowest_list[-2][1]
            squat_time_difference = last_squat_time - previous_squat_time
            if 2 < squat_time_difference < 4 and (
                    self.last_warning_time['speed'] is None or last_squat_time - self.last_warning_time['speed'] >= self.warning_cooldown):
                warning = f"Warning: You are squatting too fast. Try to take at least 2 seconds per squat.\n"
                self.warn_user(warning, 'speed', last_squat_time)
                self.issued_warnings['speed'] = False

    def warn_user(self, warning, warning_type, time):
        if not self.issued_warnings[warning_type]:
            if warning_type == 'ankle':
                playsound('ankle.wav', block=False)

            elif warning_type == 'center':
                playsound('center.wav', block=False)

            elif warning_type == 'knee_intorsion':
                playsound('knee_intorsion.wav', block=False)

            elif warning_type == 'stance':
                playsound('stance.wav', block=False)

            elif warning_type == 'depth':
                playsound('depth.wav', block=False)

            elif warning_type == 'speed':
                playsound('speed.wav', block=False)

            self.issued_warnings[warning_type] = True
        elif time - self.last_warning_time[warning_type] >= self.warning_cooldown:
            self.issued_warnings[warning_type] = False  # Reset only after cooldown period has passed
        self.last_warning_time[warning_type] = time

    def generate_chat(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=self.messages,
        )
        self.messages.append({"role": "assistant", "content": response.choices[0].message['content']})
        return response.choices[0].message['content']