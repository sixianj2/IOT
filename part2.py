# for lab 1 part 2
import math

import picar_4wd as fc
import time
from picar_4wd.servo import Servo
from picar_4wd.ultrasonic import Ultrasonic

import numpy as np
import cv2
from queue import PriorityQueue

# Init Ultrasonic
us = Ultrasonic(fc.Pin('D8'), fc.Pin('D9'))

# Init Servo
servo = Servo(fc.PWM("P0"), offset=0)

STEP_IN_DEGREE = 5
us_cur_step = STEP_IN_DEGREE
speed = 20
cur_angle = 0
max_angle = 90
min_angle = -90
my_scan_list = []
START_ANGLE = -95
END_ANGLE = 90
# max detection range in cm
MAX_DETECTION_RANGE = 40
# map grid dimension and size
topo_shape = (25, 25)
grid_size_in_cm = 4
topo_map = np.zeros(topo_shape)

# car position
car_coord_raw = 80, 0
car_grid_image_coord = -1, -1
dest_grid_image_coord = 0, 10
FORWARD, BACKWARD, LEFT, RIGHT = 0, 1, 2, 3
# Facing up initially
car_facing_dir = FORWARD

# Movement needed to go to the front, back, left, right cells based ont he current facing direction
car_facing_dir_to_movement = {
    FORWARD: [FORWARD, BACKWARD, LEFT, RIGHT],
    BACKWARD: [BACKWARD, FORWARD, RIGHT, LEFT],
    LEFT: [RIGHT, LEFT, FORWARD, BACKWARD],
    RIGHT: [LEFT, RIGHT, BACKWARD, FORWARD]
}


CLEARANCE = 2
SCAN_STEP = 10

def main():
    global car_grid_image_coord, car_coord_raw, car_facing_dirar
    # generate numpy array
    car_grid_image_coord = get_grid_image_coord(get_grid_xy_coord(car_coord_raw))
    topo_map[car_grid_image_coord] = 3
    servo.set_angle(START_ANGLE)
    iter = 0
    # while iter < 1:
    #     move_right()
    #     time.sleep(0.5)
    #     iter += 1
    # return
    reach_target = False
    while not reach_target:
        # turn the car forard before scanning
        print('rescanning surrounding')
        turn_car_forward()
        distance_angle_list = get_distance_angles()
        #print(distance_angle_list)
        update_map(topo_map, distance_angle_list)
        iter += 1
        np.set_printoptions(threshold=np.inf)
        #print(topo_map)
        print(topo_map)
        path = a_star_search(topo_map, car_grid_image_coord, dest_grid_image_coord)
        path = path[:SCAN_STEP + 1]
        print(path)
        # draw path
        idx2 = np.array(path)
        topo_map[idx2[:, 0], idx2[:, 1]] = 2
        print('writing topo.jpg')
        cv2.imwrite('topo_' + str(iter)+ '.jpg', topo_map * 255)
        visualize(topo_map, 'topo_color_' + str(iter)+ '.jpg')
        print(topo_map)
        navigate(path)
        reach_target = car_grid_image_coord == dest_grid_image_coord
        # time.sleep(0.5)
        #move_left()


def turn_car_forward():
    global car_facing_dir
    movements = [None, None, move_left, move_right]
    if car_facing_dir == FORWARD or car_facing_dir == BACKWARD:
        return
    movement_idx = car_facing_dir_to_movement[car_facing_dir][FORWARD]
    movements[movement_idx](going_forward = False)
    car_facing_dir = FORWARD

def visualize(topo_map, output_path='topo-color.jpg'):
    map_output_img = np.zeros((topo_shape[0], topo_shape[1], 3))
    # obstacle: red
    map_output_img[topo_map == 1] = [0, 0, 255]
    # path: green
    map_output_img[topo_map == 2] = [0, 128, 0]
    map_output_img[topo_map == 3] = [255, 0, 0]
    print('writing images')
    # write pixels for visualization
    cv2.imwrite(output_path, map_output_img)

def navigate(path):
    global car_grid_image_coord

    for next in path:
        print(f'cur car loc:{car_grid_image_coord}, need to go to: {next}')
        make_movement(car_grid_image_coord, next)
        #time.sleep(0.5)
        time.sleep(2)


