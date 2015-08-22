"""A set of examples with which to test the sweepy functionality"""
import sweepy
import math

def math_func1(x):
	"""
	Takes a single input, x and returns the square of x
	"""
	return x**2

def math_func2(x,y):
	return math.sin( x + 2*y )


def product( w, x, y, z ):
	return w*x*y*z

if __name__ == "__main__":

	#Run all the examples

	sweepy.sweep_func( product, [ ['x', 0, 5, 10], ['y',1,20,3], ['z',8,20,12] ], fixed_params = {'w':12}, output_data = "sample_outputs", output_graphs = "sample_outputs", ensure_dir = True)

	sweepy.sweep_func( math_func1, [ ['x', 0, 5, 10] ], output_data = "sample_outputs2", output_graphs = "sample_outputs2", ensure_dir = True)

	sweepy.sweep_func( math_func2, [ ['x', -2, 2, 100], ['y', -5, 5, 100] ], output_data = "sample_outputs3", output_graphs = "sample_outputs3", ensure_dir = True)