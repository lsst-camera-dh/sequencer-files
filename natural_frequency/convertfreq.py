#!/usr/bin/env python
import math
import re

with open('FP_ITL_2s_ir2_v26.seq') as f:
	lines = f.readlines()

p=re.compile(r'(\d*) ns')
for aline in lines:
	try:
		timing=(p.search(aline).group(1))
		newtiming=(int(math.ceil(int(timing)*10/6.4)))
#		print(re.sub(r'(\d*) ns',r'{} ns'.format(newtiming), aline.rstrip()), timing)
		print(re.sub(r'(\d*) ns',r'{} ns'.format(newtiming), aline.rstrip()))

	except:
#		pass
		print(aline.rstrip())
