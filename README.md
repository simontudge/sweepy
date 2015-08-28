#Sweepy

Python module for automatic parameter sweeping of modules.

##Why?

Frequenctly in scientific computing it is necessary to "sweep" through the parameters of a model, and observe some
key parameters. In principle this is a trivial task, but often snowballs into a long list of small but irratating tasks.
e.g. constructing the necessary for loops, then realising the experiment needs to be repeated, taking the mean of your
data, saving the data in a sensible format. Writing a README file describing the data, producing a good graphical output
of the results, labeling the axes etc. All these tasks are trivial on their own, but result in a big slow down when you
add up the time taken to do all of them. Whats more you may find yourself doing these task multiple times. Sweepy takes
care of all these things, and allows you to perform them all in a single line of code.

##Main Features

- [ ] Sweep modules defined as either functions or classes
- [ ] Sweep any number of parameters, with graphical output for upto three
- [ ] Automatically generates line graphs or heat maps, depending on dimentionality
- [ ] Pickles you data
- [ ] Creates a README
- [ ] Output any number of variables, each stored in it's own subdirectory
- [ ] Creates the directory structure for you
- [ ] Compatible with either python 2 or 3

##Instructions

Clone the module and add the directory to you PYTHONPATH. Run examples.py, this should create three folders in the working
directory as sample outputs. Reading the doc strings of sweep_func and sweep_class, as well as inspecting the examples module
should be all that is needed to start sweeping.

##Planned work

- [ ] Automated parallelisation
