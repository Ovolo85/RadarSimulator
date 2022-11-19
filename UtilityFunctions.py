
from numpy import arccos, arctan, cos, deg2rad, rad2deg, sin, sqrt

c = 300000000

def azElRange2NorthEastDown(az, el, range):
    east = range * sin(deg2rad(90-el))*cos(deg2rad(90-az))
    north = range * sin(deg2rad(90-el))*sin(deg2rad(90-az))
    down = - range * cos(deg2rad(90-el))

    return [north, east, down]

def northEastDown2AzElRange(n, e, d):
    r = sqrt(n**2 + e**2 + d**2)
    if e != 0:
        az = 90 - rad2deg(arctan(n/e))
    else:
        az = 0
    if e < 0:
        az -= 180
    el = 90 - rad2deg(arccos(-d/r))

    return [az, el, r]

def headingPitchVelocity2Vector(heading, pitch, velocity):
    east = velocity * sin(deg2rad(90-pitch)) * cos(deg2rad(90-heading)) 
    north = velocity * sin(deg2rad(90-pitch)) * sin(deg2rad(90-heading))
    down = - velocity * cos(deg2rad(90-pitch))

    return [north, east, down]

def angleBetweenVectors(v1, v2):
    scalarProduct = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    absV1 = sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    absV2 = sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)

    cosOfAngle = scalarProduct / (absV1 * absV2)
    if cosOfAngle > 1: 
        cosOfAngle = 1
    elif cosOfAngle < -1:
        cosOfAngle = -1
    return rad2deg(arccos(cosOfAngle))

def vectorOwnshipToTarget(ownship, target):
    toTargetVector = [target[1]-ownship[1],
                        target[2]-ownship[2],
                        target[3]-ownship[3]]
    return toTargetVector

def vectorToRange(vector):
    result = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    return result

def calculateLowestPositiveDopplerBin(highestOpeningVel, binSize):
    return int(abs(highestOpeningVel) / binSize) + 1

def calculateMUR(prf):
    pri = 1/prf
    global c
    mur = (c * pri) / 2
    return mur

def calculateMUV(prf, f_tx):
    muv = (c * prf)/(2*f_tx)
    return muv

def calculateEclipsingZoneSize(pw):
    global c
    size = (pw * c) / 2
    return size

def calculateClutterVel(az, el, vel):
    return vel * cos(deg2rad(az)) * cos(deg2rad(el))

def calculateRangeRate(antAz, antEl, ownshipHeading, ownshipPitch, ownshipVel, tgtHeading, tgtPitch, tgtVel):
    # TODO: is using Antenna Angles correct? Or shall that be the actual sightline?
    ownshipVelVector = headingPitchVelocity2Vector(ownshipHeading, ownshipPitch, ownshipVel)
    tgtVelVector = headingPitchVelocity2Vector(tgtHeading, tgtPitch, tgtVel)
    antennaVector = azElRange2NorthEastDown (antAz, antEl, 200)
    
    scalarProductTgt = antennaVector[0]*tgtVelVector[0] + antennaVector[1]*tgtVelVector[1] + antennaVector[2]*tgtVelVector[2] 
    factorTgt = scalarProductTgt / (antennaVector[0]**2 + antennaVector[1]**2 + antennaVector[2]**2)
    vectorTgt = [factorTgt*antennaVector[0], factorTgt*antennaVector[1], factorTgt*antennaVector[2]]

    rangeRateTgt = sqrt(vectorTgt[0]**2 + vectorTgt[1]**2 + vectorTgt[2]**2)
    #print(angleBetweenVectors(antennaVector, tgtVelVector))
    if abs(angleBetweenVectors(antennaVector, tgtVelVector)) < 90: # Opening RR
        rangeRateTgt = rangeRateTgt * -1

    scalarProductOwnship = antennaVector[0]*ownshipVelVector[0] + antennaVector[1]*ownshipVelVector[1] + antennaVector[2]*ownshipVelVector[2] 
    factorOwnship = scalarProductOwnship / (antennaVector[0]**2 + antennaVector[1]**2 + antennaVector[2]**2)
    vectorOwnship = [factorOwnship*antennaVector[0], factorOwnship*antennaVector[1], factorOwnship*antennaVector[2]]

    rangeRateOwnship = sqrt(vectorOwnship[0]**2 + vectorOwnship[1]**2 + vectorOwnship[2]**2)

    if abs(angleBetweenVectors(antennaVector, ownshipVelVector)) > 90: # Opening RR, impossible with forward looking Radar
        rangeRateOwnship = rangeRateOwnship * -1
        print("Radar Looking Backwards!")

    return rangeRateTgt + rangeRateOwnship
    
if __name__ == "__main__":
    #print(azElRange2NorthEastDown(-135, -10, 1000))
    #print(angleBetweenVectors([1,1,1], [1,2,1]))
    #print(calculateMUR(1000))
    #print(calculateEclipsingZoneSize(0.000003))
    #print(headingPitchVelocity2Vector(45, 10, 200))
    #print(calculateRangeRate(antAz=45, antEl=0, ownshipHeading=45, ownshipPitch=0, ownshipVel=200, tgtHeading=135, tgtPitch=0, tgtVel=200))
    print(calculateMUV(24000, 10000000000))
