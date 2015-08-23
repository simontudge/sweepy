import matplotlib.pyplot as plt
import numpy as np
import pickle, os, sys, warnings, time
from itertools import product
try:
	#This will make graphs look a bit prettier by default, but is not essential
	import seaborn
except ImportError:
	pass

def _check_directory( directory, ensure_dir ):
	"""
	Checks to see whether directory exists, if ensure_dir is true then make the directory if it does not. Otherwise if the directory doesn't exist
	and ensure_dir is false raise the FileNotFoundError.
	"""

	if not os.path.exists( directory ):
		if ensure_dir:
			os.makedirs( directory )
		else:
			raise FileNotFoundError("Directory '{}' does not exists, you must set ensure_dir = True if you want me to make it for you.".format( directory ) )

def sweep_func( func, sweep_params, reps = 1, fixed_params = None, output_directory = None, ensure_dir = False ):
	"""
	Function for sweeping functions. This is the one to use if the model you wish to sweep is defined as a single function.

	Inputs:

	func: the function you wish to sweep

	sweep_params: a list of parameters which the function takes, that you wish to sweep. Example input [ ['x',0,1,10] ] sweeps
	the parameter x from 0 to 1 with 10 values. [ [ 'x', 0, 5, 100 ], [ 'y', 1, 10, 20 ] ] sweeps x from 0 to 5 with 100 values,
	and y from 1 to 10 with 20 values Currently you may only have upto two sweep parameters, if one is provided any graphical output
	is in the form of a single line graph. If two are provided then the output will be a heat map.

	reps: (default 1) how many times to repeat the parameter sweep, this should only be different from one if you output in non-deterministic.

	fixed_params: this is a dictionary of additional constant parameters to be passed to the function.

	output_directory: where to output the graphs and data. Options: None (Default) in which case the data will be returned by the function,
	and the graphs will be shown on screen. Otherwise, a valid path to a directory. The directory must exist if ensure_dir is False,
	otherwise this function can create it if ensure dir = True.

	Output of graphs will be single line graphs if there is a single sweep parameter. If two are given then this will be a heatmap. If three
	then the output will be a series of heatmaps, with different values of the third input used to identify the graphs. In theory this could
	be extened to include even higher numbers of input parameters, but three is currently the maximum. The function will also only allow 128
	graphs to be produced at one time, this is to avoid acciendtly trying to create a phenomonal amount of graphs.

	ensure_dir True(default)|False. Whether or not to create the directory if it doesn't exist. 

	See also: sweep_class
	"""

	#Store the start time of the run
	start_time = now = time.strftime("%c")

	#Do some basic checking of input parameters:
	if not callable(func):
		raise TypeError("Input 'func' must be callable")

	#If the output command is a file type then out check that the directory exists, and make it if allowed, otherwise raise an error
	if output_directory:
		_check_directory( output_directory, ensure_dir )

	#Make arrays for the sweep values:
	value_lists = []
	for params in sweep_params:
		value_lists.append( np.linspace( params[1], params[2], params[3] ) )
	
	total_sweep_params = len( sweep_params )
	#Make a list of names of the sweep parameters
	param_names = [ p[0] for p in sweep_params ]
	#Lengths of parameters
	param_lengths = [ p[-1] for p in sweep_params ]

	if total_sweep_params > 3:
		print("Cannot currently make graphical outputs for more than three sweep parameters.")
		make_graphs = False
	elif total_sweep_params == 3 and param_lengths[-1] > 128:
		print("This sweep would create more than 128 graphs, so graphical output has been suppressed")
		make_graphs = False
	else:
		make_graphs = True

	#Create an empty container in which to put the data
	data_size = param_lengths.copy()
	data_size.append(reps)
	data = np.empty( tuple( data_size ) )
	
	#Create the cartesian product of all our value lists
	products = list(  product( *value_lists ) )
	#Create the cartesian product of the indices of the values
	ranges = [ range(l) for l in param_lengths ]
	indicies = list( product(*ranges) )
	for rep in range(reps):
		for index, values in zip( indicies, products ):
			#Create a dictionary of parameters to pass to the function. Using this dictionary method allows the user to
			#pass parameter values in an order other than the function accepts.
			parameter_dict = { n:v for n,v in zip( param_names, values ) }
			#"append" the fixed parameter values to list of parameters
			if fixed_params:
				parameter_dict.update( fixed_params )
			#Pass this dictionary to the function
			data[index][rep] = func( **parameter_dict )

	#Take the mean of the data and reduce the dimention representing the repeats
	data = np.mean( data, total_sweep_params )
	print(data)

	end_time = time.strftime("%c")

	#Handle graphical output:
	def make_heatmap(data):
		extent = [ sweep_params[0][1], sweep_params[0][2], sweep_params[1][1], sweep_params[1][2] ]
		plt.imshow( data.T, interpolation = 'nearest', origin = 'lower', extent = extent, aspect = 'auto' )
		plt.xlabel( param_names[0] )
		plt.ylabel( param_names[1] )
		plt.colorbar()


	if make_graphs:
		if total_sweep_params == 3:
			for i,z in enumerate( value_lists[-1] ):
				make_heatmap( data[:,:,i] )
				if output_directory:
					plt.savefig( os.path.join( output_directory, "{}_{}.png".format( param_names[-1], z ) ) )
			if not output_directory:
				plt.show()

		elif total_sweep_params == 2:
			#Make a heat map
			f = make_heatmap(data)
			if not output_directory:
				plt.show()
			else:
				plt.savefig( os.path.join( output_directory, param_names[0] + ".png" ) )
				#plt.close()
		else:
			#Make a line graph
			plt.figure()
			plt.plot( value_lists[0], data, 'o-' )
			plt.xlabel( param_names[0] )
			plt.ylabel( "{}({})".format(func.__name__, param_names[0]) )
		#Either display or save the graph(s)	
		if not output_directory:
			plt.show()
		else:
			plt.savefig( os.path.join( output_directory, param_names[0] + ".png" ) )
			plt.close()

	#Handle the output of data
	if not output_directory:
		return data
	else:
		#Output to file:
		#Output a text file describing the run
		f = open( os.path.join( output_directory, "README.txt" ), 'wt' )
		f.write( "Automatic parameter sweep generated by sweepy\n\n" )
		f.write( "Began at {}\n".format(start_time) )
		f.write( "Ended at {}\n\n".format(end_time) )
		f.write( "Using function {}\n".format(func.__name__) )
		f.write( "Sweep parameter(s):\n" )
		for p in sweep_params:
			f.write( "{} from {} to {} in {} steps\n".format( p[0], p[1], p[2], p[3] ) )
		if fixed_params:
			f.write( "\n\nFixed parameters:\n" )
			f.write( "{}".format(fixed_params) )
		f.close()
		#Pickle dump the actual data
		pickle.dump( data, open( os.path.join( output_directory, "data.p" ), 'wb' ) )

