
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

# TODO: Check MUV if correct
def calculateMUV(prf, f_tx):
    muv = (c * prf)/(2*f_tx)
    return muv

def calculateEclipsingZoneSize(pw):
    global c
    size = (pw * c) / 2
    return size

def calculateClutterVel(az, el, vel):
    return vel * cos(deg2rad(az)) * cos(deg2rad(el))

def calculateRangeRate(sightlineAz, sightlineEl, ownshipHeading, ownshipPitch, ownshipVel, tgtHeading, tgtPitch, tgtVel):
    
    ownshipVelVector = headingPitchVelocity2Vector(ownshipHeading, ownshipPitch, ownshipVel)
    tgtVelVector = headingPitchVelocity2Vector(tgtHeading, tgtPitch, tgtVel)
    antennaVector = azElRange2NorthEastDown (sightlineAz, sightlineEl, 200)
    
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

def projectVectorOnPlane(vector, normal):
    scalarProduct = vector[0]*normal[0] + vector[1]*normal[1] + vector[2]*normal[2]
    factor = scalarProduct / (normal[0]**2 + normal[1]**2 + normal[2]**2)
    projectionOnNormal = [factor*normal[0], factor*normal[1], factor*normal[2]]
    projectionOnPlane = [vector[0]-projectionOnNormal[0], vector[1]-projectionOnNormal[1], vector[2]-projectionOnNormal[2]]
    return projectionOnPlane

def calculateAzMonopulse(targetSightline, antennaSightline):
    # targetSightline, antennaSightline --> NED
    normalVector = [0,0,-1000] # NED
    targetOnPlane = projectVectorOnPlane(targetSightline, normalVector)
    targetOnPlaneNorm = normalizeVector(targetOnPlane)
    antennaOnPlane = projectVectorOnPlane(antennaSightline, normalVector)
    antennaOnPlaneNorm = normalizeVector(antennaOnPlane)
    azMonopuls = angleBetweenVectors(targetOnPlane, antennaOnPlane)
    
    # get the correct sign
    # TODO: Ugly!
    if antennaOnPlaneNorm[0] > 0:
        if targetOnPlaneNorm[0] > 0:
            if targetOnPlaneNorm[1] < antennaOnPlaneNorm[1]:
                azMonopuls = azMonopuls * -1
        else:
            azMonopuls = azMonopuls * -1
    else:
        if targetOnPlaneNorm[0] < 0:
            if targetOnPlaneNorm[1] > antennaOnPlaneNorm[1]:
                azMonopuls = azMonopuls * -1
        else:
            azMonopuls = azMonopuls * -1
    
    return azMonopuls

def calculateElMonopulse(targetSightline, antennaSightline):
    # First contruct a vertical Plane and get its normal vector. For that a second plane vector is needed...
    antennaPlaneVector2 = [antennaSightline[0], antennaSightline[1], antennaSightline[2] + 10000]
    normalVector = getNormalOfPlane(antennaSightline, antennaPlaneVector2)

    # Project Antenna Sightline as well as Target Sightline on the new Plane
    targetOnPlane = projectVectorOnPlane(targetSightline, normalVector)
    targetOnPlaneNorm = normalizeVector(targetOnPlane)
    antennaOnPlane = projectVectorOnPlane(antennaSightline, normalVector)
    antennaOnPlaneNorm = normalizeVector(antennaOnPlane)
    elMonopulse = angleBetweenVectors(targetOnPlane, antennaOnPlane)

    if targetOnPlaneNorm[2] > antennaOnPlaneNorm[2]:
        elMonopulse = elMonopulse * -1

    return elMonopulse

def getNormalOfPlane(vec1, vec2):
    c1 = vec1[1] * vec2[2] - vec1[2] * vec2[1]
    c2 = vec1[2] * vec2[0] - vec1[0] * vec2[2]
    c3 = vec1[0] * vec2[1] - vec1[1] * vec2[0]
    return[c1, c2, c3]

def normalizeVector(vector):
    length = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    normVec = [vector[0]/length, vector[1]/length, vector[2]/length]
    return normVec

if __name__ == "__main__":
    print(str(calculateMUV(15000, 10000000000)))