
from numpy import arccos, cos, deg2rad, rad2deg, sin, sqrt


def azElRange2NorthEastDown(az, el, range):
    east = range * sin(deg2rad(90-el))*cos(deg2rad(90-az))
    north = range * sin(deg2rad(90-el))*sin(deg2rad(90-az))
    down = - range * cos(deg2rad(90-el))

    return [north, east, down]

def angleBetweenVectors(v1, v2):
    scalarProduct = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    absV1 = sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    absV2 = sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)

    cosOfAngle = scalarProduct / (absV1 * absV2)
    return rad2deg(arccos(cosOfAngle))

def vectorOwnshipToTarget(ownship, target):
    toTargetVector = [target[1]-ownship[1],
                        target[2]-ownship[2],
                        target[3]-ownship[3]]
    return toTargetVector

def vectorToRange(vector):
    result = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    return result
    
if __name__ == "__main__":
    print(azElRange2NorthEastDown(-135, -10, 1000))
    print(angleBetweenVectors([1,1,1], [1,2,1]))