def make_movement(cur_pos, next_pos):
    global car_coord_raw, car_grid_image_coord, car_facing_dir
    movements = [move_forward, move_backward, move_left, move_right]
    dist = 0
    movement_idx = None
    if next_pos[1] - cur_pos[1] == 0 and next_pos[0] - cur_pos[0] < 0: #== -1:
        # next cell to the front
        movement_idx = car_facing_dir_to_movement[car_facing_dir][FORWARD]
        movements_func = movements[movement_idx]
        dist = movements_func()
        car_coord_raw = car_coord_raw[0], car_coord_raw[1] + dist
        car_facing_dir = FORWARD
    elif next_pos[1] - cur_pos[1] == 0 and next_pos[0] - cur_pos[0] > 0:#== 1:
        # next cell to the back
        movement_idx = car_facing_dir_to_movement[car_facing_dir][BACKWARD]
        movements_func = movements[movement_idx]
        dist = movements_func()
        car_facing_dir = BACKWARD
        car_coord_raw = car_coord_raw[0], car_coord_raw[1] - dist
    elif next_pos[0] - cur_pos[0] == 0 and next_pos[1] - cur_pos[1] < 0: #== -1:
        # next cell to the left
        movement_idx = car_facing_dir_to_movement[car_facing_dir][LEFT]
        movements_func = movements[movement_idx]
        dist = movements_func()
        car_facing_dir = LEFT
        car_coord_raw = car_coord_raw[0] - dist, car_coord_raw[1]
    elif next_pos[0] - cur_pos[0] == 0 and next_pos[1] - cur_pos[1] > 0: #== 1:
        # next cell to the right
        movement_idx = car_facing_dir_to_movement[car_facing_dir][RIGHT]
        movements_func = movements[movement_idx]
        dist = movements_func()
        car_facing_dir = RIGHT
        car_coord_raw = car_coord_raw[0] + dist, car_coord_raw[1]
    else:
        print(f'something is wrong. cur position:{cur_pos} -- next position: {next_pos}')

    car_grid_image_coord = get_grid_image_coord(get_grid_xy_coord(car_coord_raw))
    return dist

def a_star_search(grid, src, dest):
    """
    A-star algorithm
    reference(psudocode): http://theory.stanford.edu/~amitp/GameProgramming/ImplementationNotes.html
    returns a list of node coordinate along the path
    """
    # compute the h matrix
    h = manhatan_dist_mat(grid, dest)
    print(f'source: {src}')
    pq = PriorityQueue()
    cost = 0
    pq.put((cost, src))
    costs_g = {}
    parent = {}
    costs_g[src] = cost
    node_coord = (-1, -1)
    # 4 directions: up, down, left, right(row, col)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while not pq.empty():
        _, node_coord = pq.get()
        node_cost = costs_g[node_coord]
        if node_coord == dest:
            # find dest. we are done
            break

        # moving in 4 direction
        for direction in dirs:
            new_node = node_coord[0] + direction[0], node_coord[1] + direction[1]
            cost_g = node_cost + 1
            if not is_valid_node(new_node) or grid[new_node] != 0:
                # skip obstacl[e
                continue
            if new_node not in costs_g or cost_g < costs_g[new_node]:
                # expand only unvisited node or found a path with lower cost
                costs_g[new_node] = cost_g
                cost_f = cost_g + h[new_node]
                pq.put((cost_f, new_node))
                parent[new_node] = node_coord

    if node_coord != dest:
        # can't find the path
        print('sth is wrong, path not found!')
        return []
    # get all nodes along the path
    path = []
    cur_node = dest
    while cur_node != src:
        path.append(cur_node)
        cur_node = parent[cur_node]
    path.reverse()
    return path


def is_valid_node(node_coord):
    return 0 <= node_coord[0] < topo_shape[0] and 0 <= node_coord[1] < topo_shape[1]


def update_map(topo_map, distance_angle_list):
    # filtered out the out-of-range ones
    filtered = list(filter(lambda angle_dist_tuple: angle_dist_tuple[1] != -2 and angle_dist_tuple[1] < MAX_DETECTION_RANGE, distance_angle_list))
    print(filtered)
    # compute horizontal and vertical distance for each measurement
    previous_reading = None
    for angle, dist in filtered:
        angle_rad = math.radians(abs(angle))
        horizontal_dist = math.sin(angle_rad) * dist
        vertical_dist = math.cos(angle_rad) * dist
        if angle > 0:
            # left side
            horizontal_dist = -horizontal_dist
        obstacle_xy_coord_raw = car_coord_raw[0] + horizontal_dist, car_coord_raw[1] + vertical_dist
        obstacle_xy_coord_grid = get_grid_xy_coord(obstacle_xy_coord_raw)
        # mark the coresponding grid as obstacle
        print(f'angle: {angle} - distance: {dist}')
        print(f'obstacle coordinate: {obstacle_xy_coord_grid}')
        obstacle_grid_image_coord = get_grid_image_coord(obstacle_xy_coord_grid)
        print(obstacle_grid_image_coord)
        #topo_map[obstacle_grid_image_coord] = 1
        row, col = obstacle_grid_image_coord
        #topo_map[row, col - CLEARANCE : col + CLEARANCE] = 1
        topo_map[row - CLEARANCE : row + CLEARANCE + 1, col - CLEARANCE: col + CLEARANCE + 1] = 1

        if previous_reading and abs(previous_reading[0] - angle) <= STEP_IN_DEGREE:
            extrapolate(previous_reading[1], obstacle_xy_coord_raw, topo_map)
        previous_reading = angle, obstacle_xy_coord_raw



