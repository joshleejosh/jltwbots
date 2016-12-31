# losumiprem

# Take an arpabet phone and split it into the phone and the stress indicator.
# If there isn't an indicator, return 0 there.
def split_stress(p):
    if p[-1].isdigit():
        return p[:-1], int(p[-1])
    else:
        return p, 0

