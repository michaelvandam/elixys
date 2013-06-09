"""daemon3x.py

Generic linux daemon base class for python 3.x.  Obtained from:

http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

And modified slightly."""

import sys, os, time, atexit, signal
import logging
import logging.config
logging.config.fileConfig("/opt/elixys/config/elixyslog.conf")
log = logging.getLogger("elixys")

class daemon(object):
	"""A generic daemon class.

	Usage: subclass the daemon class and override the run() method."""

	def __init__(self, pidfile, logfile):
                self.pidfile = pidfile
                self.logfile = logfile
	
	def daemonize(self):
		"""Deamonize class. UNIX double fork mechanism."""

		try: 
            #log.info("In Daemonize")
			pid = os.fork() 
			if pid > 0:
                #log.info("First fork Exit PID=%d" % pid)
				# exit first parent
				sys.exit(0) 
		except OSError as err: 
            #log.info("Failed to fork")
			sys.stderr.write('fork #1 failed: {0}\n'.format(err))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir('/') 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
            #log.info("Try to fork")
			pid = os.fork() 
			if pid > 0:
                #log.info("Second fork Exit PID=%d" % pid)
				# exit from second parent
				sys.exit(0) 
		except OSError as err: 
			sys.stderr.write('fork #2 failed: {0}\n'.format(err))
			sys.exit(1) 
            #log.info("After second fork")
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(os.devnull, 'r')
		so = open(self.logfile, 'a+')
        #log.info("After std redirect")
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(so.fileno(), sys.stderr.fileno())
	
        #log.info("After register")
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
        #log.info("Creating PIDfile: %s" % self.pidfile)
		with open(self.pidfile,'w+') as f:
			f.write(pid + '\n')
                	
	def delpid(self):
        #log.info("Why do I stop?")
		os.remove(self.pidfile)

	def start(self):
		"""Start the daemon."""
		log.info("Daemon Start")

		# Check for a pidfile to see if the daemon already runs
		try:
			with open(self.pidfile,'r') as pf:

				pid = int(pf.read().strip())
		except IOError, ex:
            #log.info("No PID %s" % str(ex))
			pid = None
	
		if pid:
			#log.info("In Client")
			message = "pidfile {0} already exist. " + \
					"Daemon already running?\n"
			sys.stderr.write(message.format(self.pidfile))
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		#log.info("Prepare to run")
		self.run()

	def stop(self):
		"""Stop the daemon."""
		#log.info("Stop Daemon")
		# Get the pid from the pidfile
		try:
			with open(self.pidfile,'r') as pf:
				pid = int(pf.read().strip())
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile {0} does not exist. " + \
					"Daemon not running?\n"
			sys.stderr.write(message.format(self.pidfile))
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, signal.SIGTERM)
				time.sleep(0.1)
		except OSError as err:
			e = str(err.args)
			if e.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print (str(err.args))
				sys.exit(1)

	def restart(self):
		"""Restart the daemon."""
		#log.info("Restart Daemon")
		self.stop()
		self.start()

	def run(self):
		"""You should override this method when you subclass Daemon.	        	
		It will be called after the process has been daemonized by 
		start() or restart()."""
                log.info("Daemon run")

