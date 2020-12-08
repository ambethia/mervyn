#	make moar extrusion on loops possible
#	makes acceleration on perimeters differ from others possible

#	put this in your printer -> firmware -> postprocess 	postprocess.py <FILE> Y:\gcodes
#	Y:\gcodes is a mounted netdrive on my worklaptop (NFS on minipc)

accel_a = 2000	#	acceleration on perimeters and top
accel_b = 3200	#	acceleration everything else

square_a = 5	#	square_corner_velocity on perimeters and top
square_b = 5	#	square_corner_velocity everything else

slow_accel = [ 'Perimeter Path', 'Loop Path' ]
fast_accel = [ 'Travel Path', 'Solid Path', 'Infill Path', 'Crown Path' ]

#	extra extrusion?
moar_extrusions = [ 'Crown Path' ]
moar_multipler = 1.0025 #	helps the loops to overlap and generate stronger parts - 2.2 importance

#	less extrusuion?
less_extrusions = [ ]
less_multipler = 1.0

import sys, time , os

#
src_file = sys.argv[1]
#

gcode = []
with open( src_file , 'r' ) as fp:
	for cnt, line in enumerate(fp):
		gcode.append( line )

#

output = []
do_extra = False
do_less = False
last_accel = 0
for i in range( 0 , len(gcode) ):

	l_ = gcode[i]

	if any(path_ in l_ for path_ in fast_accel) \
		and last_accel != accel_b:
		output.append( 'SET_VELOCITY_LIMIT ACCEL=' + str(accel_b) + ' ACCEL_TO_DECEL=' + str(accel_b) + ' SQUARE_CORNER_VELOCITY=' + str(square_b) + '\n' )
		last_accel = accel_b

	if any(path_ in l_ for path_ in slow_accel) \
		and last_accel != accel_a:
		output.append( 'SET_VELOCITY_LIMIT ACCEL=' + str(accel_a) + ' ACCEL_TO_DECEL=' + str(accel_a) + ' SQUARE_CORNER_VELOCITY=' + str(square_a) + '\n' )
		last_accel = accel_a

	#	switch between linetypes
	if '[feed mm/s]' in l_:
		if any(path_ in l_ for path_ in moar_extrusions):
			do_extra = True
		elif any(path_ in l_ for path_ in less_extrusions):
			do_less = True
		else:
			do_extra = False
			do_less = False
	#	do that extra
	if do_extra or do_less:
		if l_.startswith( 'G1 X' ):
			lele = l_.split(' ')
			for e in range(0,len(lele)):
				if 'E' in lele[e]:
					mult = moar_multipler if do_extra else less_multipler
					org = lele[e]
					lele[e] = 'E' + str( round( float( lele[e][1:] ) * mult, 6) ) #+ ' ; transformed from: ' + l_

			l_ = " ".join(lele)
			if '\n' not in l_:
				l_ = l_ + '\n'

	output.append(l_)

with open( sys.argv[1] , 'w') as f:
	for line in output:
		f.write(line)

os.system('curl -k -H "X-Api-Key: NULL" -F "select=false" -F "print=false" -F "file=@' + sys.argv[1] + '" "http://mervyn.local/api/files/local"')

exit(0)