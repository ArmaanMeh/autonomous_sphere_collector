import sys
import termios
import tty
import select
from turtle import position
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
from math import pi
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

# --- Configuration Constants ---
# TOPICS ARE CORRECT - Verified by ros2 topic list
CMD_VEL_TOPIC = 'cmd_vel'
SCOOP_CMD_TOPIC = '/scoop_controller/joint_trajectory' 

# Define the acceptable position limits for the scoop joint (e.g., in radians)
# NOTE: These positions are the target values sent to the controller.
SCOOP_POSITIONS = {
    '1': 0.0,       # Scoop UP (Rest Position)
    '2': 0.5,       # Scoop LEVEL (Ground Contact/Initial Scoop)
    '3': -0.785,    # Scoop DOWN (Tilted back for maximum carry, approx -45 degrees)
}

# --- Keyboard Input Setup ---

msg = """
Control Autonomous Sphere Collector!
----------------------------------
Moving (Differential Drive):
      w
    a s d
      x

q/z : increase/decrease max speeds by 10%
w/x : linear movement (forward/back)
a/d : angular movement (left/right)
s   : force stop

Scoop Controls (Joint Position):
1 : Scoop UP (Carry/Rest Position)
2 : Scoop LEVEL (Ground Contact/Initial Scoop)
3 : Scoop DOWN (Tilted back for maximum carry)

CTRL-C to quit
"""

moveBindings = {
    'w': (1, 0),    # Linear Forward
    'a': (0, 1),    # Angular Left
    'd': (0, -1),   # Angular Right
    'x': (-1, 0),   # Linear Backward
}

speedBindings = {
    'q': (1.1, 1.1),  # Increase speed by 10%
    'z': (0.9, 0.9),  # Decrease speed by 10%
}

# --- Utility Functions ---

def getKey(settings):
    """Reads a single keypress from stdin without blocking indefinitely."""
    # Set stdin to raw mode
    tty.setraw(sys.stdin.fileno())
    # Non-blocking check for input
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    # Restore terminal settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(speed, turn):
    return "currently:\tLinear Speed: %s\tAngular Speed: %s" % (speed, turn)

# --- ROS 2 Node Class ---

class TeleopNode(Node):
    def __init__(self):
        super().__init__('sphere_collector_teleop')
        
        # 1. Command Velocity Publisher (Uses standard Twist message)
        self.cmd_vel_pub = self.create_publisher(
            Twist,         # CHANGE 3: Twist message type
            CMD_VEL_TOPIC, 
            10
        )
        
        # 2. Scoop Command Publisher (Uses simple Float64 message)
        self.scoop_pub = self.create_publisher(
            JointTrajectory,       # CHANGE 4: Float64 message type
            SCOOP_CMD_TOPIC, 
            10
        )

        # Initial movement state
        self.speed = 0.5  # Max linear speed (m/s)
        self.turn = 1.0   # Max angular speed (rad/s)
        self.x = 0.0      # Current linear direction (1, 0, or -1)
        self.th = 0.0     # Current angular direction (1, 0, or -1)
        self.status = 0   # Status counter for printing Vels message

    def publish_twist(self):
        """Creates and publishes a Twist message for vehicle movement."""
        # CHANGE 5: Use Twist message
        twist_msg = Twist() 

        # Calculate final velocities
        twist_msg.linear.x = self.x * self.speed
        twist_msg.angular.z = self.th * self.turn
        
        self.cmd_vel_pub.publish(twist_msg)

    def publish_scoop_command(self, position):
        """Publishes a single position command to the scoop joint."""
        traj_msg = JointTrajectory()
    # IMPORTANT: This name must EXACTLY match the joint name in your XACRO/URDF
        traj_msg.joint_names = ['scoop_pivot_joint'] 

        point = JointTrajectoryPoint()
        point.positions = [position]
    # Set a duration for the movement (e.g., 1 second)
        point.time_from_start = Duration(sec=1, nanosec=0) 

        traj_msg.points.append(point)
        self.scoop_pub.publish(traj_msg)
        
        sys.stdout.write(f"\rScoop target position set to: {position:.3f} rad\n")
        sys.stdout.flush()

def main(args=None):
    # Get current terminal settings to restore them later
    settings = termios.tcgetattr(sys.stdin)
    
    rclpy.init(args=args)
    node = TeleopNode()
    
    print(msg)
    print(vels(node.speed, node.turn))
    
    try:
        while True:
            # Read non-blocking keypress
            key = getKey(settings)
            
            # --- Movement Commands (w, a, d, x, s) ---
            if key in moveBindings.keys():
                node.x = float(moveBindings[key][0])
                node.th = float(moveBindings[key][1])
                
            # --- Speed Adjustments (q, z) ---
            elif key in speedBindings.keys():
                node.speed *= speedBindings[key][0]
                node.turn *= speedBindings[key][1]
                
                print(vels(node.speed, node.turn))
                node.status = (node.status + 1) % 15
                if (node.status == 14):
                    print(msg)
                    
            elif key == 's':
                node.x = 0.0
                node.th = 0.0
                print("\rSTOPPING                 ")

            # --- Scoop Commands (1, 2, 3) ---
            elif key in SCOOP_POSITIONS.keys():
                target_pos = SCOOP_POSITIONS[key]
                node.publish_scoop_command(target_pos)

            # --- Exit Command (Ctrl-C) ---
            elif key == '\x03': 
                break
                
            # Publish movement commands on every loop iteration
            node.publish_twist()

    except Exception as e:
        print(f"An exception occurred: {e}")

    finally:
        # Final cleanup and stop command
        print("\nExiting Teleop. Sending stop command...")
        
        # Send a zero-velocity Twist to ensure robot stops
        stop_msg = Twist()
        node.cmd_vel_pub.publish(stop_msg)

        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()