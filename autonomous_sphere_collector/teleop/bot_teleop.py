#!/usr/bin/env python3
import sys
import termios
import tty
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

# --- Configuration Constants ---
CMD_VEL_TOPIC = 'cmd_vel'
SCOOP_CMD_TOPIC = 'scoop_cmd_pos' # Matches the bridge and Gazebo plugin topic

# Target positions (in radians)
SCOOP_POSITIONS = {
    '1': 0.0,       # Scoop UP (Rest Position)
    '2': 0.5,       # Scoop LEVEL (Ground Contact/Initial Scoop)
    '3': -0.785,    # Scoop DOWN (Tilted back for maximum carry)
}

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
    'w': (1.0, 0.0),
    'a': (0.0, 1.0),
    'd': (0.0, -1.0),
    'x': (-1.0, 0.0),
}

speedBindings = {
    'q': (1.1, 1.1),  
    'z': (0.9, 0.9),  
}

def getKey(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(speed, turn):
    return f"currently:\tLinear Speed: {speed:.2f}\tAngular Speed: {turn:.2f}"

class TeleopNode(Node):
    def __init__(self):
        super().__init__('sphere_collector_teleop')
        
        # 1. Command Velocity Publisher
        self.cmd_vel_pub = self.create_publisher(Twist, CMD_VEL_TOPIC, 10)
        
        # 2. Scoop Position Publisher (Simple Float64 for Gazebo Control)
        self.scoop_pub = self.create_publisher(Float64, SCOOP_CMD_TOPIC, 10)

        self.speed = 0.5  
        self.turn = 1.0   
        self.x = 0.0      
        self.th = 0.0     

    def publish_twist(self):
        twist_msg = Twist() 
        twist_msg.linear.x = self.x * self.speed
        twist_msg.angular.z = self.th * self.turn
        self.cmd_vel_pub.publish(twist_msg)

    def publish_scoop_command(self, position):
        """Publishes the target position as a simple Float64 scalar value."""
        scoop_msg = Float64()
        scoop_msg.data = position
        self.scoop_pub.publish(scoop_msg)
        
        sys.stdout.write(f"\rScoop target position set to: {position:.3f} rad\n")
        sys.stdout.flush()

def main(args=None):
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init(args=args)
    node = TeleopNode()
    
    print(msg)
    print(vels(node.speed, node.turn))
    
    try:
        while True:
            key = getKey(settings)
            
            if key in moveBindings.keys():
                node.x = moveBindings[key][0]
                node.th = moveBindings[key][1]
                
            elif key in speedBindings.keys():
                node.speed *= speedBindings[key][0]
                node.turn *= speedBindings[key][1]
                print(vels(node.speed, node.turn))
                    
            elif key == 's':
                node.x = 0.0
                node.th = 0.0
                sys.stdout.write("\rSTOPPING                 \n")
                sys.stdout.flush()

            elif key in SCOOP_POSITIONS.keys():
                target_pos = SCOOP_POSITIONS[key]
                node.publish_scoop_command(target_pos)

            elif key == '\x03': 
                break
                
            node.publish_twist()

    except Exception as e:
        print(f"An exception occurred: {e}")

    finally:
        print("\nExiting Teleop. Sending stop command...")
        stop_msg = Twist()
        node.cmd_vel_pub.publish(stop_msg)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()