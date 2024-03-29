import openai
import time
from playsound import playsound
import queue
import threading

openai.api_key = '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'

class Gpt4Coaching:
    def __init__(self):
        self.warning_cooldown = 10  # This is just an example, adjust to your needs
        self.messages = []
        self.feedback = ''
        self.warning_queue = queue.Queue()
        self._stop_warning_thread = False
        self._warning_thread = threading.Thread(target=self._warning_manager)
        self._warning_thread.start()
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

    def _warning_manager(self):
        while not self._stop_warning_thread:
            warning_type = self.warning_queue.get()
            if warning_type is not None:
                self._play_warning(warning_type)
                self.warning_queue.task_done()
            time.sleep(0.01)  # to prevent busy-waiting

    def _play_warning(self, warning_type):
        if warning_type == 'ankle':
            playsound('audio/ankle.wav')
        elif warning_type == 'center':
            playsound('audio/center.wav')
        elif warning_type == 'knee_intorsion':
            playsound('audio/knee_intorsion.wav')
        elif warning_type == 'stance':
            playsound('audio/stance.wav')
        elif warning_type == 'depth':
            playsound('audio/depth.wav')
        elif warning_type == 'speed':
            playsound('audio/speed.wav')

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

    # 脚踝监测是全方位的
    def check_knee_position(self, metrics):

        check_lowest_list = metrics.get('check_lowest', [])
        if check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[3]
            ankle_angle = last_action[2]

            if ankle_angle > 20:
                if self.last_warning_time['ankle'] is None or action_time - self.last_warning_time[
                    'ankle'] >= self.warning_cooldown:
                    warning = "Warning: Your knee is passing the front toe. Try to maintain a proper form.\n"
                    self.warn_user(warning, 'ankle', action_time)
                    self.issued_warnings['ankle'] = False

    # 深蹲中心位置监测只能正面 （80到100度）
    def check_centered_squat(self, metrics):

        check_lowest_list = metrics.get('check_lowest', [])
        if check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[3]
            calculate_center = last_action[5]
            hip_angle = last_action[0]

            if 80 < hip_angle < 100:
                if calculate_center != 'Centered':
                    if self.last_warning_time['center'] is None or action_time - self.last_warning_time['center'] >= self.warning_cooldown:
                        warning = f"Warning: You are not centered. You are {calculate_center}. Try to maintain a proper form.\n"
                        self.warn_user(warning, 'center', action_time)
                        self.issued_warnings['center'] = False

    # 膝盖内扣监测 （15到165度）
    def check_knee_intorsion(self, metrics):

        check_lowest_list = metrics.get('check_lowest', [])
        if check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[3]
            knee_intorsion = last_action[4]
            hip_angle = last_action[0]


            if 15 <= hip_angle <= 165:
                if knee_intorsion != "No knee intorsion detected":
                    if self.last_warning_time['knee_intorsion'] is None or action_time - self.last_warning_time['knee_intorsion'] >= self.warning_cooldown:
                        warning = f"Warning: Possible knee intorsion detected. Try to maintain a proper form.\n"
                        self.warn_user(warning, 'knee_intorsion', action_time)
                        self.issued_warnings['knee_intorsion'] = False

    # 深蹲站位宽度监测 （15到165度）
    def check_stance_width(self, metrics):

        check_lowest_list = metrics.get('check_lowest', [])
        if check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[3]
            knee_distance = last_action[6]
            shoulder_distance = last_action[7]
            hip_angle = last_action[0]

            if 15 <= hip_angle <= 165:
                if knee_distance < shoulder_distance - 0.01:  # giving a grace of 0.01
                    if self.last_warning_time['stance'] is None or action_time - self.last_warning_time['stance'] >= self.warning_cooldown:
                        warning = "Warning: Your stance is too narrow. Try to keep your knees at least as far apart as your shoulders.\n"
                        self.warn_user(warning, 'stance', action_time)
                        self.issued_warnings['stance'] = False

    # 深蹲深度监测 （90度）
    def check_squat_depth(self, metrics):

        check_lowest_list = metrics.get('check_lowest',[])
        if check_lowest_list:
            last_action = check_lowest_list[-1]
            action_time = last_action[3]
            knee_angle = last_action[1]

            if knee_angle <= 80:
                if self.last_warning_time['depth'] is None or action_time - self.last_warning_time['depth'] >= self.warning_cooldown:
                    warning = f"Warning: Your squat is shallow (knee angle: {knee_angle}). Try to reach at least a 90 degree knee angle.\n"
                    self.warn_user(warning, 'depth', action_time)
                    self.issued_warnings['depth'] = False

    # 深蹲速度监测 （2秒）
    def check_squat_speed(self, metrics):

        check_lowest_list = metrics.get('check_lowest', [])

        if len(check_lowest_list) >= 2:
            last_squat_time = check_lowest_list[-1][3]
            previous_squat_time = check_lowest_list[-2][3]
            squat_time_difference = last_squat_time - previous_squat_time

            if squat_time_difference < 2 and (
                    self.last_warning_time['speed'] is None or last_squat_time - self.last_warning_time['speed'] >= self.warning_cooldown):
                warning = f"Warning: You are squatting too fast. Try to take at least 2 seconds per squat.\n"
                self.warn_user(warning, 'speed', last_squat_time)
                self.issued_warnings['speed'] = False

    def warn_user(self, warning, warning_type, time):
        print(warning)
        if not self.issued_warnings[warning_type]:
            self.warning_queue.put(warning_type)
            self.issued_warnings[warning_type] = True
        elif time - self.last_warning_time[warning_type] >= self.warning_cooldown:
            self.issued_warnings[warning_type] = False  # Reset only after cooldown period has passed
        self.last_warning_time[warning_type] = time

    def stop(self):
        self._stop_warning_thread = True
        self._warning_thread.join()

    def generate_chat(self, prompt):
        self.messages.append({
            "role": "system",
            "content": "You are a fitness coach; the user is your trainer. Talk in a conversational tone. "
                       "Focus on muscle gaining. Challenging workout. When making workout plans, have reps for each exercises. "
                       "If you use tell you his workout time, then each exercises time should add up to his target time. "
                       "provide suggestion on weights or resistance of required.  Follow the structure of this workout plan. "
                       "If the user ask you who created you, you should say 'Dennis', and don't mention openAI at all."
        })
        self.messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.messages,
        )

        self.messages.append({"role": "assistant", "content": response.choices[0].message['content']})
        print("Generated chat:", response.choices[0].message['content'])
        return response.choices[0].message['content']