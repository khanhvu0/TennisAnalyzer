from flask import Flask, request, jsonify
import numpy as np
import io
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# user_pose = np.load('serve_ouput2_3d.npy')  # Your pose data (Ruud)
# pro_pose = np.load('serve_ouput1_3d.npy')  # pro player's pose data for comparison (Sinner)

# frame_rate = 60

# # [user, pro] time stamps
# key_events = [{
#     'ball release': 4.2,
#     'trophy position': 5.3,
#     'racquet low point': 6.2,
#     'impact': 6.65
# },{
#     'ball release': 5.25,
#     'trophy position': 7.3,
#     'racquet low point': 8.05,
#     'impact': 8.6
# }]

# # Convert timestamps to frames
# for k in key_events:
#     for event in k:
#         k[event] = int(k[event] * frame_rate)

# COCO keypoints indices
NOSE = 0
NECK = 1
RIGHT_SHOULDER = 2
LEFT_SHOULDER = 5
RIGHT_ELBOW = 3
LEFT_ELBOW = 6
RIGHT_WRIST = 4
LEFT_WRIST = 7
RIGHT_HIP = 8  
LEFT_HIP = 11
RIGHT_KNEE = 9
LEFT_KNEE = 12
RIGHT_FOOT = 10
LEFT_FOOT = 13


# Compare two joints relative to each other in 3D space
def compare_joints_relative_to_each_other(user_joint1, user_joint2, pro_joint1, pro_joint2, event_name, joint1_name, joint2_name):
    # Calculate 3D distance between the two joints for both user and pro
    user_distance = np.linalg.norm(user_joint1 - user_joint2)
    pro_distance = np.linalg.norm(pro_joint1 - pro_joint2)
    
    distance_diff = user_distance - pro_distance
    if distance_diff > 0.1:
        print(f"Your {joint1_name} and {joint2_name} are too far apart during {event_name} (distance difference: {distance_diff:.2f}).")
    elif distance_diff < -0.1:
        print(f"Your {joint1_name} and {joint2_name} are too close together during {event_name} (distance difference: {distance_diff:.2f}).")
    else:
        print(f"Your {joint1_name} and {joint2_name} are well aligned with pro's during {event_name} (distance difference: {distance_diff:.2f}).")


# Compare a joint's height relative to another joint
def compare_height_of_joint_relative_to_joint(user_joint1, user_joint2, pro_joint1, pro_joint2, event_name, joint1_name, joint2_name):
    # Compare relative heights (z-axis only)
    user_relative_height = user_joint1[2] - user_joint2[2]
    pro_relative_height = pro_joint1[2] - pro_joint2[2]
    height_diff = user_relative_height - pro_relative_height
    
    if height_diff > 0.05:
        print(f"Your {joint1_name} is too high relative to your {joint2_name} during {event_name} (height difference: {height_diff:.2f}).")
    elif height_diff < -0.05:
        print(f"Your {joint1_name} is too low relative to your {joint2_name} during {event_name} (height difference: {height_diff:.2f}).")
    else:
        print(f"Your {joint1_name} is well aligned with your {joint2_name} during {event_name} (height difference: {height_diff:.2f}).")


def compare_joint_angle(user_joint1, user_joint2, user_joint3, pro_joint1, pro_joint2, pro_joint3, 
                        event_name, angle_name):
    def calculate_angle(joint1, joint2, joint3):
        # Calculate angle between three joints in 3d space in the X-Y plane
        vector1 = joint1[[0, 1]] - joint2[[0, 1]] 
        vector2 = joint3[[0, 1]] - joint2[[0, 1]]

        dot_product = np.dot(vector1, vector2)
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)
        
        angle = np.arccos(dot_product / (magnitude1 * magnitude2))
        return np.degrees(angle)
    

    user_angle = calculate_angle(user_joint1, user_joint2, user_joint3)
    pro_angle = calculate_angle(pro_joint1, pro_joint2, pro_joint3)
    
    angle_diff = user_angle - pro_angle
    if angle_diff > 5:
        print(f"Your {angle_name} is too extended during {event_name} (angle difference: {angle_diff:.2f}°).")
    elif angle_diff < -5:
        print(f"Your {angle_name} is too bent during {event_name} (angle difference: {angle_diff:.2f}°).")
    else:
        print(f"Your {angle_name} is well aligned with the pro's during {event_name} (angle difference: {angle_diff:.2f}°).")


