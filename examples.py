"""A set of examples with which to test the sweepy functionality. These tests serve a) as partial documentation, so that
use of the module should be clear from examining the examples, and b) as a testing suit for future updates.

"""

import sweepy
import math
from numpy import random
import numpy as np

def almost_square( x, sig ):
	"""
	A function which takes inputs x and sig and retruns x^(2+E) where E is a small
	gaussian error term generatesd randomly from random.normal(0,sig)

	"""
	
	return x**( 2 + random.normal( 0, sig ) )

class survival_of_the_largest():
	"""
	Class defining a model which evolves integers. An integer's fitness is defined
	as how large it is.
	
	"""

	def __init__( self, pop_size, mu, gens ):
		"""
		inputs:
		-------
		pop_size : int
			number of integer individuals to have in the population.
		mu : 0 < float < 1
			mutation rate, with probability mu an individual turns into another random number
		gens : int
			number of generations to select for

		"""
		self.pop_size = int( pop_size )
		self.mu = mu
		self.gens = gens
		self.population = random.choice( list( range( 100 ) ) , self.pop_size )

	def mutate( individual ):
		"""
		Randomly mutates an individual with probability mu

		"""
		if random.random() < self.mu :
			return random.randint(100)
		else:
			return individual

	def go(self):
		"""
		Set the simulation running

		"""

		##Define fitness as the value of the individual, normalised
		##to sum to one.
		for gen in range(self.gens):
			
			total = float( sum( self.population ) )
			fitness = [ i/total for i in self.population  ]

			#choose the individuals who will reproduce
			new_pop = random.choice( self.population, p = fitness, replace = True, size = self.pop_size )

			self.population = new_pop
			#list( map( self.mutate, new_pop ) )

		##The fittest indivdual
		self.max = max( self.population )

		##The least fit individual
		self.min = min( self.population )

		##The mean fitness
		self.mean_fitness = np.mean( self.population )

		##The standard deviation of fitness
		self.std_fitness = np.std( self.population )


if __name__ == "__main__":

	#Run all the examples

	##Lets run almost_square with a fixed value of sigma = 0.05 and sweep over x from 0 to 2 in steps of 100, taking the mean of 5 runs
	sweepy.sweep_func( almost_square, [ ['x', 0, 2, 100] ], fixed_params = {'sig': 0.2}, reps = 5, output_directory = 'example_almost_square', ensure_dir = True )

	##Let's run almost square, but this time sweeping over sig as well. Have x run from 0 to 2 in steps of 1000 and sigma
	#from 0.05 to 1 in steps of 100, and this time don't repeat and give the output parameter a more descriptive name, so that
	##sweepy can name the subdirectories.
	sweepy.sweep_func( almost_square, [ [ 'x', 0.2, 1.2, 1000 ], [ 'sig', 0.05, 0.5, 100 ] ],\
	 output_directory = 'example_almost_square2', ensure_dir = True, output_names = [ 'x_to_two_ish' ]  )

	##Run the survival of the largest module, and sweep over mutation rate and population size, and observe both mean fitness and std of fitness
	sweepy.sweep_class( survival_of_the_largest, [ [ 'mu', 0, 0.5, 10 ], [ 'pop_size', 10 , 50, 5 ] ], reps = 5,\
	 output_variables = [ 'mean_fitness', 'std_fitness' ], fixed_params = {'gens':100}, output_directory = 'example_SOTL', ensure_dir = True )
