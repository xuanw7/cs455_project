import numpy as np
from matplotlib import pyplot as plt
import pygame


pygame.init()
clock = pygame.time.Clock()

'''
Initialize 8 vertices of the cube
cube_vertices: normalized positions of vertices in 3D space, shape = 8 * 3
cube_scale: used for denormalized
'''

cube_vertices = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                           [-1, -1,  1], [1, -1,  1], [1, 1,  1], [-1, 1,  1]], dtype=float)

#cube_vertices = np.array([[-1, -1, -0.5], [1, -0.6, -1.2], [0.5, 1, -0.5], [-1, 1, -1.5],
                          #[-0.5, -1.2,  1], [0, -1.8,  1], [1.5, 1.5,  1], [-1.5, 0.5,  1]], dtype=float)

                          
cube_vertices_moved = cube_vertices.copy()
cube_scale = 75


# The intergers store in this array represents the index in cube_vertices, so each [] contains a trangle
# The sequence of [x_0, x_1, x_2] is very important here:
# Let A = cube_vertices[x_0] - cube_vertices[x_1]
# Let B = cube_vertices[x_2] - cube_vertices[x_1]
# Make sure cross_product(A,B), points out of the surfaces

cube_trangles = np.array([[0,1,2],[2,3,0],  #front
                          [6,5,4],[4,7,6],  #back
                          [7,4,0],[0,3,7],  #left
                          [1,5,6],[6,2,1],  #right
                          [5,1,0],[0,4,5],  #top
                          [3,2,6],[6,7,3]]) #bottom

N = len(cube_trangles)
# trangular components of the cube    
cube_trangles_normal = np.zeros((N,3))              # store normal vector of the trangle surfaces that pointing out of the surfaces
cube_trangles_shown = np.zeros(N, dtype=bool)       # store whether a trangle should be drawn
cube_trangles_color = np.zeros((N, 3), dtype=int)   # store rgb color of each trangle


# light: Directional Light
# np.array([0.57735,0.57735,0.57735])
# np.array([0.0,0.0,1.0])
# np.array([0.0,0.0,-1.0])
light_direction_not_unit = np.array([-3.0,4.0,5.0]) 
light_direction = light_direction_not_unit / np.sqrt((light_direction_not_unit**2).sum())
light_intensity = np.array([127, 255, 212], dtype=float) 
light_intensity = light_intensity % 256


# texture: Diffuse Reflection

cube_albedo = 0.7





# Initialize pygame window
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,1000
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 

red = (255, 0, 0)
green = (0,255,0)
black = (0.0,0.0,0.0)
grays = np.array([[80, 80, 80],
                  [160,160,160], 
                  [240,240,240]])
f = 0.1
K = np.array([[1,0,0],
              [0,1,0],
              [0,0,f]], dtype=float)



center_x = WINDOW_WIDTH / 2             # center_x of the window
center_y = WINDOW_HEIGHT / 2            # center_y of the window

# rotation parameter of the cube
angle_x = 0
angle_y = 0
angle_z = 0


points = np.zeros((len(cube_vertices),2))       # location of points representing cube_vertices on the window

speed = (0.00, 0.00 , 0.00)
location = np.array([0,0,8], dtype=float)       # cube location


#The "Look-At" Camera
C = np.array([0.0,0.0, 0.0], dtype=float)       # camera location
p =  np.array([0,0,100], dtype=float)           # where camera is looking at
u = np.array([0.0,-1.0,0.0], dtype=float)       # the direction of up


# drawing function
# i, j: index of cube_vertices
# color: rgb color
# points: points representing cube_vertices on the window
def draw_line(i, j, points):
    pygame.draw.line(window, (255, 255, 255), points[i] , points[j])


def draw_trangle(i, j, k, color, points):
    pygame.draw.polygon(window, color, (points[i], points[j], points[k]))


