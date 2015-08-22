"""A set of examples with which to test the sweepy functionality"""
import sweepy
import math
from numpy import random

def math_func1(x):
	"""
	Takes a single input: x, and returns its square
	"""
	return x**2

def math_func2(x,y):
	return math.sin( x + 2*y )


def product( w, x, y, z ):
	return w*x*y*z

class x_plus_random():

	def __init__( self, x, lam ):
		self.x = x
		self.lam = lam

	def go(self):
		self.A = random.normal( self.x, self.lam ) 

if __name__ == "__main__":

	#Run all the examples

	# sweepy.sweep_func( product, [ ['x', 0, 5, 10], ['y',1,20,3], ['z',8,20,12] ], fixed_params = {'w':12}, output_directory= "sample_outputs", ensure_dir = True)

	# sweepy.sweep_func( math_func1, [ ['x', 0, 5, 10] ], output_directory = "sample_outputs2", ensure_dir = True)

	# sweepy.sweep_func( math_func2, [ ['x', -2, 2, 100], ['y', -5, 5, 100] ] )

	f = sweepy.sweep_class( x_plus_random, [ ['x',-1,1,100], ['lam', .1, 2, 100 ] ], output_variable = 'A', output_directory = "Example_class1", ensure_dir = True)