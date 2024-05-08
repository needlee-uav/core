
from math import sqrt
from math import dist
import math

def gps_to_meters(lat1, lon1, lat2, lon2):
    R = 6378.137
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
    math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * \
    math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000

def build_raw_route(start_pos, points):
    points = list(map(lambda n: (n[0], n[1]), points))
    return points + [(start_pos[0], start_pos[1])]

def build_mission(start_pos, target_area, offset):
    area = build_area_points(start_pos, target_area)
    points = list(map(lambda n: (n["lat"], n["lon"]), area))
    direct_points = points
    reversed_points = points[::-1]

    mission = recursive(
        points=direct_points,
        distance=offset
    )

    if mission == False:
        mission = recursive(
            points=reversed_points,
            distance=offset
        )
    mission = mission + [(start_pos["lat"], start_pos["lon"])]
    return mission


def build_area_points(start_pos, target_area):
    nearest_point_index = get_nearest_point(start_pos, target_area)
    get_nearest_point(target_area[nearest_point_index], target_area)
    return reorder_target_area(target_area)

def get_nearest_point(start_pos, target_area):
    nearest_point_index = 0
    for i in range(len(target_area)):
        target_area[i]["distance"] = gps_to_meters(start_pos["lat"], start_pos["lon"], target_area[i]["lat"], target_area[i]["lon"])
        if (target_area[i]["distance"] < target_area[nearest_point_index]["distance"]):
            nearest_point_index = i
    return nearest_point_index

def reorder_target_area(target_area):
    target_area = sorted(target_area, key=lambda d: d["distance"])
    nearest_point = target_area[1]
    diagonal_point = target_area[3]

    target_area[1] = target_area[2]
    target_area[2] = diagonal_point
    target_area[3] = nearest_point

    return target_area


def right_M(r, M0, M1, M2):
    x, y = zip(*(M0, M1, M2))
    dx, dy = ((t[1]-t[0], t[2]-t[1]) for t in (x, y))
    norm = tuple(sqrt(dx[i] ** 2 + dy[i] ** 2) for i in (0, 1))
    u, v = ((-dy[i]/norm[i], dx[i]/norm[i]) for i in (0,1))
    p = 1 + u[0]*v[0]+u[1]*v[1]
    w = ((u[0]+v[0])/p, (u[1]+v[1])/p)
    return (x[1] - r * w[0], y[1] - r * w[1])

def check_len(point_a, point_b, distance):
    new_point = False
    if dist([point_a[0], point_a[1]], [point_b[0], point_b[1]]) < distance*1.5:
        new_point = (point_a[0] + (point_b[0] - point_a[0]) / 2, point_a[1] + (point_b[1] - point_a[1]) / 2)
    return new_point

def reduce_points(points, distance):
    i = 0
    length = len(points) - 1
    while i < length:
        new_pt = check_len(points[i], points[i+1], distance)
        if new_pt != False:
            points.pop(i+1)
            points[i] = new_pt
        i+=1
        length = len(points) - 1
    new_pt = check_len(points[length], points[0], distance)
    if new_pt != False:
            points.pop(0)
            points[length - 1] = new_pt
    return points

def offset(points, distance):
    points.append(points[0])
    points.append(points[1])
    offset = []
    for i in range(len(points) - 2):
        offset.append(right_M(distance, *points[i:i+3]))
    offset = reduce_points(offset, distance)
    if len(offset) > 1:
        first = [offset[len(offset) - 1]]
        return first + offset[0:len(offset) - 1]
    else:
        return False

def recursive(points, distance):
    result = []
    temp_points = points
    count = 100
    while temp_points != False:
        count-=1
        if count == 0:
            result = False
            break
        result = result + temp_points
        if len(temp_points) < 3:
            break
        temp_points = offset(temp_points, distance)
    return result