def extrapolate(start_coord_xy, end_coord_xy, topo_map):
    '''
    mark along the slope as obstacles
    '''
    slope = (end_coord_xy[1] - start_coord_xy[1]) / (end_coord_xy[0] - start_coord_xy[0])
    new_x = start_coord_xy[0] + grid_size_in_cm
    new_y = slope * new_x + start_coord_xy[1]
    print(f'start coord: {start_coord_xy} -- end coord: {end_coord_xy}')
    while new_x < end_coord_xy[0] and new_y < end_coord_xy[1]:
        # get grid coordinate
        extrapolated_xy_coord_grid = get_grid_xy_coord((new_x, new_y))
        extrapolated_grid_image_coord = get_grid_image_coord(extrapolated_xy_coord_grid)

        if extrapolated_grid_image_coord[0] >= topo_shape[0] or extrapolated_grid_image_coord[1] >= topo_shape[1]:
            break
        print(f'marking cell {extrapolated_grid_image_coord} as 1')
        topo_map[extrapolated_grid_image_coord] = 1
        new_x = new_x + grid_size_in_cm
        new_y = slope * new_x + new_y


def get_grid_xy_coord(xy_coord_raw):
    return int(xy_coord_raw[0] / grid_size_in_cm), int(xy_coord_raw[1] / grid_size_in_cm)


def get_grid_image_coord(xy_coord_grid):
    return topo_shape[1] - xy_coord_grid[1] - 1, xy_coord_grid[0]


def move_forward():
    # for moving forward around 4cm
    #return move(fc.forward, 50, 0.25)
    return move(fc.forward, 20, 0.1)

def move_backward():
    # for moving forward around 4.1cm
    return move(fc.backward, 20, 0.1)


def move_left(going_forward = True):
    # for moving to the left
    # green battery
    #move(fc.turn_left, 50, 0.76)
    # pink battery
    #move(fc.turn_left, 50, 0.74)
    move(fc.turn_left, 18, 1.125)
    time.sleep(0.5)
    if going_forward:
        return move_forward()
    return 0


def move_right(going_forward = True):
    # for moving to the left
    # green battery
    #move(fc.turn_right, 50, 0.65)
    # pink battery
    #move(fc.turn_right, 50, 0.60)
    # green battery
    #move(fc.turn_right, 18, 1.125)
    move(fc.turn_right, 18, 1)

    time.sleep(0.5)
    if going_forward:
        return move_forward()
    return 0

def move(func, speed, duration):
    """ make the move based on speed and duration and return the distance travelled"""
    speed4 = fc.Speed(25)
    speed4.start()
    func(speed)
    x = 0
    for i in range(1):
        time.sleep(duration)
        cur_speed = speed4()
        x += cur_speed * duration
        #print("%smm/s" % cur_speed)
    print(f'distance: {x} cm')
    speed4.deinit()
    fc.stop()
    # todo: make sure this is correct
    x = 4
    return x


def get_distance_at(angle):
    servo.set_angle(angle)
    time.sleep(0.04)
    distance = us.get_distance()
    # distance is in cm
    return (angle, distance)


def get_distance_angles():
    global cur_angle
    done = False
    tmp = []
    # set the servo pointing to the start angle
    servo.set_angle(START_ANGLE)
    cur_angle = START_ANGLE
    time.sleep(0.04)
    while not done:
        tmp = scan_all_angles()
        if tmp is not False:
            print('got data!')
            done = True
    # set it back to the start angle
    servo.set_angle(START_ANGLE)
    cur_angle = START_ANGLE
    return tmp


def scan_all_angles():
    global my_scan_list, cur_angle, us_cur_step
    cur_angle += us_cur_step
    if cur_angle >= max_angle:
        cur_angle = max_angle
        us_cur_step = -STEP_IN_DEGREE
    elif cur_angle <= min_angle:
        cur_angle = min_angle
        us_cur_step = STEP_IN_DEGREE
    angle, distance = get_distance_at(cur_angle)

    my_scan_list.append((angle, distance))
    if cur_angle == END_ANGLE:
        if us_cur_step < 0:
            print("reverse")
            my_scan_list.reverse()
        # print(scan_list)
        tmp = my_scan_list.copy()
        my_scan_list = []
        return tmp
    else:
        return False


def manhatan_dist_mat(a, end_grid_coord):
    """
    compute manhatan distance from every index of a to the end index
    referenece: https://stackoverflow.com/questions/61628380/calculate-distance-from-all-points-in-numpy-array-to-a-single-point-on-the-basis
    """
    end_index = [end_grid_coord[0], end_grid_coord[1]]
    i, j = np.indices(a.shape, sparse=True)
    return abs(i - end_index[0]) + abs(j - end_index[1])


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()
