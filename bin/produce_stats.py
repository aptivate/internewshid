#!/usr/bin/env python

import hotshot.stats
import sys

stats = hotshot.stats.load(sys.argv[1])
stats.sort_stats('time', 'calls')
stats.print_stats(2000)
