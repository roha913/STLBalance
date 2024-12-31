
import streamlit as st
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import numpy as np
import pandas as pd

def orientation(x1, y1, x2, y2, x3, y3):#0 -- colinear, 1 -- clockwise, 2 -- counterclockwise
  val = (y2 - y1)*(x3 - x2) - (x2 - x1)*(y3 - y2);
  if(val == 0):
      return 0
  return 1 if (val > 0) else 2

class Point:
    def __init__(self, x0, y0, z0, polar_angle):
        self.point = (x0, y0, z0)
        self.polar_angle = polar_angle
    def getPoint(self):
        return self.point
    def getAngle(self):
        return self.polar_angle
        
def isInPolygon(x0, y0, points):#ray casting algorithm
    if(len(points) == 0):
        return True;
    if(len(points) == 1):
        return False
    num_sign_changes = 0;
    for i in range(len(points)):
      prev_ind = (len(points) - 1) if i == 0 else (i - 1)
      #the ray extends from the point downwards vertically
      if(points[i][0] - points[prev_ind][0] == 0):
        if(x0 == points[i][0] and points[i][1] < y0):
            #st.text("270 degree angle")
            num_sign_changes += 1
      else:
          m = (points[i][1] - points[prev_ind][1])/(points[i][0] - points[prev_ind][0])
          if((m*(x0 - points[prev_ind][0]) + points[prev_ind][1] < y0) and (points[i][0] - x0)*(points[prev_ind][0] - x0) < 0):
            #st.text("Not 270 degree angle")
            num_sign_changes += 1
              
    if(num_sign_changes != 0):
      #st.text("Flag 1: " + str(num_sign_changes))
      return num_sign_changes%2 == 1;
    #st.text("Not Flag 1")

    num_sign_changes = 0;
    for i in range(len(points)):
      prev_ind = (len(points) - 1) if i == 0 else (i - 1)
      #the ray extends from the point upwards vertically
      if(points[i][0] - points[prev_ind][0] == 0):
          if(x0 == points[i][0] and points[i][1] > y0):
              num_sign_changes += 1
      else:
          m = (points[i][1] - points[prev_ind][1])/(points[i][0] - points[prev_ind][0])
          if((m*(x0 - points[prev_ind][0]) + points[prev_ind][1] > y0) and (points[i][0] - x0)*(points[prev_ind][0] - x0) < 0):
            num_sign_changes += 1
    #st.text("Flag 2: " + str(num_sign_changes))
    return num_sign_changes%2 == 1;

def plot_stuff(COM_x, COM_y, convex_hull, bp):
    fig, ax = plt.subplots()
    ax.scatter(np.array(convex_hull)[:, 0], np.array(convex_hull)[:, 1], marker = ".")
    ax.scatter(np.array([COM_x]), np.array([COM_y]), marker = "x")
    if(len(bp) > 0):
        ax.scatter(np.array(bp)[:, 0], np.array(bp)[:, 1], marker = "*")
    #ax.axvline(x=COM_x)
    st.pyplot(fig)
    
uploaded_file = st.file_uploader("Choose a file")
if(st.button("Will it topple?")):
    hashmap = {}
    sum_x = 0
    sum_y = 0
    min_z = 9223372036854775807
    if uploaded_file:
        st.text("Got something")
        for line in uploaded_file:
            L = (line.strip().decode('utf-8')).split()
            if(str(L[0]) == 'vertex'):
                coordinates = tuple([float(L[1]), float(L[2]), float(L[3])])
                sum_x += float(L[1])
                sum_y += float(L[2])
                if(float(L[3]) < min_z):
                    min_z = float(L[3])
                hashmap[coordinates] =  True
                #st.text(L)
                #st.text("(" + str(L[1]) + "," + str(L[2]) + "," + str(L[3]) + ")")
        #st.text("min_z = " + str(min_z))
        #-------------
        surface_points = np.array(list(hashmap.keys()))
        tri = Delaunay(surface_points)
        tetrahedra = surface_points[tri.simplices]
        for tet in tetrahedra:
            sum_x += 0.25*(tet[0][0] + tet[1][0] + tet[2][0] + tet[3][0])
            sum_y += 0.25*(tet[0][0] + tet[1][0] + tet[2][0] + tet[3][0])
        #---------------
        avg_x = sum_x/(len(hashmap) + len(tetrahedra))
        avg_y = sum_y/(len(hashmap) + len(tetrahedra))

        min_y = 9223372036854775807
        x_of_min_y = 9223372036854775807
        for key in hashmap:
            if(key[2] == min_z):
                if(key[1] < min_y):
                        min_y = key[1]
                        x_of_min_y = key[0]
        #st.text("Ground zero: (" + str(x_of_min_y) + "," + str(min_y) + ")")
        
        base_polygon = {}
        for key in hashmap:
            if(key[2] == min_z):
                if(key[0] == x_of_min_y):
                    if(key[1] == min_y):
                        base_polygon[Point(key[0], key[1], key[2], -1)] = True
                    else:
                        base_polygon[Point(key[0], key[1], key[2], 1.5708)] = True
                elif(key[1] == min_y):
                    if(key[0] > x_of_min_y):
                        base_polygon[Point(key[0], key[1], key[2], 0)] = True
                    else:
                        base_polygon[Point(key[0], key[1], key[2], 3.14159)] = True
                else:
                    ang = np.arctan((key[1] - min_y)/(key[0] - x_of_min_y))
                    if(ang < 0):
                        ang = 3.14159 + ang
                    base_polygon[Point(key[0], key[1], key[2], ang)] = True

        convex_hull = []
        other_base_points = []
        base_points = list(base_polygon.keys())
        base_points.sort(key=lambda x: x.polar_angle)
        convex_hull.append((base_points[0]).point)
        #st.text("(" + str((base_points[0]).point[0]) + "," + str((base_points[0]).point[1]) + "," + str((base_points[0]).point[2]) + "): " + str((base_points[0]).polar_angle))
        for p in range(1, len(base_points)):
            ori = orientation(convex_hull[-1][0], convex_hull[-1][1], (base_points[p]).point[0], (base_points[p]).point[1], x_of_min_y if(p == len(base_points) - 1) else (base_points[p + 1]).point[0], min_y if(p == len(base_points) - 1) else (base_points[p + 1]).point[1])
            #st.text("(" + str((base_points[p]).point[0]) + "," + str((base_points[p]).point[1]) + "," + str((base_points[p]).point[2]) + "): " + str((base_points[p]).polar_angle))
            if(ori == 2):
                convex_hull.append((base_points[p]).point)
            else:
                other_base_points.append((base_points[p]).point)
        #st.text(avg_x)
        #st.text(avg_y)
        #st.text(min_z)
        plot_stuff(avg_x, avg_y, convex_hull, other_base_points)
        if(isInPolygon(avg_x, avg_y, convex_hull)):
            st.text("Won't topple!")
        else:
            st.text("Will topple!")
    else:
        st.text("Nah....")
                  
    
      
