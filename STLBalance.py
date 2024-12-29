
import streamlit as st
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import numpy as np

def isInPolygon(x0, y0, points):#ray casting algorithm
    if(len(points) == 0):
        return True;
    if(len(points) == 1):
        return False
    num_sign_changes = 0;
    for i in range(len(points)):
      prev_ind = (len(points) - 1) if i == 0 else (i - 1)
      #the ray extends from the point downwards vertically
      m = (points[i][1] - points[prev_ind][1])/(points[i][0] - points[prev_ind][0])
      if((m*(x0 - points[prev_ind][0]) + points[prev_ind][1] < y0) and (points[i][0] - x0)*(points[prev_ind][0] - x0) < 0):
        num_sign_changes += 1
      
    if(num_sign_changes != 0):
      return num_sign_changes%2 == 1;
    

    num_sign_changes = 0;
    for i in range(len(points)):
      prev_ind = (len(points) - 1) if i == 0 else (i - 1)
      #the ray extends from the point upwards vertically
      m = (points[i][1] - points[prev_ind][1])/(points[i][0] - points[prev_ind][0])
      if((m*(x0 - points[prev_ind][0]) + points[prev_ind][1] > y0) and (points[i][0] - x0)*(points[prev_ind][0] - x0) < 0):
        num_sign_changes += 1
    return num_sign_changes%2 == 1;

def plot_stuff(COM_x, COM_y, convex_hull):
    for key in convex_hull:
        plt.scatter(np.array([key[0]]), np.array([key[1]]), marker = ".")
    plt.scatter(np.array([COM_x]), np.array([COM_y]), marker = "x")
    st.pyplot(plt.figure())
    
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
                st.text("(" + str(L[1]) + "," + str(L[2]) + "," + str(L[3]) + ")")
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
        base_polygon = {}
        for key in hashmap:
            if(key[2] < (min_z + 2)):
                base_polygon[key] = True
                st.text("(" + str(key[0]) + "," + str(key[1]) + ")")
        st.text(avg_x)
        st.text(avg_y)
        st.text(min_z)
        if(isInPolygon(avg_x, avg_y, list(base_polygon.keys()))):
            st.text("Won't topple!")
        else:
            st.text("Will topple!")
    else:
        st.text("Nah....")
                  
    
      
