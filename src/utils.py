import urllib, urllib.request

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
			urllib.request.urlretrieve(url, f)
		except ContentTooShortError:
			print("There was an error when saving your file...")
			sys.exit()

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

