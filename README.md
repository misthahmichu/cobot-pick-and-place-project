# Cobot Pick and Place Project

## Project Overview
This project demonstrates a complete cobot pick-and-place system developed in both simulation and hardware.  
The system uses a robotic arm with a vacuum gripper to detect, pick, and place colored objects into the correct target area.  

The project was first developed and tested in a software simulation environment using **ROS2**, **Gazebo**, and **MoveIt2**, and later implemented in a real hardware setup using a **NeoFlux cobot**, **vacuum gripper**, **camera-based detection**, and a custom control interface.

The main goal of this project is to combine:
- Robot motion planning
- Object detection using camera
- Vacuum-based gripping
- Pick-and-place automation
- Simulation to hardware workflow

---

## Project Concept
The project is based on an automated pick-and-place workflow where the cobot identifies an object, moves to the object position, activates suction using a vacuum gripper, lifts the object safely, and places it into the correct container or target location.

### Working Flow
1. Camera detects the object / colored cube
2. System identifies the target object
3. Cobot moves to the pick position
4. Vacuum gripper activates suction
5. Object is picked
6. Cobot lifts the object
7. Cobot moves to the target placement area
8. Vacuum gripper releases the object
9. Process repeats for the next object

This project shows how a robotic system can perform automated material handling using both software simulation and real hardware implementation.

---

## Features
- Cobot pick-and-place operation
- Simulation in ROS2 + Gazebo
- MoveIt2 motion planning
- Vacuum gripper integration
- Camera-based object detection concept
- Colored object sorting
- Hardware implementation with real cobot
- Custom control interface for hardware testing
- Pick, lift, and place sequence execution

---

## Software / Simulation Technologies Used
- ROS2 Humble
- Gazebo
- MoveIt2
- Python
- URDF / Xacro
- VS Code
- Ubuntu (VM environment)

---

## Hardware Components Used
- NeoFlux Cobot / Robotic Arm
- Vacuum Gripper
- DC Vacuum Pump
- Relay Module
- Arduino
- Suction Cup
- Air Tube / Pneumatic Tube
- Camera
- Power Supply
- Laptop / PC for control interface

---

## Simulation Workflow
The simulation part was developed to test the robot behavior before hardware implementation.

### Simulation Steps
1. Create robot and workspace in Gazebo
2. Spawn boxes / objects in the simulation scene
3. Add target placement zones
4. Define pick positions and place positions
5. Use MoveIt2 for motion planning
6. Simulate vacuum gripper logic
7. Test robot movement
8. Verify pick-and-place sequence
9. Improve the environment and debug issues

The simulation helped in understanding:
- Robot model loading
- Workspace setup
- Pick and place positions
- Motion planning
- Camera placement concept
- System debugging before hardware testing

---

## Hardware Implementation
After simulation testing, the project was implemented on real hardware.

### Hardware Workflow
1. Camera detects the object
2. Control interface receives the feed
3. Operator / system selects the object
4. Cobot moves to the object position
5. Vacuum gripper picks the object
6. Object is transferred to the correct container
7. System can repeat the operation for multiple objects

The hardware implementation demonstrates the practical use of:
- Real cobot motion
- Real suction-based gripping
- Real object handling
- Camera-assisted object identification
- Manual / semi-automatic control through UI

---

## My Contribution
- Worked on project setup and implementation
- Developed and tested simulation environment
- Worked on robot movement logic
- Added vacuum gripper integration
- Created pick, lift, and place sequence
- Worked on camera-based object detection concept
- Tested simulation outputs
- Participated in hardware implementation and testing
- Worked on control interface and object handling workflow

---

## Project Files Included
- Python source files
- Simulation scripts
- Box spawning scripts
- Camera detection scripts
- Vacuum gripper control scripts
- Pick-and-place logic files
- Simulation screenshots
- Hardware implementation photos

---

## Important Python Files
- `add_scene_objects.py`
- `spawn_box.py`
- `red_box.py`
- `spawn_camera.py`
- `vacuum_gripper.py`
- `wrist_camera_detector.py`
- `wrist_pick_place.py`
- `setup.py`

---

## Simulation Screenshots

### Final Simulation Output
![Final Simulation](images:software/final_simulation.png)

### Gazebo Empty World Issue
![Gazebo Empty World](images:software/empty_gazebo_issue.png)

### RViz / Robot Model View
![RViz Robot Model](images:software/rviz_robot_fixed.png)

### Pick and Place Position Code
![Position Code](images:software/pssition_code.png)

### Camera Setup - View 1
![Camera Setup 1](images:software/camera_setup_1.png)

### Camera Setup - View 2
![Camera Setup 2](images:software/camera_setup_2.png)

---

## Hardware Photos

### Hardware Control Interface with Camera Detection
![Hardware Camera Detection](images/hardware/camera_detect.jpeg)

### Hardware Pick and Place Setup
![Hardware Pick and Place](images/hardware/pick_object.jpeg)

---

## Challenges Faced
- Gazebo showing empty world
- Robot model not fully visible in simulation
- Partial robot loading issues
- Camera placement and detection alignment
- Pick and place position tuning
- Vacuum gripper integration issues
- Hardware and software synchronization
- Testing object handling accuracy

---

## Future Improvements
- Fully automatic color detection and sorting
- Better object detection accuracy
- Improved UI for real-time control
- Better suction control and safety
- More robust simulation environment
- Expand to multiple object classes
- Improve real-time hardware performance

---

## Download / Installation Links

### ROS2 Humble
https://docs.ros.org/en/humble/Installation.html

### Gazebo
https://gazebosim.org/docs

### MoveIt2
https://moveit.picknik.ai/main/doc/tutorials/getting_started/getting_started.html

### VS Code
https://code.visualstudio.com/

### Ubuntu
https://ubuntu.com/download/desktop

### Python
https://www.python.org/downloads/

---

## Project Type
This was a team project completed with my classmate.
