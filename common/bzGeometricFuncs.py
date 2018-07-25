#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 14:22:58 2018

@author: bzorn
"""

import numpy as np
import shapely.geometry as geo


#Projects a point (usually baselink coordinates) to a trajectory and returns
#the distance to that trajectory as well as the index of the next point on the trajectory
#that should be used as the desired heading
#def BaseLinkToTrajectory(baselink_x, baselink_y, trajectory_xvals, trajectory_yvals):
def BaseLinkToTrajectory(baselink_x, baselink_y, trajectory_poses):
    
    [trajectory_xvals, trajectory_yvals] = PathToValues(trajectory_poses)
    
    geoBaselink = geo.Point(baselink_x, baselink_y)
    trajectory = np.array([trajectory_xvals, trajectory_yvals])
    trajectory = np.transpose(trajectory)
    geoTrajectory = geo.LineString(trajectory)
    f_dist = geoBaselink.distance(geoTrajectory) #distance between trajectory and baselink origin
    f_projLength = geoTrajectory.project(geoBaselink, normalized=True) #projection of Baselink to closest point on trajectory with distance f_dist
    
    f_distToEnd = geo.Point(geoTrajectory.coords[-1]).distance(geoBaselink)
    
    b_DirectionFound = False
    nDirection = 0
    idx = int(round(len(geoTrajectory.coords)*f_projLength))
    while(True):
#        if idx == 0: #is starting point
#            idx += 1
        if idx == len(geoTrajectory.coords)-1:
            idx -= 1
            print("at estimated end")
        else:
            if(b_DirectionFound == False):
                f_projLengthPointBefore = geoTrajectory.project(geo.Point(geoTrajectory.coords[idx]), normalized=True)
                try:
                    f_projLengthPointAfter = geoTrajectory.project(geo.Point(geoTrajectory.coords[idx+1]), normalized=True)
                except:
                    print("ERROR idx: " +str(idx))
            elif(nDirection == 1):
                f_projLengthPointAfter = geoTrajectory.project(geo.Point(geoTrajectory.coords[idx+1]), normalized=True)
            else:
                f_projLengthPointBefore = geoTrajectory.project(geo.Point(geoTrajectory.coords[idx]), normalized=True)
                
            if (f_projLengthPointBefore <= f_projLength and f_projLengthPointAfter >= f_projLength):
                idx += 1
                break;
            else:
                if (nDirection == 0):
                    if(f_projLengthPointAfter-f_projLength < f_projLengthPointBefore-f_projLength):
                        nDirection = 1
                    else:
                        nDirection = -1
                    b_DirectionFound = True
            if(nDirection == 1):
                idx += 1
                f_projLengthPointBefore = f_projLengthPointAfter
                if(idx == len(geoTrajectory.coords)-1):
                    break; #last point has been reached
            elif(nDirection == -1):
                idx -= 1
                f_projLengthPointAfter = f_projLengthPointBefore

    #so far only the distance has been calculated. the side of the trajectory the baselink is located on has to be accounted for as well
    #in 2D this can be determined by the sign of the cross product of two vectors
    #helpfull link:
    #https://math.stackexchange.com/questions/274712/calculate-on-which-side-of-a-straight-line-is-a-given-point-located
    #AB is the line segment of the polyline where the baselink point has been projected to (where B is idx, and A is idx-1)
    #AP is the line from the first point to the baselink point 
    AB = np.array((trajectory_xvals[idx]-trajectory_xvals[idx-1], trajectory_yvals[idx]-trajectory_yvals[idx-1])) 
    AP = np.array((baselink_x-trajectory_xvals[idx-1], baselink_y-trajectory_yvals[idx-1]))
    f_dist = f_dist*np.sign(np.cross(AB, AP))*-1
    
    return [f_dist, idx, f_distToEnd]


def PathToValues(trajectory_poses):
    xvals = []
    yvals = []
    for pose in trajectory_poses:
        xvals.append(pose.pose.position.x)
        yvals.append(pose.pose.position.y)
    return [xvals, yvals]
    # return [f_dist, f_heading]

#    