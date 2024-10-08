import numpy as np

# Load the pose data from two npy files
user_pose = np.load('serve_ouput2_3d.npy')  # Your pose data (Ruud)
pro_pose = np.load('serve_ouput1_3d.npy')  # pro player's pose data for comparison (Sinner)

frame_rate = 60

# [user, pro] time stamp
key_events = [{
    'ball_release': 4.2,
    'trophy_position': 5.3,
    'racquet_low_point': 6.2,
    'impact': 6.65
},{
    'ball_release': 5.25,
    'trophy_position': 7.3,
    'racquet_low_point': 8.05,
    'impact': 8.6
}]

# Convert timestamps to frames
for k in key_events:
    for event in k:
        k[event] = int(k[event] * frame_rate)

# COCO keypoints indices
RIGHT_ELBOW = 3
LEFT_ELBOW = 6
RIGHT_KNEE = 9
LEFT_KNEE = 12
RIGHT_FOOT = 10
LEFT_FOOT = 13

# Function to compare joints and output relative feedback
def compare_joints(user_joint, pro_joint, event_name, joint_name):
    # Compare relative positions (in this example, using z-axis as the height)
    height_diff = user_joint[2] - pro_joint[2]
    
    if height_diff < -0.05:
        print(f"Your {joint_name} during {event_name} is too low compared to pro's.")
    elif height_diff > 0.05:
        print(f"Your {joint_name} during {event_name} is too high compared to pro's.")
    else:
        print(f"Your {joint_name} during {event_name} is well aligned with pro's.")

# Function to analyze key events and compare player vs. pro
def analyze_serve(user_pose, pro_pose, key_events):
    event = 'trophy_position'
    user_frame = key_events[0][event]
    pro_frame = key_events[1][event]

    print(f"\nAnalyzing {event.replace('_', ' ').capitalize()}:")
    
    # Compare elbows
    compare_joints(user_pose[user_frame, RIGHT_ELBOW], pro_pose[pro_frame, RIGHT_ELBOW], event, 'right elbow')
    compare_joints(user_pose[user_frame, LEFT_ELBOW], pro_pose[pro_frame, LEFT_ELBOW], event, 'left elbow')
    
    # Compare knees
    compare_joints(user_pose[user_frame, RIGHT_KNEE], pro_pose[pro_frame, RIGHT_KNEE], event, 'right knee')
    compare_joints(user_pose[user_frame, LEFT_KNEE], pro_pose[pro_frame, LEFT_KNEE], event, 'left knee')

    # Compare feet (relative to each other)
    user_feet_dist = np.linalg.norm(user_pose[user_frame, RIGHT_FOOT][:2] - user_pose[user_frame, LEFT_FOOT][:2])
    pro_feet_dist = np.linalg.norm(pro_pose[pro_frame, RIGHT_FOOT][:2] - pro_pose[pro_frame, LEFT_FOOT][:2])
    
    if user_feet_dist > pro_feet_dist + 0.1:
        print(f"Your feet are further apart during {event.replace('_', ' ').capitalize()} compared to pro's.")
    elif user_feet_dist < pro_feet_dist - 0.1:
        print(f"Your feet are closer together during {event.replace('_', ' ').capitalize()} compared to pro's.")

# Run the analysis
analyze_serve(user_pose, pro_pose, key_events)

