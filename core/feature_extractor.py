import numpy as np


class FeatureExtractor:
    def calculate_angle(self, a, b, c):
        a = np.array(a[:3], dtype=np.float32)
        b = np.array(b[:3], dtype=np.float32)
        c = np.array(c[:3], dtype=np.float32)
        ba = a - b
        bc = c - b
        denominator = np.linalg.norm(ba) * np.linalg.norm(bc)
        if denominator == 0:
            return 0.0
        cosine = np.dot(ba, bc) / denominator
        cosine = np.clip(cosine, -1.0, 1.0)
        angle = np.arccos(cosine)
        return np.degrees(angle)

    def extract_angles(self, landmarks):
        left = {
            "shoulder": landmarks[11],
            "elbow": landmarks[13],
            "wrist": landmarks[15],
            "hip": landmarks[23],
            "knee": landmarks[25],
            "ankle": landmarks[27],
        }
        right = {
            "shoulder": landmarks[12],
            "elbow": landmarks[14],
            "wrist": landmarks[16],
            "hip": landmarks[24],
            "knee": landmarks[26],
            "ankle": landmarks[28],
        }

        left_knee = self.calculate_angle(left["hip"], left["knee"], left["ankle"])
        right_knee = self.calculate_angle(right["hip"], right["knee"], right["ankle"])
        left_hip = self.calculate_angle(left["shoulder"], left["hip"], left["knee"])
        right_hip = self.calculate_angle(right["shoulder"], right["hip"], right["knee"])
        left_elbow = self.calculate_angle(left["shoulder"], left["elbow"], left["wrist"])
        right_elbow = self.calculate_angle(right["shoulder"], right["elbow"], right["wrist"])
        left_shoulder = self.calculate_angle(left["elbow"], left["shoulder"], left["hip"])
        right_shoulder = self.calculate_angle(right["elbow"], right["shoulder"], right["hip"])

        return {
            "left_knee": left_knee,
            "right_knee": right_knee,
            "avg_knee": (left_knee + right_knee) / 2.0,
            "left_hip": left_hip,
            "right_hip": right_hip,
            "avg_hip": (left_hip + right_hip) / 2.0,
            "left_elbow": left_elbow,
            "right_elbow": right_elbow,
            "avg_elbow": (left_elbow + right_elbow) / 2.0,
            "left_shoulder": left_shoulder,
            "right_shoulder": right_shoulder,
            "avg_shoulder": (left_shoulder + right_shoulder) / 2.0,
        }
