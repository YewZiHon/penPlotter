from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
import sys

class CustomInterface(interfaces.Gcode):
    def __init__(self):
        super().__init__()

    # Override the laser_off method such that it also powers off the fan.
    def laser_off(self):
        return "G1 F1000 Z1"  # Turn off the fan + turn off the laser

    # Override the set_laser_power method
    def set_laser_power(self, *args):
        return f"G1 F1000 Z0"  # Turn on the fan + change laser power

    def linear_move(self, x=None, y=None, z=None):
        if x is None and y is None and z is None:
            return ''
        movement="G1 F300"
        if x is not None:
            movement=movement+" X"+"{0:0.1f}".format(float(x))
        if y is not None:
            movement=movement+" Y"+"{0:0.1f}".format(float(y))
        if z is not None:
            movement=movement+" Z"+"{0:0.1f}".format(float(z))
        return movement
    def set_absolute_coordinates(self):
        return "G90"
    def set_relative_coordinates(self):
        return "G91"
    def set_origin_at_position(self):
        return "G92 X0 Y0 Z0;"

    def set_unit(self, unit):
        if unit == "mm":
            return "G21"

        if unit == "in":
            return "G20"

        return ''

    def home_axes(self):
        return "G28"




def gcodeGenerate(path):
    # Instantiate a compiler, specifying the interface type and the speed at which the tool should move. pass_depth controls
    # how far down the tool moves after every pass. Set it to 0 if your machine does not support Z axis movement.
    gcode_compiler = Compiler(CustomInterface, movement_speed=1000, cutting_speed=300, pass_depth=5)
    curves = parse_file(sys.path[0]+"\\rufus.svg") # Parse an svg file into geometric curves
    gcode_compiler.append_curves(curves) 
    gcode_compiler.compile_to_file(path, passes=1)
    del gcode_compiler