def sweep_class( input_class, sweep_params, output_variable, reps = 1, fixed_params = None, go_func_name = 'go' , output_directory = None, ensure_dir = False ):
	"""
	Sweeps a model which is defined as a class rather than a funcion.

	Inputs: input_class, a class representing the model to be sweeped.

	sweep_params: a list of parameters which the function takes, that you wish to sweep. Example input [ ['x',0,1,10] ] sweeps
	the parameter x from 0 to 1 with 10 values. [ [ 'x', 0, 5, 100 ], [ 'y', 1, 10, 20 ] ] sweeps x from 0 to 5 with 100 values,
	and y from 1 to 10 with 20 values Currently you may only have upto two sweep parameters, if one is provided any graphical output
	is in the form of a single line graph. If two are provided then the output will be a heat map.

	output_variable: in the form of a string, the name of the variable that will be recorded.

	reps: (default 1) how many times to repeat the parameter sweep, this should only be different from one if you output in non-deterministic.

	fixed_params: this is a dictionary of additional constant parameters to be passed to the function.

	go_func_name: the name of the function to call to set the model running, default 'go'. i.e. C = myClass(), C.go()
	can also be None.
	"""

	#This works simply by defining a function which initialises the class perfomrs the setup and returns the vairable in question and then calling sweep_func
	#on this function
	def class_as_func( *args, **kwargs ):
		X = input_class( *args, **kwargs )
		#Setup the class by calling it's go func if necessasry
		if go_func_name:
			exec( "X.{}()".format( go_func_name ) )
		return X.__dict__[ output_variable ]

	return sweep_func( class_as_func, sweep_params, reps = reps, fixed_params = fixed_params, output_directory = output_directory, ensure_dir = ensure_dir  )



if __name__ == "__main__":
	pass

