import urllib, urllib.request, os, sys

class core_utils(object):
	def __init__(self):
		self.ta = text_attributes()
		self.back = len("") # For cool on-line writing

	def curl(self, url):
		c = urllib.request.Request(url)
		code = urllib.request.urlopen(c).read()
		return code

	def download(self, url, f):
		try:
			try:
				urllib.request.urlretrieve(url, f)
			except ContentTooShortError:
				self.print_warning("There was an error when saving your file...")
				return False
		except NameError:
			self.print_warning("There was an error when saving your file...")
			return False
		return True

	def gen_bar(self, state, maximum, scale = 4):
		perc = round(( 100 / maximum ) * state)
		ticks = round(perc / scale)
		if ticks > maximum:
			ticks = maximum
		bar = "[%s%s]" % ("#" * ticks, " " * round((100/scale - ticks)))
		return bar

	def print_warning(self, string):
		print(self.ta.s(["red", "bold"]) + "Warning: " + self.ta.r() + string)

	def requires_root(self):
		if os.geteuid() != 0:
			print(
			  self.ta.s(["red", "bold"]) +
			  "Warning: " +
			  self.ta.r() +
			  "This operation requires root access."
			)
			sys.exit()

	def usage(self):
		print(
			self.ta.s(["green","bold"]) +
			"Usage: " +
			self.ta.s(["cyan","italic"]) +
			"%s " % sys.argv[0] +
			self.ta.r() +
			"<-S[s/i/y]> [name]"
		)
		sys.exit(42)


class file_operations(object):
	def __init__(self):
		self.base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
		self.path2config = "%s/../config/pyur.conf" % self.base_path

	def parse_config(self):
		fd = open(self.path2config, "r")
		c = fd.read()
		fd.close()
		lines = c.split("\n")
		to_remove = []
		for l in lines:
			try:
				if l[0] == "#":
					to_remove.append(l)
			except IndexError:
				pass
		for r in to_remove:
			lines.remove(r)
			try:
				lines.remove("")
			except ValueError:
				pass
		config = {}
		for l in lines:
			var_name = l.split("=")[0].replace(" ","")
			var_vals = []
			for e in l.split("=")[1].split(" "):
				if e != "":
					var_vals.append(e.replace(" ",""))
			config[var_name] = var_vals
		return config

class text_attributes(object):
	def __init__(self):
		self.base = '\033[%sm'

		self.translate = {
			# Styles
			"normal":0,
			"bold":1,
			"italic":3,
			# Colors
			"red":31,
			"violet":"35",
			"blue":34,
			"cyan":36,
			"green":32,
			"white":37,
		}

	def r(self): # reset
		return self.base % "0"

	def w(self, string, style): # write
		return self.s(style) + string + self.r()

	def s(self, args): # set
		a = ""
		for v in args:
			a += "%s;" % self.translate[str(v)]
		a = a[:-1] # Remove last ";"
		return self.base % "0" + self.base % a

