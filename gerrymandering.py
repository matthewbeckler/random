#!/usr/bin/env python
# Code to solve the gerrymandering problem here:
# https://fivethirtyeight.com/features/rig-the-election-with-math/
#
# Written by Matthew Beckler, released into the public domain, have fun.

import sys
import copy

verbose = True

RED = '\033[31m'
BLUE = '\033[34m'
CLEAR = '\033[0m'

# 0 = red, 1 = blue
easy = [[1, 1, 0, 0, 0],
        [0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 1]]

hard = [[0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0]]


if True:
    voters = easy
    num_dist = 5
    voters_per_dist = 5
else:
    viters = hard
    num_dist = 7
    voters_per_dist = 20

width = len(voters[0])
height = len(voters)
# district nubmers are 1 - N
state = []
for i in range(height):
    state.append( [0] * width )

def print_state(state):
    """ Print state in red/blue, numbers are district numbers. """
    for ixrow in range(height):
        for ixcol in range(width):
            if voters[ixrow][ixcol] == 0:
                print "%s%d%s" % (RED, state[ixrow][ixcol], CLEAR),
            else:
                print "%s%d%s" % (BLUE, state[ixrow][ixcol], CLEAR),
        print ""

visited = set()
rclist = []

def visit(x, y):
    """ Starting at (x, y), visit neighboring cells to see if we can visit all in rclist.
        Recursive algorithm. visited helps us avoid loops. """
    if verbose:
        print "visit(%d, %d)" % (x, y)
    if (x, y) in visited:
        if verbose:
            print "  already visited, returning"
        return
    if (x, y) not in rclist:
        if verbose:
            print "  not in rclist, returning"
        return

    if verbose:
        print "  adding to visited"
    visited.add( (x, y) )
    if y > 0:
        visit(x, y - 1)
    if y < (height - 1):
        visit(x, y + 1)
    if x > 0:
        visit(x - 1, y)
    if x < (width - 1):
        visit(x + 1, y)

def is_district_connected(thelist):
    """ Returns True if the list of (row, col) pairs are all edge-adjacent, False otherwise. """
    if verbose:
        print "is_district_connected(%s)" % str(thelist)
    global rclist, visited
    rclist = thelist
    visited = set() # track nodes we've already visited to avoid loops
    if len(rclist) == 0:
        return True
    assert len(rclist) > 0 and len(rclist) <= voters_per_dist
    x, y = rclist[0]
    visit(x, y)
    # If we could visit all the nodes, we're good
    return sorted(visited) == sorted(thelist)

verbose = False
assert is_district_connected([(1,1),(1,2),(2,2),(2,1)])
assert not is_district_connected([(1,1),(1,2),(2,2),(5,1)])


STATE_OK = 0
STATE_ERROR = 1
STATE_OK_INCOMPLETE = 2
def check_state(state):
    # Let's check district by district to see if it's valid
    # Build a map from district to a list of its squares
    dict_dist_to_rc = dict(zip(range(1,num_dist+1), [[] for i in range(num_dist)]))
    for ixdistrict in range(1, num_dist+1):
        for ixrow in range(height):
            for ixcol in range(width):
                if state[ixrow][ixcol] == ixdistrict:
                    dict_dist_to_rc[ixdistrict].append( (ixrow,ixcol) )

#    for i in range(1, num_dist+1):
#        print "District %2d:" % i, dict_dist_to_rc[i]

    all_districts_done = True
    for i in range(1, num_dist+1):
#        print "District %d -" % i,
        if len(dict_dist_to_rc[i]) > voters_per_dist:
#            print "Too many voters (%d)" % len(dict_dist_to_rc[i])
            return STATE_ERROR
        if not is_district_connected(dict_dist_to_rc[i]):
#            print "Not connected"
            return STATE_ERROR
        if len(dict_dist_to_rc[i]) < voters_per_dist:
#            print "Not finished"
            all_districts_done = False
        else:
#            print "Apparently ok"
            pass

    if all_districts_done:
        return STATE_OK
    else:
        return STATE_OK_INCOMPLETE


#print_state(state)
#print check_state(state)

valid_states = []

def go(y, x):
    """ Updates global state "state" and tries different assignments of the next square. """
#    print "-" * (y * width + x)
#print "go(%d, %d)" % (y, x)
    for ix in range(1, num_dist+1):
        state[y][x] = ix
        status = check_state(state)
        if status == STATE_ERROR:
            # Error, undo it, try the next one
            #print "  ERROR"
            state[y][x] = 0
            continue
        # Assignment to ix is ok so far, recurse if we can
        if x < (width - 1): # Go right
            go(y, x + 1)
        elif y < (height - 1): # Go down, like a typewriter
            go(y + 1, 0)
        else: # end of the grid, must be a valid state (already checked above)
            if check_state(state) == STATE_OK:
                sys.stdout.write(".")
                sys.stdout.flush()
                valid_states.append(copy.deepcopy(state))
            else:
                assert 0 # this can't happen, right?

        # TODO I guess we undo the latest change and keep going?
        state[y][x] = 0


go(0,0)


for vs in valid_states:
    print_state(vs)
    print ""


