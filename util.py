import numpy as np

class Util:
    def __init__(self):
        self.seen_true = False

    def smooth_list(self,lst,window_size):
        smoothed_list = []

        for i in range(len(lst)):
            start_index = max(0, i - window_size + 1)
            end_index = i + 1
            window = lst[start_index:end_index]
            average = int(np.mean(window))
            smoothed_list.append(average)

        return smoothed_list

    def find_turning_points(self, list_values, window):
        if len(list_values) > 2 * window:
            check_list = list_values[-window:]
            lower_bound = check_list[:window // 2]
            upper_bound = check_list[window // 2:]

            lower_bound_gradient = np.gradient(lower_bound)
            upper_bound_gradient = np.gradient(upper_bound)

            if np.mean(lower_bound_gradient[-window:]) > 0 and np.mean(upper_bound_gradient[-window:]) < 0:
                if self.seen_true == False:
                   self.seen_true = True
                   return True
            else:
               self.seen_true = False




