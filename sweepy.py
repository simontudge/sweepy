from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
import pickle, os, sys, warnings, time
from tqdm import tqdm, trange
from itertools import product
try:
	#This will make graphs look a bit prettier by default, but is not essential
	import seaborn
except ImportError:
	print("Could not find module seaborn, try pip install seaborn for full functionality.")

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

def sweep_func( func, sweep_params, reps = 1, fixed_params = None, record_outputs = 'only', output_names = None,\
 output_directory = None, ensure_dir = False, file_type = 'png' ):
	r"""
	Function for sweeping functions. This is the one to use if the model you wish to sweep is defined as a single function.

	Parameters:
	-----------

	func : callable
		A function that returns at least one numeric variable 
	
	sweep_params : list of lists of type [str, float, float, int] 
		a list of parameters that the function takes, which you wish to sweep. Example input [ ['x',0,1,10] ] sweeps
		the parameter x from 0 to 1 with 10 values. [ [ 'x', 0, 5, 100 ], [ 'y', 1, 10, 20 ] ] sweeps x from 0 to 5 with 100 values,
		and y from 1 to 10 with 20 values. Can be any number of sweep parameters, but graphical output is limited to three.

	reps: int (default 1), optional
		How many times to repeat the parameter sweep, this should only be different from one if you output in non-deterministic.

	fixed_params : { None, dict }, optional
		(default None) this is a dictionary of additional constant parameters to be passed to the function. E.g. {temp = 12, velocity = 26}

	record_outputs : {'only', list of booleans}, optional
		Which outputs of the function to record. Either a list of booleans or the string 'only', this is if you function returns a single numerical output. Otherwise,
		if the function returns a tuple you can specify which outputs to record via a list of booleans e.g. [True,False,True].

	output_names : {None, list of strings}, optional.
		A list of strings to identify the outputs. This is so that graphs and directories can be labeled appropriately. If None (default) falls back
		on integer naming (param1, param2 etc.)

	output_directory : {None,valid path to directory}, optional
		where to output the graphs and data. Options: None (Default) in which case the data will be returned by the function,
		and the graphs will be shown on screen. Otherwise, a valid path to a directory. The directory must exist if ensure_dir is False,
		otherwise this function can create it if ensure dir = True.

	ensure_dir {False,True} :
		Whether or not to create the directory if it doesn't exist. If this is set to false and the directory does not exist then FileNotFoundError will be raised

	file_type str (default 'png'), optional:
		A file extention for which to save the files. Will except anything that your version of matplotlib will take. e.g. 'png', 'eps', 'svg' 

	Returns
	-------

	Output of graphs will be single line graphs if there is a single sweep parameter. If two are given then this will be a heatmap. If three
	then the output will be a series of heatmaps, with different values of the third input used to identify the graphs. Each returned output
	will be put in a seperate subfolder labelled with the name of the output file.

	In the parent directory will make a text file called README.txt with information on the parameters used to generate this data.
	
	All data will be sent to a pickle file in the form of a list of numpy arrays. Each element of the list represents one of the output variables. The
	dimension of the arrays will be the number of sweep parameters plus one for the repeats.

	The function will also only allow 128 graphs to be produced at one time, this is to avoid accidently trying to create a phenomonal amount of graphs.

	If output directory is None then the graphs will be displayed rather than output to file and the data returned rather than pickled.

	Example Use
	-----------

	See examples.py

	See also
	--------

	sweep_class: wraps this functionality for use in models defined as classes rather than functions.

	"""
	##TODO check file extention exists

	#Store the start time of the run
	start_time = time.strftime("%c")

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

	#See how many outputs will be returned
	if record_outputs == 'only':
		total_outputs = 1
	else:
		try:
			total_outputs = sum( record_outputs )
		except TypeError:
			raise TypeError("record_outputs must be either the string 'only' or a list of boolenas, got {}".format( record_outputs ) )
	#Make sure param_names is the correct length, and revert to default if None
	if output_names:
		if not len(output_names) == total_outputs:
			raise ValueError("Length of output_names must be equal to the number of output parameters you wish to record.")
	else:
		output_names = [ "param_{}".format(i) for i in range( total_outputs ) ]



	#Create an empty container in which to put the data
	data_size = param_lengths + [reps]
	data = [ np.empty( tuple( data_size ) ) for i in range( total_outputs ) ]
	
	#Create the cartesian product of all our value lists
	products = list(  product( *value_lists ) )
	#Create the cartesian product of the indices of the values
	ranges = [ range(l) for l in param_lengths ]
	indicies = list( product(*ranges) )
	for rep in trange(reps):
		for index, values in zip( indicies, products ):
			#Create a dictionary of parameters to pass to the function. Using this dictionary method allows the user to
			#pass parameter values in an order other than the function accepts.
			parameter_dict = { n:v for n,v in zip( param_names, values ) }
			#"append" the fixed parameter values to list of parameters
			if fixed_params:
				parameter_dict.update( fixed_params )
			#Pass this dictionary to the function
			function_outputs = func( **parameter_dict )
			if record_outputs == 'only':
				#Record the single output parameter in the only array
				data[0][index][rep] = function_outputs
			else:
				#Otherwise strip down the outputs to the relevent ones
				relevent_outputs = [ fo for i,fo in enumerate( function_outputs ) if record_outputs[i] ]
				#And put them in each data array
				for i,r in enumerate(relevent_outputs):
					data[i][index][rep] = r

	#Take the mean of each array in data thus reducing the dimension representing the repeats
	data_meaned = [ np.mean( d, total_sweep_params ) for d in data ]

	end_time = time.strftime("%c")

	#Handle graphical output:
	def make_heatmap( data, title  ):
		extent = [ sweep_params[0][1], sweep_params[0][2], sweep_params[1][1], sweep_params[1][2] ]
		plt.imshow( data.T, interpolation = 'nearest', origin = 'lower', extent = extent, aspect = 'auto' )
		plt.xlabel( param_names[0] )
		plt.ylabel( param_names[1] )
		plt.title( title )
		plt.colorbar()

	#Loop through each array and output the graph to a seperate file
	for i,d in enumerate( data_meaned ):
		#Give each output parameter it's own subdiretory
		if output_directory:
			path = os.path.join( output_directory, output_names[i] )
			if not os.path.exists( path ):
				os.mkdir( path )

		if make_graphs:
			if total_sweep_params == 3:
				for i,z in enumerate( value_lists[-1] ):
					make_heatmap( d[:,:,i], title = output_names[i] )
					if output_directory:
						plt.savefig( os.path.join( path, "{}_{}.{}".format( param_names[0], z, file_type ) ) )
						plt.close()
				if not output_directory:
					plt.show()
					pl.close()

			elif total_sweep_params == 2:
				#Make a heat map
				f = make_heatmap( d, title = output_names[i]  )
				if not output_directory:
					plt.show()
				else:
					plt.savefig( os.path.join( path, "{}.{}".format( param_names[0], file_type ) ) )
					plt.close()
			else:
				#Make a line graph
				plt.figure()
				plt.plot( value_lists[0], d, 'o-' )
				plt.xlabel( param_names[0] )
				plt.ylabel( output_names[i] )
				#Either display or save the graph(s)	
				if not output_directory:
					plt.show()
				else:
					plt.savefig( os.path.join( path, "{}.{}".format( param_names[0], file_type ) ) )
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

