import matplotlib.pyplot as plt
import numpy as np
import pickle, os, sys, warnings, time
from itertools import product

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

def sweep_func( func, sweep_params, fixed_params = None, output_graphs = 'screen', output_data = 'return', ensure_dir = False ):
	"""
	Function for sweeping functions. This is the one to use if the model you wish to sweep is defined as a single function.

	Inputs:

	func: the function you wish to sweep

	sweep_params: a list of parameters which the function takes, that you wish to sweep. Example input [ ['x',0,1,10] ] sweeps
	the parameter x from 0 to 1 with 10 values. [ [ 'x', 0, 5, 100 ], [ 'y', 1, 10, 20 ] ] sweeps x from 0 to 5 with 100 values,
	and y from 1 to 10 with 20 values Currently you may only have upto two sweep parameters, if one is provided any graphical output
	is in the form of a single line graph. If two are provided then the output will be a heat map.

	fixed_params: this is a dictionary of additional constant parameters to be passed to the function.

	output_graphs: where to put the graphs. Options None, i.e. no graphical output will be provided. 'screen' (default), will show the graphs
	onscreen, an exisitng file directory if ensure_dir is false, or a directory which may or may not exist if ensure_dir is true.

	output_data: can be 'return' (default), i.e. simply returns the results as a numpy array. 'screen', prints the results. None, i.e.
	won't output the data, or a path to a directory. If the later the path must exist unless ensure_dir is True. Note: if outputting to file
	format will be a pickle file.

	ensure_dir True(default)|False. Whether or not to create the directory if it doesn't exist.  
	"""

	#Store the start time of the run
	start_time = now = time.strftime("%c")

	#Do some basic checking of input parameters:
	if not callable(func):
		raise TypeError("Input 'func' must be callable")

	if output_graphs == None and output_data == None:
		warning.warn("Both graphical and data outputs are set to none, this is usually a pointless thing to do!")

	#If the output command is a file type then out check that the directory exists, and make it if allowed, otherwise raise an error
	if output_graphs != 'screen' and output_graphs != None: 
		_check_directory( output_graphs, ensure_dir )
	if output_data != 'screen' and output_data != 'return' and output_data == None:
		_check_directory( output_data, ensure_dir )

	#Make arrays for the sweep values:
	value_lists = []
	for params in sweep_params:
		value_lists.append( np.linspace( params[1], params[2], params[3] ) )
	
	total_sweep_params = len( sweep_params )
	#Make a list of names of the sweep parameters
	param_names = [ p[0] for p in sweep_params ]
	#Lengths of parameters
	param_lengths = [ p[-1] for p in sweep_params ]

	#Create an empty container in which to put the data
	data = np.empty( tuple( param_lengths ) )
	
	#Create the cartesian product of all our value lists
	products = product( *value_lists )
	#Create the cartesian product of the indices of the values
	ranges = [ range(l) for l in param_lengths ]
	indicies = product(*ranges)
	for index, values in zip( indicies, products ):
		#Create a dictionary of parameters to pass to the function. Using this dictionary method allows the user to
		#pass parameter values in an order other than the function accepts.
		parameter_dict = { n:v for n,v in zip( param_names, values ) }
		#"append" the fixed parameter values to list of parameters
		if fixed_params:
			parameter_dict.update( fixed_params )
		#Pass this dictionary to the function 
		data[index] = func( **parameter_dict )

	end_time = time.strftime("%c")

	#Handle graphical output:
	if output_graphs:
		if total_sweep_params > 2:
			print("Output of graphs for more than 2 parameters not currently supported.")
		elif total_sweep_params == 2:
			#Make a heat map
			plt.figure()
			plt.imshow( data.T )
			plt.xlabel( param_names[0] )
			plt.ylabel( param_names[1] )
			if output_graphs == 'screen':
				plt.show()
			else:
				plt.savefig( os.path.join( output_graphs, param_names[0] + ".png" ) )
		else:
			#Make a line graph
			plt.figure()
			plt.plot( value_lists[0], data, 'o-' )
			plt.xlabel( param_names[0] )
			plt.ylabel( "{}({})".format(func.__name__, param_names[0]) )
			if output_graphs == 'screen':
				plt.show()
			else:
				plt.savefig( os.path.join( output_graphs, param_names[0] + ".png" ) )

	#Handle the output of data
	if output_data == 'return':
		return data
	elif output_data == 'screen':
		print(data)
	else:
		#Output to file:
		#Output a text file describing the run
		f = open( os.path.join( output_data, "README.txt" ), 'wt' )
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
		pickle.dump( data, open( os.path.join( output_data, "data.p" ), 'wb' ) )


if __name__ == "__main__":
	pass

