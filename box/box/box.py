#   MaKey MaKey Box Script - Python 3.2
#   
#   This files contains the script for managing input from MaKey MaKey sensors, as well as
#   any related functions.
#   
#   Notes:  The file contains critical code.  Since it is not that critical if triggers
#           are missed, we will choose to ignore it.  Also note that shared variables are
#           defined as single element lists.  This is so they can be passed across threads
#           by reference as we do not care about synchronization issues.
#
#   Revision History:
#       05/07/13    Steven Okai     Initial revision.
#   

from threading import *
from tkinter import *
import sched, time
import msvcrt
import sys

# Constants and other definitions
CHECK_INTERVAL = 10         # Interval to check input at in seconds.
NUM_SENSORS = 13            # Number of input sensors.
NUM_NON_KEY_SENSORS = 2     # Number of sensors that are not keys.
PATTERNS_TO_MATCH = 2       # Number of patterns to match.
KEY_EVENT = "2"             # Indicates a keyboard even.
MOUSE_BUTTON_EVENT = "4"    # Indicates a mouse button event.
WINDOW_WIDTH = 500          # Window width in pixels.
WINDOW_HEIGHT = 500         # Window height in pixels.
MOUSE_LEFT = 1              # Mouse left click.
MOUSE_RIGHT = 3             # Mouse right click.

# Shared variables
pressed_sensors = [False] * NUM_SENSORS;    # List containing statuses of sensors.
patterns_matched = [0];                     # Number of patterns matched (array with one
                                            #   element so it can be passed across
                                            #   threads by reference).

# Patterns to match.
patterns = [
        [False, False, False, False, False, False, True, True, True, True, True, True, False],
        [False, False, False, False, False, False, True, True, True, True, True, True, False],
        [False, True, True, True, True, True, True, True, True, True, True, False, False]
    ];

# Make sure there at least as many patterns as there are patterns to match.
assert (len(patterns) >= PATTERNS_TO_MATCH);

def check_sensors():
    """
    check_sensors
    
    Description:    This function checks if the sensor input matches the specified
                    pattern.  If so, it goes on to the next pattern, then resets the state
                    of all sensors to not triggered, and resets the timer for checking
                    checking the state of the sensors.  If the sensor input does not match
                    the pattern, it resets the state of all sensors and resets the timer
                    for checking the state of the sensors.  If all patterns have been 
                    found, nothing is done.
    
    Arguments:      None.
    Return Value:   None.

    Shared:         pressed_sensors (read)
                    patterns_matched (write)
    
    Input:          None.
    Output:         None.
    
    Notes:          This function is meant to be called asynchronously via a timer.
    
    Last Modified:  05/07/13
    """

    # If all patterns have been found, nothing left to do so exit.
    if (patterns_matched[0] >= PATTERNS_TO_MATCH):
        print("All patterns found!");
        sys.stdout.flush();
        return;
  
    # If matching pattern found, look again for next one.
    elif (pressed_sensors == patterns[patterns_matched[0]]):
        # Mark that all sensors have been triggered.
        patterns_matched[0] = patterns_matched[0] + 1;
        print("Pattern found!");
        print("Patterns left: " + str(PATTERNS_TO_MATCH - patterns_matched[0]));
        sys.stdout.flush();
        
    # Reset sensors and reset timer.
    reset_sensors();
    reset_check_timer();
    return;

def reset_sensors():
    """
    reset_sensors
    
    Description:    This function resets all sensors to the not triggered state.
    
    Arguments:      None.
    Return Value:   None.

    Shared:         pressed_sensors (write)
    
    Input:          None.
    Output:         None.
    
    Notes:          None.
    
    Last Modified:  05/07/13
    """
    
    print("Resetting sensors...");
    for i in range(len(pressed_sensors)):
        pressed_sensors[i] = False;

    sys.stdout.flush();
    return;

def reset_check_timer():
    """
    reset_check_timer
    
    Description:    This function resets the timer for calling the function to check the
                    sensors.
    
    Arguments:      None.
    Return Value:   None.

    Shared:         None.
    
    Input:          None.
    Output:         None.
    
    Notes:          None.
    
    Last Modified:  05/07/13
    """

    # Create a timer and start it.
    t = Timer(CHECK_INTERVAL, check_sensors);
    t.start();
    return;

def handle_sensor_trigger(event):
    """
    handle_sensor_trigger
    
    Description:    This function handles and records all event triggers from the MaKey
                    MaKey sensors.
    
    Arguments:      event - trigger event from sensors.
    Return Value:   None.

    Shared:         pressed_sensors (write)
    
    Input:          None.
    Output:         None.
    
    Notes:          None.
    
    Last Modified:  05/07/13
    """

    # Translate sensor input to array indicies to be recorded.
    cases = {   "w"         : 0,
                "a"         : 1,
                "s"         : 2,
                "d"         : 3,
                "f"         : 4,
                "g"         : 5,
                "Up"        : 6,
                "Down"      : 7,
                "Left"      : 8,
                "Right"     : 9,
                "space"     : 10,
                MOUSE_LEFT  : 11,
                MOUSE_RIGHT : 12
            }

    # Make sure that all sensors are handled.
    assert(len(cases) == NUM_SENSORS);
    
    # Handle mouse events properly.
    if (event.type == MOUSE_BUTTON_EVENT):
        # Set focus to UI window.
        frame.focus_set()
        print("clicked at", event.x, event.y);
        # Mark sensor as triggered.
        pressed_sensors[cases[event.num]] = True;
    # Handle keyboard event properly.
    elif (event.type == KEY_EVENT):
        print(event.keysym);
        # Mark sensor as triggered.
        pressed_sensors[cases[event.keysym]] = True;

    return;
        
# Initialize the timer.
reset_check_timer();

# Setup the window.
root = Tk();
frame = Frame(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT);

# Setup key bindings for the sensors.
frame.bind("<Key>", handle_sensor_trigger);
frame.bind("<Button>", handle_sensor_trigger);
frame.pack();

# Go!
root.mainloop();
