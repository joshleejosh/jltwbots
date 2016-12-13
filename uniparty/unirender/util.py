import colorsys, os.path

def clamp(v, low, high):
    return min(high, max(low, v))

def lerp(v, low, high):
    return low + v*(high-low)

# well, I guess we can't call it map, so...
def morp(i, imin, imax, omin, omax):
    if imin == imax:
        return imin
    return ((i - imin) / (imax - imin)) * (omax - omin) + omin

def h2f(h, width=2):
    i = int(h, 16)
    return float(i) / (pow(16,width)-1)

def f2h(f, width=2):
    i = int(f*(pow(16,width)-1))
    fmt = '%%0%dX'%width
    s = fmt%i
    return s

def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#%s%s%s'%(f2h(r), f2h(g), f2h(b))

def basebase(fn):
    return os.path.splitext(os.path.basename(fn))[0]

