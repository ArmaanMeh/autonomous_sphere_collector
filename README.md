# autonomous_sphere_collector
# ROS 2 Autonomous Sphere Collector Robot

## 🎯 Introduction & Objective

This project documents the development and current state of a ROS 2-based mobile robot system designed for the autonomous task of locating, collecting, and delivering three spheres of varying size and color to a designated goal zone within a mapped environment.

The robot platform features a custom model, `ros2_control` hardware abstraction, and was originally intended to use the Nav2 stack for autonomous movement.

### System Goal (Original Objective)
The original objective was to autonomously complete the following sequence for all three spheres:
1. Detect the position and estimated radius of a sphere via **LiDAR-only geometric clustering**.
2. Navigate to an approach pose.
3. Collect the sphere using the L-shaped front arms.
4. Navigate to the predefined goal zone and deliver the ball.

---

## 🤖 System Implementation and Architecture

### 1. Robot Model (`URDF` / `Xacro`)
The robot is defined using a modular Xacro-based URDF, detailing the chassis, wheels, arms, and sensor placement.
* **Locomotion:** Four-wheel differential-drive configuration.
* **Manipulation:** Two L-shaped front arms.
* **Sensors:** A 2D LiDAR is mounted low.

### 2. Control Integration and Movement Limitations
Hardware abstraction is handled by `ros2_control`.

| Controller | Function | Status (Current) |
| :--- | :--- | :--- |
| **`diff_drive_controller`** | Locomotion (Wheels) | **Crashed** |
| **`joint_trajectory_controller`** | Manipulation (Arms/Scoop) | **Functional** |

**Available Movements (Current State):**
Due to the failure of the `diff_drive_controller`, the robot is stationary. The only operational movement available is control of the scoop arms.

**The Linear and Angular Velocity Issue:**
The differential drive is designed to accept commands for **Linear Velocity** (`cmd_vel.linear.x`) and **Angular Velocity** (`cmd_vel.angular.z`). However, the controller responsible for translating these commands to wheel actuation is failing. This prevents the robot from executing or maintaining any commanded linear or angular velocities, making all navigational functions impossible.

---

## ❌ Current System State and Fatal Errors

The system is currently in a critical failure state. An underlying issue is preventing core control and navigation components from initializing properly, rendering almost all advanced functionality inoperable.

### Achieved/Functional Components
| Component | Status | Detail |
| :--- | :--- | :--- |
| **Robot Model** | **Functional** | The robot model successfully spawns in the Gazebo environment. |
| **Scoop/Arm Control** | **Functional** | The `joint_trajectory_controller` for the scoop arms remains functional. The arms can be commanded to open and close. |

### Crashed/Inoperable Components (The "Everything is now Crashed" State)
| Component | Status | Detail |
| :--- | :--- | :--- |
| **Locomotion** | **Crashed** | The `diff_drive_controller` is failing to activate or communicate, meaning the robot cannot move. |
| **SLAM / Mapping** | **Crashed** | The SLAM Toolbox node fails to start. |
| **Map Server** | **Crashed** | The `nav2_map_server` fails to initialize the map, preventing costmap generation. |
| **Nav2 Navigation** | **Crashed** | The entire Nav2 stack (AMCL, planners, etc.) fails to launch due to missing critical dependencies (map, working locomotion). |
| **Autonomous Logic** | **Crashed** | The custom detection (`target_finder.py`) and collection (`pos_commander.py`) nodes fail without a running Nav2 stack or functional topics. |

---

## 🛠️ Launch Commands and Troubleshooting

### Launch Status
Currently, only the base spawn and scoop functionality are verifiable using the integrated launch file.

| Mode | Command | Status |
| :--- | :--- | :--- |
| **Full Integrated Sim** | `ros2 launch autonomous_sphere_collector_pkg gazebo_assessment.launch.py` | **Partial Success.** Robot spawns, scoop works, all other advanced functions fail. |
| **Autonomous Collector** | `ros2 launch autonomous_sphere_collector_pkg collect_balls.launch.py` | **Crashed.** Dependent on Nav2/Locomotion. |


### Key Troubleshooting Solutions (Applied, but insufficient to fix the current crash state)

We resolved several lower-level issues, but the core locomotion/Nav2 crash remains the fatal problem:

1.  **Map Server Failure Fix:**
    * **Error:** `Unknown topic '/map'` (indicating `map_server` crashed).
    * **Solution:** Added the map file installation rule to `CMakeLists.txt` to ensure map files were available in the `install/` directory at runtime. 

2.  **Controller Tolerance Violation Fix (Scoop):**
    * **Genuine Error:** The `joint_trajectory_controller` reported a `Position Error: -0.104470, Position Tolerance: 0.100000`, causing the scoop to enter a holding mode.
    * **Solution:** Increased the `position` tolerance parameter in `ros_controllers.yaml` for the `scoop_controller` to `0.15` to accommodate simulation drift.