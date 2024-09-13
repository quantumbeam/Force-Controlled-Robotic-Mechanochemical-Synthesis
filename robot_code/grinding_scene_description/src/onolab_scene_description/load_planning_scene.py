#!/usr/bin/env python3
import sys

import rospy
import roslib
import geometry_msgs.msg
from moveit_commander import PlanningSceneInterface
from moveit_commander import MoveGroupCommander
from moveit_commander import roscpp_initialize, roscpp_shutdown


class PlanningScene:
    """
    A class to manage the planning scene for a MoveIt! move group.

    Attributes:
        move_group (MoveGroupCommander): The move group to manage the planning scene for.
        planning_frame (str): The planning frame for the move group.
        scene (PlanningSceneInterface): The interface to the planning scene.
    """

    def __init__(self, move_group):
        """
        The constructor for PlanningScene class.

        Parameters:
            move_group (MoveGroupCommander): The move group to manage the planning scene for.
        """
        self.move_group = move_group
        self.planning_frame = self.move_group.get_planning_frame()
        self.scene = PlanningSceneInterface()
        self.scene.remove_world_object("")

    def init_planning_scene(self):
        """
        Initializes the planning scene by adding objects to it based on ROS parameters.
        """
        table_pos = rospy.get_param("~table_position", None)
        table_scale = rospy.get_param("~table_scale", None)
        if table_pos and table_scale:
            self._add_table(table_scale, table_pos)
        else:
            rospy.logwarn("Table parameters not provided")

        mortar_mesh_file_path = (
            roslib.packages.get_pkg_dir("grinding_scene_description")
            + "/mesh/scene_object/mortar_40mm.stl"
        )
        mortar_pos = rospy.get_param("~mortar_top_position", None)
        if mortar_pos:
            self._add_mortar(mortar_mesh_file_path, mortar_pos)
        else:
            rospy.logwarn("Mortar parameters not provided")

        pestle_jig_mesh_file_path = (
            roslib.packages.get_pkg_dir("grinding_scene_description")
            + "/mesh/scene_object/pestle_jig.stl"
        )
        pestle_jig_pos = rospy.get_param("~pestle_tip_position", None)
        if pestle_jig_pos:
            self._add_pestle_jig(pestle_jig_mesh_file_path, pestle_jig_pos)
        else:
            rospy.logwarn("Pestle jig parameters not provided")

        MiniFlex_pos = rospy.get_param("~MiniFlex_position", None)
        MiniFlex_scale = rospy.get_param("~MiniFlex_scale", None)
        if MiniFlex_pos and MiniFlex_scale:
            self._add_MiniFlex(MiniFlex_pos, MiniFlex_scale)
        else:
            rospy.logwarn("MiniFlex parameters not provided")

        MasterSizer_pos = rospy.get_param("~MasterSizer_position", None)
        MasterSizer_scale = rospy.get_param("~MasterSizer_scale", None)
        if MasterSizer_pos and MasterSizer_scale:
            self._add_MasterSizer(MasterSizer_pos, MasterSizer_scale)
        else:
            rospy.logwarn("MasterSizer parameters not provided")

    def _add_table(self, table_scale, table_pos):
        """
        Adds a table to the planning scene.

        Parameters:
            table_scale (dict): The scale of the table.
            table_pos (dict): The position of the table.
        """
        table_pose = geometry_msgs.msg.PoseStamped()
        table_pose.header.frame_id = self.planning_frame
        table_pose.pose.orientation.w = 1.0
        table_pose.pose.position.z = table_pos["z"]
        table_pose.pose.position.z -= table_scale["z"] / 2
        self.scene.add_box(
            "Table",
            table_pose,
            size=(table_scale["x"], table_scale["y"], table_scale["z"]),
        )

    def _add_mortar(self, file_path, mortar_pos):
        """
        Adds a mortar to the planning scene.

        Parameters:
            file_path (str): The path to the mesh file for the mortar.
            mortar_pos (dict): The position of the mortar.
        """
        mortar_pose = geometry_msgs.msg.PoseStamped()
        mortar_pose.header.frame_id = self.planning_frame
        mortar_pose.pose.position.x = mortar_pos["x"]
        mortar_pose.pose.position.y = mortar_pos["y"]
        mortar_pose.pose.position.z = mortar_pos["z"]
        self.scene.add_mesh("Mortar", mortar_pose, file_path)

    def _add_pestle_jig(self, file_path, pestle_jig_pos):
        """
        Adds a pestle jig to the planning scene.

        Parameters:
            file_path (str): The path to the mesh file for the pestle jig.
            pestle_jig_pos (dict): The position of the pestle jig.
        """
        pestle_jig_pose = geometry_msgs.msg.PoseStamped()
        pestle_jig_pose.header.frame_id = self.planning_frame
        pestle_jig_pose.pose.position.x = pestle_jig_pos["x"]
        pestle_jig_pose.pose.position.y = pestle_jig_pos["y"]
        pestle_jig_pose.pose.position.z = pestle_jig_pos["z"]
        self.scene.add_mesh("PestleJig", pestle_jig_pose, file_path)

    def _add_MiniFlex(self, pos, scale):
        """
        Adds a MiniFlex to the planning scene.

        Parameters:
            file_path (str): The path to the mesh file for the MiniFlex.
            miniflex_pos (dict): The position of the MiniFlex.
        """
        MiniFlex_pose = geometry_msgs.msg.PoseStamped()
        MiniFlex_pose.header.frame_id = self.planning_frame
        MiniFlex_pose.pose.orientation.w = 1.0
        MiniFlex_pose.pose.position.x = pos["x"]
        MiniFlex_pose.pose.position.y = pos["y"]
        MiniFlex_pose.pose.position.z = pos["z"] + scale["z"] / 2
        self.scene.add_box(
            "MiniFlex",
            MiniFlex_pose,
            size=(scale["x"], scale["y"], scale["z"]),
        )

    def _add_MasterSizer(self, pos, scale):
        """
        Adds a MasterSizer to the planning scene.

        Parameters:
            file_path (str): The path to the mesh file for the MasterSizer.
            mastersizer_pos (dict): The position of the MasterSizer.
        """
        MasterSizer_pose = geometry_msgs.msg.PoseStamped()
        MasterSizer_pose.header.frame_id = self.planning_frame
        MasterSizer_pose.pose.orientation.w = 1.0
        MasterSizer_pose.pose.position.x = pos["x"]
        MasterSizer_pose.pose.position.y = pos["y"]
        MasterSizer_pose.pose.position.z = pos["z"] + scale["z"] / 2
        self.scene.add_box(
            "MasterSizer",
            MasterSizer_pose,
            size=(scale["x"], scale["y"], scale["z"]),
        )


if __name__ == "__main__":
    rospy.init_node("load_planning_scene")
    move_group_name = rospy.get_param(
            "~move_group_name"
        )
    planning_scene = PlanningScene(MoveGroupCommander(move_group_name))
    planning_scene.init_planning_scene()