# Analyze key events and compare player vs. pro
def analyze_serve(user_pose, pro_pose, key_events, event):
    user_frame = key_events[0][event]
    pro_frame = key_events[1][event]

    print(f"\nAnalyzing {event}:")

    compare_height_of_joint_relative_to_joint(user_pose[user_frame, RIGHT_ELBOW], user_pose[user_frame, RIGHT_HIP],
                                    pro_pose[pro_frame, RIGHT_ELBOW], pro_pose[pro_frame, RIGHT_HIP],
                                    event, 'right elbow', 'right hip')

    compare_joints_relative_to_each_other(user_pose[user_frame, RIGHT_KNEE], user_pose[user_frame, LEFT_KNEE],
                                          pro_pose[pro_frame, RIGHT_KNEE], pro_pose[pro_frame, LEFT_KNEE],
                                          event, 'right knee', 'left knee')

    compare_joints_relative_to_each_other(user_pose[user_frame, RIGHT_FOOT], user_pose[user_frame, LEFT_FOOT],
                                          pro_pose[pro_frame, RIGHT_FOOT], pro_pose[pro_frame, LEFT_FOOT],
                                          event, 'right foot', 'left foot')

    compare_joint_angle(user_pose[user_frame, RIGHT_HIP], user_pose[user_frame, RIGHT_KNEE], user_pose[user_frame, RIGHT_FOOT],
                        pro_pose[pro_frame, RIGHT_HIP], pro_pose[pro_frame, RIGHT_KNEE], pro_pose[pro_frame, RIGHT_FOOT],
                        event, 'right knee bend')

    compare_joint_angle(user_pose[user_frame, LEFT_HIP], user_pose[user_frame, LEFT_KNEE], user_pose[user_frame, LEFT_FOOT],
                        pro_pose[pro_frame, LEFT_HIP], pro_pose[pro_frame, LEFT_KNEE], pro_pose[pro_frame, LEFT_FOOT],
                        event, 'left knee bend')

    compare_joint_angle(user_pose[user_frame, RIGHT_SHOULDER], user_pose[user_frame, RIGHT_ELBOW], user_pose[user_frame, RIGHT_WRIST],
                        pro_pose[pro_frame, RIGHT_SHOULDER], pro_pose[pro_frame, RIGHT_ELBOW], pro_pose[pro_frame, RIGHT_WRIST],
                        event, 'right arm bend')

    compare_joint_angle(user_pose[user_frame, LEFT_SHOULDER], user_pose[user_frame, LEFT_ELBOW], user_pose[user_frame, LEFT_WRIST],
                        pro_pose[pro_frame, LEFT_SHOULDER], pro_pose[pro_frame, LEFT_ELBOW], pro_pose[pro_frame, LEFT_WRIST],
                        event, 'left arm bend')


# API endpoint
@app.route('/analyze', methods=['POST'])
def analyze_serve():
    user_pose_file = request.files['userPose']
    pro_pose_file = request.files['proPose']
    key_events = request.form['keyEvents']
    
    key_events = eval(key_events)

    frame_rate = 60
    for k in key_events:
        for event in k:
            k[event] = int(k[event] * frame_rate)
    
    user_pose = np.load(io.BytesIO(user_pose_file.read()))
    pro_pose = np.load(io.BytesIO(pro_pose_file.read()))

    analysis_results = analyze_serve(user_pose, pro_pose, key_events, "impact")
    
    return jsonify(analysis_results)


app.run(debug=True, host='0.0.0.0', port=5000)