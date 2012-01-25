import urllib, urllib.request, json, sys, os, tarfile

class aur(object):
	def __init__(self):
		self.cu = core_utils()
		self.curl = self.cu.curl
		self.ta = text_attributes()

		self.base_url = "http://aur.archlinux.org"
		self.com_url = "%s/rpc.php?type=%s&arg=%s" % (self.base_url, "%s", "%s")

		self.working_dir = "/tmp"

		self.search_arg = "search"

	def handle_start(self):
		todo, data = self.cu.parse_input(sys.argv)
		todo = "%s%s" % (todo, "      ")
		if todo[0] == "S":
			if todo[1] == "s":
				for d in data:
					self.show_search(self.search_pattern(d))
			if todo[1] == " ":
				for d in data:
					self.install_pattern(d)

	def search_pattern(self, pattern):
		x = self.curl(self.com_url % (self.search_arg, pattern) )
		return json.loads(x.decode("utf-8"))

	def install_pattern(self, pattern):
		self.cu.requires_root()
		print(self.ta.s(["bold","white"]) + "Download: " + self.ta.s(["blue"]) + pattern)
		x = self.curl(self.com_url % (self.search_arg, pattern) )
		x = json.loads(x.decode("utf-8"))
		n = "%s%s" % (x["results"][0]["Name"], ".tar.gz")
		dl = x["results"][0]["URLPath"] # First result fits best
		dl_url = "%s%s" % (self.base_url, dl)
		self.cu.download(dl_url, "%s/%s" % (self.working_dir, n))

		print(self.ta.s(["bold","white"]) + "Install: " + self.ta.s(["blue"]) + pattern)
		print(self.ta.s(["bold","white"]) + ">> Unpacking")
		if not tarfile.is_tarfile("%s/%s" % (self.working_dir, n)):
			print(self.ta.s(["red", "bold"]) + "Warning: " + self.ta.r() + "Did not find any tar-archive.")
			sys.exit()
		fd = tarfile.open("%s/%s" % (self.working_dir, n), 'r:gz')
		fd.extractall(path = self.working_dir)
		os.chdir(os.path.join(self.working_dir, pattern))
		os.system("ls")
		print(self.ta.s(["bold","white"]) + ">> Building package")
		#os.system("makepkg -s")

	def show_search(self, dd):
		items = dd["results"]
		for item in items:
			name = item["Name"]
			version = item["Version"]
			desc = item["Description"]
			print(self.ta.s(["blue", "bold"]) + name + " " + self.ta.s(["green"]) + "(" + version +")")


class core_utils(object):
	def __init__(self):
		self.ta = text_attributes()

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

	def requires_root(self):
		if os.geteuid() != 0:
			print(self.ta.s(["red", "bold"]) + "Warning: " + self.ta.r() + "This operation requires root access.")
			sys.exit()

	def parse_input(self, inp):
		if len(inp) == 1:
			print("Exiting with no arguments given...")
			sys.exit()
		do = sys.argv[1]
		if do[0] != "-":
			print("First argument has to define action[s]")
			sys.exit()
		do = do[1:]
		# "do" contains what to do, e.g. "S", "Ss", ...
		return do, sys.argv[2:]

class text_attributes(object):
	def __init__(self):
		self.base = '\033[%sm'

		self.translate = {
			# Styles
			"normal":0,
			"bold":1,
			# Colors
			"red":31,
			"blue":34,
			"green":32,
			"white":37,
		}

	def r(self):
		return self.base % "0"

	def s(self, args):
		a = ""
		for v in args:
			a += "%s;" % self.translate[str(v)]
		a = a[:-1] # Remove last ";"
		return self.base % "0" + self.base % a

aur().handle_start()