while True:
    
    clock.tick(60)
    window.fill(grays[0])

    L = p-C
    L = L/np.sqrt(np.sum(L**2))
    s = np.cross(L,u)
    s = s/np.sqrt(np.sum(s**2))
    u_ = np.cross(s,L)

    R = np.array([[-s[0], -s[1], -s[2]],
                  [u_[0],u_[1],u_[2]],
                  [-L[0],-L[1],-L[2]]])

    relative_location = location - C # cube location relative to camera location

    rotation_matrix_x = np.array([[1, 0, 0],
                                  [0, np.cos(angle_x), -np.sin(angle_x)],
                                  [0, np.sin(angle_x), np.cos(angle_x) ]],  dtype=float)

    rotation_matrix_y = np.array([[np.cos(angle_y),  0, np.sin(angle_y)],
                                  [0, 1, 0],
                                  [-np.sin(angle_y), 0, np.cos(angle_y)]], dtype=float)

    rotation_matrix_z = np.array([[np.cos(angle_z), -np.sin(angle_z), 0],
                                  [np.sin(angle_z), np.cos(angle_z), 0],
                                  [0, 0, 1]], dtype=float)


    # determine the projected vertices location in this iteration
    for i in range(len(cube_vertices)):
        vertex = cube_vertices[i]
        moved_vertex = rotation_matrix_z @ rotation_matrix_y @ rotation_matrix_x @ vertex + relative_location # 3D position after transformation

        cube_vertices_moved[i] = moved_vertex 
        projected_vertex = K @ R @ moved_vertex # projected position after transformation

        # transform porjected position, now center_x, center_y is 0,0
        x = projected_vertex[0] / projected_vertex[2] * cube_scale + center_x
        y = projected_vertex[1] / projected_vertex[2] * cube_scale + center_y 
        points[i,:] = (x,y)



    # determine whether each trangle will be drawn and and its color
    for j in range(N):
        idx_0, idx_1, idx_2 = cube_trangles[j]
        vertex_0 = cube_vertices_moved[idx_0]
        vertex_1 = cube_vertices_moved[idx_1]
        vertex_2 = cube_vertices_moved[idx_2]
        
        A = vertex_0 - vertex_1     # vectors representing A side of an trangle
        B = vertex_2 - vertex_1     # vectors representing B side of an trangle
        C_AB =  np.cross(A,B)       # cross product of A, B, pointing out of the cube surfaces
        C_AB_unit = C_AB / np.sqrt(np.sum(C_AB**2)) # make unit vector of C_AB
        cube_trangles_normal[j] = C_AB_unit
        
        eye_vector = - vertex_1      # the vector pointing from the vertex to the eye (camera)

        if (np.dot(eye_vector, cube_trangles_normal[j]) > 0): 
            cube_trangles_shown[j] = True
            color_temp = -cube_albedo * np.dot(light_direction, cube_trangles_normal[j]) * light_intensity
            cube_trangles_color[j] = color_temp.astype(int)
            if (np.min(cube_trangles_color[j]) < 0) :
                cube_trangles_color[j] = black

        else:
            cube_trangles_shown[j] = False
            cube_trangles_color[j] = black



    
    # draw each trangle if it should be shown
    for k in range(12):
        
        idx_0, idx_1, idx_2 = cube_trangles[k]
        if (cube_trangles_shown[k] == True):
            draw_trangle(idx_0, idx_1, idx_2, cube_trangles_color[k], points)



    
    
    # draw_line(0, 1, points)
    # draw_line(1, 2, points)
    # draw_line(2, 3, points)
    # draw_line(3, 0, points)
    # draw_line(4, 5, points)
    # draw_line(5, 6, points)
    # draw_line(6, 7, points)
    # draw_line(7, 4, points)
    # draw_line(0, 4, points)
    # draw_line(1, 5, points)
    # draw_line(2, 6, points)
    # draw_line(3, 7, points)


    # move cube
    angle_x  += 0.002
    angle_y  += 0.002
    angle_z  += 0.002
    light_intensity += np.array([0.1, 0.2, 0.3], dtype=float) 
    light_intensity = light_intensity % 256
    cube_albedo += 0.001
    if (cube_albedo > 1) :
        cube_albedo -= 0.8

    location = location + speed


    # move camera using keyboard input
    w_pressed = False
    a_pressed = False
    s_pressed = False
    d_pressed = False


    key_input = pygame.key.get_pressed()
    
    if key_input[pygame.K_w]:
        C += np.array([0.0, 0.1, 0.0])    # up
    if key_input[pygame.K_s]: 
        C += np.array([0.0, -0.1,  0.0])  # down
    if key_input[pygame.K_a]:
        C += np.array([0.1, 0.0,  0.0])   # left
    if key_input[pygame.K_d]:
        C += np.array([-0.1, 0.0,  0.0])  # right
    if key_input[pygame.K_q]:
        C += np.array([0.0, 0.0,  0.1])   # zoom in
    if key_input[pygame.K_e]:
        C += np.array([0.0, 0.0, -0.1])   # zoom out

    if key_input[pygame.K_UP]:
        p += np.array([0.0,  2,  0.0])   # up
    if key_input[pygame.K_DOWN]:
        p += np.array([0.0,  -2,  0.0])  # down
    if key_input[pygame.K_LEFT]:
        p += np.array([2, 0.0,  0.0])    # left
    if key_input[pygame.K_RIGHT]:
        p += np.array([-2, 0.0,   0.0])  # right



    # close window
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            pygame.quit()
        
                

        
    pygame.display.flip()
