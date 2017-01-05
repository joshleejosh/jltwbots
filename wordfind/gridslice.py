# encoding: utf-8
# Slice a grid in any of 8 directions. Assumes the grid is square.

# Return tuple (x, y, dx, dy), where x,y is the starting location for the slice
# on the grid and dx,dy is the increment to walk through the slice.
#
# direction     first slice (G = grid size - 1)
# 0 → W to E    top-left (0,0)
# 1 ↘ NW to SE  bottom-left (0,G)
# 2 ↓ N to S    top-left  (0,0)
# 3 ↙ NE to SW  top-left (0,0)
# 4 ← E to W    top-right (G,0)
# 5 ↖ SE to NW  bottom-left (0,G)
# 6 ↑ S to N    bottom-left (0,G)
# 7 ↗ SW to NE  top-left (0,0)
#
def slice_params(grid, di, si):
    mg = len(grid) - 1
    return [(0, si,  1,  0),
            # x = 000001234
            # y = 432100000
            (max(0, si-mg), max(0, mg-si),  1,  1),
            (si, 0,  0,  1),
            # x = 012344444
            # y = 000001234
            (min(mg, mg-(mg-si)), max(0, si-mg), -1,  1),
            (mg, si, -1,  0),
            # x = 012344444
            # y = 444443210
            (min(mg, mg-(mg-si)), min(mg, mg-(si-mg)), -1, -1),
            (si, mg,  0, -1),
            # x = 000001234
            # y = 123444444
            (max(0, si-mg), min(mg, mg-(mg-si)),  1, -1),
            ][di]

# Return a string containing the characters pulled out of the grid along the
# given slice.
def cut_slice(grid, di, si):
    gsize = len(grid)
    x, y, dx, dy = slice_params(grid, di, si)
    cut = ''
    while (0 <= x < gsize) and (0 <= y < gsize):
        cut += grid[y][x]
        x += dx
        y += dy
    return cut


if __name__ == '__main__':
    arrows = u'→↘↓↙←↖↑↗'
    g5 = [
            ['A','B','C','D','E',],
            ['F','G','H','I','J',],
            ['K','L','M','N','O',],
            ['P','Q','R','S','T',],
            ['U','V','W','X','Y',],
            ]
    g = [
            ['A','B','C','D','E','F','G','H',],
            ['I','J','K','L','M','N','O','P',],
            ['Q','R','S','T','U','V','W','X',],
            ['Y','Z','a','b','c','d','e','f',],
            ['g','h','i','j','k','l','m','n',],
            ['o','p','q','r','s','t','u','v',],
            ['w','x','y','z','0','1','2','3',],
            ['4','5','6','7','8','9','+','/',],
            ]

    for i in xrange(4):
        sz = len(g)
        fmt = '%%-%ds %%%ds'%(sz, sz)
        print fmt%('%d %s'%(i, arrows[i]), '%s %d'%(arrows[(i+4)%8], (i+4)%8))
        if i%2==1:
            sz = len(g) * 2 - 1
        for j in xrange(sz):
            c = cut_slice(g, i, j)
            k = (i+4)%8
            d = cut_slice(g, k, j)
            fmt = '%%%ds %%-%ds'%(len(g), len(g))
            print fmt%(c,d)
        print ''

