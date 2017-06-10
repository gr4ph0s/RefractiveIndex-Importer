import math

class MiscFunction():
    """
    Utility Class
    FUNCTION FROM http://therenderblog.com/custom-fresnel-curves-in-maya/
    """
    def get_diff(self,a,b):
        buffer = []
        if type(a) is list:
            for i in xrange(len(b)):
                if a[i] != b[i]:
                    buffer.append(i)
        return buffer

    def IOR(self,n,k):
        theta_deg = 0
        fresnel = []

        while theta_deg <= 90:
            theta = math.radians(theta_deg)
            a = math.sqrt((math.sqrt((n**2-k**2-(math.sin(theta))**2)**2 + ((4 * n**2) * k**2)) + (n**2 - k**2 - (math.sin(theta))**2))/2)
            b = math.sqrt((math.sqrt((n**2-k**2-(math.sin(theta))**2)**2 + ((4 * n**2) * k**2)) - (n**2 - k**2 - (math.sin(theta))**2))/2)

            Fs = (a**2+b**2-(2 * a * math.cos(theta))+(math.cos(theta))**2)/(a**2+b**2+(2 * a * math.cos(theta))+(math.cos(theta))**2)
            Fp = Fs * ((a**2+b**2-(2 * a * math.sin(theta) * math.tan(theta))+(math.sin(theta))**2*(math.tan(theta))**2)/(a**2+b**2+(2 * a * math.sin(theta) * math.tan(theta))+(math.sin(theta))**2*(math.tan(theta))**2))

            R = (Fs + Fp)/2
            fresnel.append(R)
            theta_deg += 1
        return fresnel

    def vec2dDist(self,p1, p2):
        return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

    def vec2dSub(self,p1, p2):
        return (p1[0]-p2[0], p1[1]-p2[1])

    def vec2dMult(self,p1, p2):
        return p1[0]*p2[0] + p1[1]*p2[1]

    def ramer_douglas(self,line, dist):
        if len(line) < 3:
            return line
        (begin, end) = (line[0], line[-1]) if line[0] != line[-1] else (line[0], line[-2])
        distSq = []

        for curr in line[1:-1]:
            tmp = (self.vec2dDist(begin, curr) - self.vec2dMult(self.vec2dSub(end, begin), self.vec2dSub(curr, begin)) ** 2 / self.vec2dDist(begin, end))
            distSq.append(tmp)

        maxdist = max(distSq)
        if maxdist < dist ** 2:
            return [begin, end]

        pos = distSq.index(maxdist)
        return (self.ramer_douglas(line[:pos + 2], dist) +
                self.ramer_douglas(line[pos + 1:], dist)[1:])