#!/usr/bin/env python3


import rospy
import tf.transformations as tf
import time
import csv
from inputimeout import inputimeout, TimeoutOccurred

from math import pi
import copy
from scipy.spatial.transform import Rotation
import numpy as np

from grinding_motion_routines import (
    moveit_executor,
    JTC_executor,
    motion_primitive,
    marker_display,
    tf_publisher,
    motion_generator,
)

from grinding_scene_description import load_planning_scene

################### Fixed params ###################

# debug class
debug_marker = marker_display.MarkerDisplay("debug_marker")
debug_tf = tf_publisher.TFPublisher()


def display_debug_waypoints(waypoints, debug_type, tf_name="debug"):
    if debug_type == "mk":
        rospy.loginfo("Display waypoints marker")
        debug_marker.display_waypoints(waypoints, clear=True)
    elif debug_type == "tf":
        rospy.loginfo("Display waypoints tf")
        debug_tf.broadcast_tf_with_waypoints(
            waypoints, parent_link="base_link", child_link=tf_name + "_waypoints"
        )


def compute_grinding_waypoints(motion_generator, debug_type=False):
    waypoints = motion_generator.create_circular_waypoints(
        begining_position=rospy.get_param("~grinding_pos_begining"),
        end_position=rospy.get_param("~grinding_pos_end"),
        begining_radious_z=rospy.get_param("~grinding_rz_begining"),
        end_radious_z=rospy.get_param("~grinding_rz_end"),
        angle_param=rospy.get_param("~grinding_angle_param"),
        yaw_bias=rospy.get_param("~grinding_yaw_bias"),
        number_of_rotations=rospy.get_param("~grinding_number_of_rotation"),
        number_of_waypoints_per_circle=rospy.get_param(
            "~grinding_number_of_waypoints_per_circle"
        ),
        center_position=rospy.get_param("~grinding_center_pos"),
        yaw_rotation=rospy.get_param("~grinding_yaw_rotation"),
    )
    if debug_type != False:
        display_debug_waypoints(waypoints, debug_type)
    return waypoints


def compute_gathering_waypoints(motion_generator, debug_type=False):
    waypoints = motion_generator.create_circular_waypoints(
        begining_position=rospy.get_param("~gathering_pos_begining"),
        end_position=rospy.get_param("~gathering_pos_end"),
        begining_radious_z=rospy.get_param("~gathering_rz_begining"),
        end_radious_z=rospy.get_param("~gathering_rz_end"),
        angle_param=rospy.get_param("~gathering_angle_param"),
        yaw_bias=rospy.get_param("~gathering_yaw_bias"),
        number_of_rotations=rospy.get_param("~gathering_number_of_rotation"),
        number_of_waypoints_per_circle=rospy.get_param(
            "~gathering_number_of_waypoints_per_circle"
        ),
    )
    if debug_type != False:
        display_debug_waypoints(waypoints, debug_type)
    return waypoints


def exit_process(msg=""):
    if msg != "":
        rospy.loginfo(msg)
    rospy.loginfo("Exit mechano grinding")
    rospy.signal_shutdown("finish")
    rospy.spin()
    exit()


def command_to_execute(cmd):
    if cmd == "y":
        return True
    elif cmd == "mk":
        return False
    elif cmd == "tf":
        return False
    else:
        return None


