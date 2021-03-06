import numpy
import openmoc

###############################################################################
#                          Main Simulation Parameters
###############################################################################

opts = openmoc.options.Options()

openmoc.log.set_log_level('NORMAL')

openmoc.log.py_printf('TITLE', \
  'Simulating a one group homogeneous infinite medium...')
openmoc.log.py_printf('HEADER', 'The reference keff = 1.43...')


###############################################################################
#                            Creating Materials
###############################################################################

openmoc.log.py_printf('NORMAL', 'Creating materials...')

sigma_f = numpy.array([0.0414198575])
nu_sigma_f = numpy.array([0.0994076580])
sigma_s = numpy.array([0.383259177])
chi = numpy.array([1.0])
sigma_t = numpy.array([0.452648699])

infinite_medium = openmoc.Material(name='1-group infinite medium')
infinite_medium.setNumEnergyGroups(1)
infinite_medium.setSigmaF(sigma_f)
infinite_medium.setNuSigmaF(nu_sigma_f)
infinite_medium.setSigmaS(sigma_s)
infinite_medium.setChi(chi)
infinite_medium.setSigmaT(sigma_t)


###############################################################################
#                            Creating Surfaces
###############################################################################

openmoc.log.py_printf('NORMAL', 'Creating surfaces...')

left = openmoc.XPlane(x=-100.0, name='left')
right = openmoc.XPlane(x=100.0, name='right')
top = openmoc.YPlane(y=100.0, name='top')
bottom = openmoc.YPlane(y=-100.0, name='bottom')

left.setBoundaryType(openmoc.REFLECTIVE)
right.setBoundaryType(openmoc.REFLECTIVE)
top.setBoundaryType(openmoc.REFLECTIVE)
bottom.setBoundaryType(openmoc.REFLECTIVE)


###############################################################################
#                             Creating Cells
###############################################################################

openmoc.log.py_printf('NORMAL', 'Creating cells...')

cell = openmoc.Cell()
cell.setFill(infinite_medium)
cell.addSurface(halfspace=+1, surface=left)
cell.addSurface(halfspace=-1, surface=right)
cell.addSurface(halfspace=+1, surface=bottom)
cell.addSurface(halfspace=-1, surface=top)


###############################################################################
#                             Creating Universes
###############################################################################

openmoc.log.py_printf('NORMAL', 'Creating universes...')

root_universe = openmoc.Universe(name='root universe')
root_universe.addCell(cell)


###############################################################################
#                         Creating the Geometry
###############################################################################

openmoc.log.py_printf('NORMAL', 'Creating geometry...')

geometry = openmoc.Geometry()
geometry.setRootUniverse(root_universe)


###############################################################################
#                          Creating the TrackGenerator
###############################################################################

openmoc.log.py_printf('NORMAL', 'Initializing the track generator...')

track_generator = openmoc.TrackGenerator(geometry, opts.num_azim,
                                         opts.track_spacing)
track_generator.setNumThreads(opts.num_omp_threads)
track_generator.generateTracks()


###############################################################################
#                            Running a Simulation
###############################################################################

openmoc.log.py_printf('NORMAL', 'Running MOC forward eigenvalue simulation...')

solver = openmoc.CPUSolver(track_generator)
solver.setNumThreads(opts.num_omp_threads)
solver.setConvergenceThreshold(opts.tolerance)
solver.computeEigenvalue(opts.max_iters, mode=openmoc.FORWARD)
solver.printTimerReport()


###############################################################################
#                            Verify with NumPy
###############################################################################

openmoc.log.py_printf('NORMAL', 'Verifying with NumPy forward eigenvalue...')

# Compute fission production matrix
fiss_mat = numpy.outer(chi, nu_sigma_f)

# Create forward operator
M = numpy.linalg.solve((numpy.diag(sigma_t) - sigma_s), fiss_mat)

# Solve forward eigenvalue problem with NumPy
k, phi = numpy.linalg.eig(M)

# Select the dominant eigenvalue
k = max(k)

openmoc.log.py_printf('RESULT', 'Numpy forward eigenvalue: {0:.6f}'.format(k))
openmoc.log.py_printf('TITLE', 'Finished')