def sweep_class( input_class, sweep_params, output_variables, reps = 1, fixed_params = None, go_func_name = 'go' , output_directory = None, ensure_dir = False ):
	r"""Sweeps a model which is defined as a class rather than a funcion.

	sweep_params : list of lists of type [str, float, float, int] 
		a list of parameters that the function takes, which you wish to sweep. Example input [ ['x',0,1,10] ] sweeps
		the parameter x from 0 to 1 with 10 values. [ [ 'x', 0, 5, 100 ], [ 'y', 1, 10, 20 ] ] sweeps x from 0 to 5 with 100 values,
		and y from 1 to 10 with 20 values. Can be any number of sweep parameters, but graphical output is limited to three.

	reps: int (default 1), optional
		How many times to repeat the parameter sweep, this should only be different from one if you output in non-deterministic.

	fixed_params : { None, dict }, optional
		(default None) this is a dictionary of additional constant parameters to be passed to the function. E.g. {temp = 12, velocity = 26}

	output_names : {None, list of strings}, optional.
		A list of strings to identify which outputs to look for the outputs. Must be a value of the class once go_func_name is called.

	output_directory : {None,valid path to directory}, optional
		where to output the graphs and data. Options: None (Default) in which case the data will be returned by the function,
		and the graphs will be shown on screen. Otherwise, a valid path to a directory. The directory must exist if ensure_dir is False,
		otherwise this function can create it if ensure dir = True.

	go_func_name : {str, None}
		the name of the function to call to set the model running, default 'go'. i.e. C = myClass(), C.go()
		can also be None if the __init__ method of the class defines all necessary values.
	
	Returns
	-------

	Output of graphs will be single line graphs if there is a single sweep parameter. If two are given then this will be a heatmap. If three
	then the output will be a series of heatmaps, with different values of the third input used to identify the graphs. Each returned output
	will be put in a seperate subfolder labelled with the name of the output file.

	In the parent directory will make a text file called README.txt with information on the parameters used to generate this data.
	
	All data will be sent to a pickle file in the form of a list of numpy arrays. Each element of the list represents one of the output variables. The
	dimension of the arrays will be the number of sweep parameters plus one for the repeats.

	The function will also only allow 128 graphs to be produced at one time, this is to avoid accidently trying to create a phenomonal amount of graphs.

	If output directory is None then the graphs will be displayed rather than output to file and the data returned rather than pickled.

	Example Use
	-----------

	See examples.py

	See also
	--------

	sweep_func : sweep_class essentially turns you class into a function and send to sweep_func
	
	"""

	#Allow a single string to be passed by putting it in a list
	if isinstance( output_variables, str ):
		output_variables = [output_variables]
	total_outputs = len( output_variables )
	#This works simply by defining a function which initialises the class performs the setup and returns the vairable in question and then calling sweep_func
	#on this function
	def class_as_func( *args, **kwargs ):
		X = input_class( *args, **kwargs )
		#Setup the class by calling it's go func if necessasry
		if go_func_name:
			exec( "X.{}()".format( go_func_name ) ) in locals()
		return [ X.__dict__[ ov ] for ov in output_variables ]
	#Rename the function to have the same name as the class
	class_as_func.__name__ = input_class.__name__

	return sweep_func( class_as_func, sweep_params, record_outputs = [True]*total_outputs, output_names = output_variables, reps = reps, fixed_params = fixed_params, output_directory = output_directory, ensure_dir = ensure_dir  )



if __name__ == "__main__":
	pass