def main():
    ################### init node ###################
    rospy.init_node("mechano_grinding", anonymous=True)
    log_file_dir = rospy.get_param("~log_file_dir", None)

    ################### experiment parametrs ###################
    target_experiment_time = rospy.get_param("~experiment_time")
    pouse_time_list = rospy.get_param("~pouse_time_list")
    TIMEOUT_SEC = 0.1
    current_experiment_time = 0
    ################### motion generator ###################
    mortar_top_pos = rospy.get_param("~mortar_top_position", None)
    mortar_inner_scale = rospy.get_param("~mortar_inner_scale", None)
    motion_gen = motion_generator.MotionGenerator(mortar_top_pos, mortar_inner_scale)

    ################### motion executor ###################
    move_group_name = rospy.get_param("~move_group_name", None)
    grinding_ee_link = rospy.get_param("~grinding_ee_link", None)
    gathering_ee_link = rospy.get_param("~gathering_ee_link", None)
    grinding_total_joint_diffence_for_planning = rospy.get_param(
        "~grinding_total_joint_diffence_for_planning", None
    )
    gathering_total_joint_diffence_for_planning = rospy.get_param(
        "~gathering_total_joint_diffence_for_planning", None
    )
    motion_planner_id = rospy.get_param("~motion_planner_id", None)
    planning_time = rospy.get_param("~planning_time", None)
    trial_number = rospy.get_param("~trial_number", None)
    rospy.loginfo(grinding_total_joint_diffence_for_planning)
    moveit = moveit_executor.MoveitExecutor(
        move_group_name, grinding_ee_link, motion_planner_id, planning_time
    )

    ################### init pose ###################
    init_pos = copy.deepcopy(mortar_top_pos)
    rospy.loginfo("Mortar pos: " + str(init_pos))
    init_pos["z"] += 0.05
    yaw = np.arctan2(mortar_top_pos["y"], mortar_top_pos["x"]) + pi
    euler = [pi, 0, yaw]
    r = Rotation.from_euler("xyz", euler, degrees=False)
    quat = r.as_quat()
    init_pose = list(init_pos.values()) + list(quat)
    moveit.execute_to_goal_pose(
        init_pose, ee_link=grinding_ee_link, vel_scale=0.5, acc_scale=0.5
    )
    rospy.loginfo("Goto init pose")

    ################### motion primitive ###################
    ik_solver = rospy.get_param("~ik_solver", None)
    primitive = motion_primitive.MotionPrimitive(
        init_pose=init_pose,
        ee_link=grinding_ee_link,
        robot_urdf_pkg="grinding_description",
        robot_urdf_file_name=rospy.get_param("~urdf_name"),
        joint_trajectory_controller_name=rospy.get_param(
            "~joint_trajectory_controller_name"
        ),
        move_group_name=move_group_name,
        ns=None,
        joint_names_prefix=None,
        planner_id=motion_planner_id,
        planning_time=planning_time,
        ft_topic="/wrench",
        ik_solver=ik_solver,
    )

    ################### init planning scene ###################
    planning_scene = load_planning_scene.PlanningScene(moveit.move_group)
    planning_scene.init_planning_scene()

    grinding_sec = rospy.get_param("~grinding_sec_per_rotation") * rospy.get_param(
        "~grinding_number_of_rotation"
    )
    gathering_sec = rospy.get_param("~gathering_sec_per_rotation") * rospy.get_param(
        "~gathering_number_of_rotation"
    )
    try:
        while not rospy.is_shutdown():
            motion_command = input(
                "q \t= exit.\n"
                + "scene \t= init planning scene.\n"
                + "pestle_calib \t= go to caliblation pose of pestle tip position.\n"
                + "g \t= grinding demo.\n"
                + "G \t= Gathering demo.\n"
                + "RGG \t= Repeate Grinding and Gathering motion during the experiment time.\n"
                + "\n"
            )

            if motion_command == "q":
                exit_process()

            elif motion_command == "scene":
                rospy.loginfo("Init planning scene")
                planning_scene.init_planning_scene()
            elif motion_command == "pestle_calib":
                rospy.loginfo("Go to caliblation pose of pestle tip position")
                pos = copy.deepcopy(mortar_top_pos)
                quat = init_pose[3:]
                calib_pose = list(pos.values()) + quat
                moveit.execute_cartesian_path_to_goal_pose(
                    calib_pose, ee_link=grinding_ee_link, vel_scale=0.9, acc_scale=0.9
                )

            elif motion_command == "g":
                key = input(
                    "Start grinding demo.\n execute = 'y', show waypoints marker = 'mk', show waypoints tf = 'tf', canncel = other\n"
                )
                exec = command_to_execute(key)
                if exec:
                    primitive.execute_grinding(
                        compute_grinding_waypoints(motion_gen),
                        grinding_sec=grinding_sec,
                        total_joint_limit=grinding_total_joint_diffence_for_planning,
                        trial_number=trial_number,
                        ee_link=grinding_ee_link,
                    )
                elif exec == False:
                    compute_grinding_waypoints(motion_gen, debug_type=key)
            elif motion_command == "G":
                key = input(
                    "Start circular gathering demo.\n execute = 'y', show waypoints marker = 'mk', show waypoints tf = 'tf', canncel = other\n"
                )
                exec = command_to_execute(key)
                if exec:
                    primitive.execute_gathering(
                        compute_gathering_waypoints(motion_gen),
                        gathering_sec=gathering_sec,
                        total_joint_limit=gathering_total_joint_diffence_for_planning,
                        trial_number=trial_number,
                        ee_link=gathering_ee_link,
                    )
                elif exec == False:
                    compute_gathering_waypoints(motion_gen, debug_type=key)

            elif motion_command == "RGG":
                i = 0
                motion_counts = 0
                grinding_trajectory = []
                gathering_trajectory = []

                while True:
                    try:
                        key = inputimeout(
                            prompt="If you want to finish grinding -> 'q', pose -> 'p'.\n",
                            timeout=TIMEOUT_SEC,
                        )
                        if key == "q":
                            exit_process()
                        elif key == "p":
                            input("Press Enter to continue...")

                    except TimeoutOccurred:
                        st = time.time()
                        if len(grinding_trajectory) == 0:
                            grinding_trajectory = primitive.JTC_executor.generate_joint_trajectory(
                                compute_grinding_waypoints(motion_gen),
                                total_joint_limit=grinding_total_joint_diffence_for_planning,
                                ee_link=grinding_ee_link,
                                trial_number=trial_number,
                            )
                        trajectory_success, pestle_ready_joints = (
                            primitive.execute_grinding(
                                grinding_trajectory,
                                grinding_sec=grinding_sec,
                                ee_link=grinding_ee_link,
                                execute_by_joint_trajectory=True,
                            )
                        )

                        if len(gathering_trajectory) == 0:
                            gathering_trajectory = primitive.JTC_executor.generate_joint_trajectory(
                                compute_gathering_waypoints(motion_gen),
                                total_joint_limit=gathering_total_joint_diffence_for_planning,
                                ee_link=gathering_ee_link,
                                trial_number=trial_number,
                            )
                        trajectory_success, spatula_ready_joints = (
                            primitive.execute_gathering(
                                gathering_trajectory,
                                gathering_sec=gathering_sec,
                                ee_link=gathering_ee_link,
                                execute_by_joint_trajectory=True,
                            )
                        )
                        motion_counts += 1
                        if log_file_dir != None:
                            with open(
                                log_file_dir + "pestle_and_spatula_joints_log.csv", "a"
                            ) as file:
                                writer = csv.writer(file)
                                writer.writerow(
                                    [pestle_ready_joints, spatula_ready_joints]
                                )

                    current_experiment_time += (time.time() - st) / 60
                    rospy.loginfo(
                        "Experiment time: " + str(current_experiment_time) + " min"
                    )
                    if pouse_time_list[i] < current_experiment_time:
                        i += 1
                        input(
                            "Pouse experiment on pouse settings. Press Enter to continue..."
                        )
                    if current_experiment_time > target_experiment_time:
                        rospy.loginfo("Over experiment time")
                        exit_process("Motion counts: " + str(motion_counts))

    except rospy.ROSInterruptException as err:
        exit_process(err)
    except KeyboardInterrupt as err:
        exit_process(err)


if __name__ == "__main__":
    main()
