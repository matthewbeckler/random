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

def is_district_connected(reallist, unassignedlist):
    """ Returns True if the list of (row, col) pairs in reallist are all edge-adjacent (possibly using unassignedlist to help), False otherwise. """
    if verbose:
        print "is_district_connected(%s, %s)" % (str(reallist), str(unassignedlist))
    global rclist, visited
    rclist = reallist + unassignedlist
    visited = set() # track nodes we've already visited to avoid loops
    if len(rclist) == 0:
        return True
    assert len(rclist) > 0
    x, y = rclist[0]
    visit(x, y)
    # If we could visit all the nodes in reallist starting with a point in reallist, we're good
    return set(reallist).issubset(visited)

verbose = False
assert is_district_connected([(1,1),(1,2),(2,2),(2,1)],[])
assert not is_district_connected([(1,1),(1,2),(2,2),(5,1)],[])


STATE_OK = 0
STATE_ERROR = 1
STATE_OK_INCOMPLETE = 2
def check_state(state):
    # Let's check district by district to see if it's valid
    # Build a map from district to a list of its squares
    dict_dist_to_rc = dict(zip(range(0, num_dist+1), [[] for i in range(num_dist+1)]))
    for ixdistrict in range(0, num_dist+1):
        for ixrow in range(height):
            for ixcol in range(width):
                if state[ixrow][ixcol] == ixdistrict:
                    dict_dist_to_rc[ixdistrict].append( (ixrow,ixcol) )

    if verbose:
        for i in range(0, num_dist+1):
            print "District %2d:" % i, dict_dist_to_rc[i]

    all_districts_done = True
    for i in range(1, num_dist+1):
        if verbose:
            print "District %d -" % i,
        if len(dict_dist_to_rc[i]) > voters_per_dist:
            if verbose:
                print "Too many voters (%d)" % len(dict_dist_to_rc[i])
            return STATE_ERROR

        # Count unassigned cells too for the connectivity test
        if not is_district_connected(dict_dist_to_rc[i], dict_dist_to_rc[0]):
            if verbose:
                print "Not connected"
            return STATE_ERROR
        if len(dict_dist_to_rc[i]) < voters_per_dist:
            if verbose:
                print "Not finished"
            all_districts_done = False
        else:
            if verbose:
                print "Apparently ok"
            pass

    if all_districts_done:
        return STATE_OK
    else:
        return STATE_OK_INCOMPLETE


def evaluate_winners(state):
    """ Evaluates the district assignments with the voters data.
        Returns (dist_red, dist_blue, dist_tie). """
    dist_red = 0
    dist_blue = 0
    dist_tie = 0
    if check_state(state) == STATE_ERROR:
        return None
    # Build a map from district to a list of its squares
    dict_dist_to_rc = dict(zip(range(1,num_dist+1), [[] for i in range(num_dist)]))
    for ixdistrict in range(1, num_dist+1):
        for ixrow in range(height):
            for ixcol in range(width):
                if state[ixrow][ixcol] == ixdistrict:
                    dict_dist_to_rc[ixdistrict].append( (ixrow,ixcol) )
    for i in range(1, num_dist+1):
        #print "District %2d:" % i, dict_dist_to_rc[i]
        num_red = 0
        num_blue = 0
        for r, c in dict_dist_to_rc[i]:
            if voters[r][c] == 0:
                num_red += 1
            else:
                num_blue += 1
        if num_red > num_blue:
            dist_red += 1
        elif num_red < num_blue:
            dist_blue += 1
        else:
            dist_tie += 1
    return (dist_red, dist_blue, dist_tie)

def print_status(y, x):
    global state
    s = ""
    for ixrow in range(height):
        for ixcol in range(width):
            s += str(state[ixrow][ixcol])
            if ixrow == y and ixcol == x:
                return s
        s += "|"
    return s

    

# For some reason the code below can't find this solution
#state = [[1, 1, 5, 5, 5],
#         [1, 2, 2, 5, 4],
#         [1, 2, 2, 5, 4],
#         [1, 3, 2, 4, 0],
#         [0, 0, 0, 0, 0]]
#
#         #[1, 3, 2, 4, 4],
#         #[3, 3, 3, 3, 4]]
#verbose = True
#print_state(state)
#print check_state(state)
#print evaluate_winners(state)
#print print_status(3,3)
#sys.exit()

best_red_dist = 0
best_red_states = []
best_blue_dist = 0
best_blue_states = []

def go(y, x):
    """ Updates global state "state" and tries different assignments of the next square. """
    #print "go(%d, %d)" % (y, x)
    #print print_status(y, x)
    global best_red_dist, best_red_states, best_blue_dist, best_blue_states, state
    for ix in range(1, num_dist+1):
        state[y][x] = ix
        #print "  trying %d" % ix
        if check_state(state) == STATE_ERROR:
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
                dist_red, dist_blue, dist_tie = evaluate_winners(state)
#                if dist_red == best_red_dist:
#                    print ""
#                    print "%sAnother best red state (%d to %d)%s" % (RED, dist_red, dist_blue, CLEAR)
#                    print_state(state)
#                    best_red_states.append(copy.deepcopy(state))
#                if dist_red > best_red_dist:
#                    print ""
#                    print "%sNew best red state (%d to %d)%s" % (RED, dist_red, dist_blue, CLEAR)
#                    print_state(state)
#                    best_red_dist = dist_red
#                    best_red_states = [copy.deepcopy(state)]
                if dist_blue == best_blue_dist:
                    print ""
                    print "%sAnother best blue state (%d to %d)%s" % (BLUE, dist_blue, dist_red, CLEAR)
                    print_state(state)
                    best_blue_states.append(copy.deepcopy(state))
                if dist_blue > best_blue_dist:
                    print ""
                    print "%sNew best blue state (%d to %d)%s" % (BLUE, dist_blue, dist_red, CLEAR)
                    print_state(state)
                    best_blue_dist = dist_blue
                    best_blue_states = [copy.deepcopy(state)]
                
                sys.stdout.write(".")
                sys.stdout.flush()
            else:
                assert 0 # this can't happen, right?

        # Undo the latest change and keep going
        state[y][x] = 0


startx = 0
starty = 0
if False:
    #pre-seed the first row of state
    state[0][0] = 1
    state[0][1] = 1
    state[0][2] = 5
    state[0][3] = 5
    state[0][4] = 5
    state[1][0] = 1
    state[1][1] = 2
    state[1][2] = 2
    state[1][3] = 5
    state[1][4] = 4
    state[2][0] = 1
    state[2][1] = 2
    state[2][2] = 2
    state[2][3] = 5
    state[2][4] = 4
    state[3][0] = 1
    state[3][1] = 3
    state[3][2] = 2
    startx = 3
    starty = 3

go(starty, startx)

print ""
print "=" * 80
print "Final results:"
print ""
#print "%sBest red states (%d districts)%s" % (RED, best_red_dist, CLEAR)
#for s in best_red_state:
#    print ""
#    print_state(s)
print ""
print "%sBest blue states (%d districts)%s" % (BLUE, best_blue_dist, CLEAR)
for s in best_blue_state:
    print ""
    print_state(s)

