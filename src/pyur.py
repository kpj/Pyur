#!/usr/bin/python
import json, sys, os, tarfile, subprocess # stdlibs
import utils, arg_parser # own libs

class aur(object):
	def __init__(self):
		self.cu = utils.core_utils()
		self.curl = self.cu.curl
		self.ta = utils.text_attributes()
		self.prog = prog_itself()
		self.fo = utils.file_operations()

		self.base_url = "http://aur.archlinux.org"
		self.com_url = "%s/rpc.php?type=%s&arg=%s" % (self.base_url, "%s", "%s")

		self.working_dir = "/tmp/%s-%s" % (self.prog.app_name, self.prog.app_version)
		self.check_working_dir()

		self.search_arg = "search"
		self.info_arg = "info"

		self.additional_pacman_args = ""

		self.get_aur_pkg = ["pacman", "-Qm"]

	def check_working_dir(self):
		try:
			os.mkdir(self.working_dir)
		except OSError:
			pass

	def handle_more(self):
		self.config = self.fo.parse_config()

	def handle_start(self):
		self.handle_more()
		args = arg_parser.setup_argparser()
		if args.S:
			if args.i:
				for n in args.i:
					self.show_info(self.info_pattern(n[0]))
			elif args.s:
				self.show_search(self.search_pattern(args.s[0]))
			elif args.y:
				self.upgrade_all()
			else:
				if args.S == True:
					print("Append a name or option")
				else:
					self.install_pattern(args.S)
		elif args.R:
			for n in args.R:
				self.delete_pattern(n)
		else:
			self.cu.print_warning("No mode defined")
		if args.noconfirm:
			self.additional_pacman_args += "--noconfirm "

	def delete_pattern(self, pattern):
		self.cu.requires_root()
		os.system("pacman -R %s" % pattern)

	def search_pattern(self, pattern):
		x = self.curl(self.com_url % (self.search_arg, pattern) )
		x = json.loads(x.decode("utf-8"))
		if self.corrupted_response(x):
			sys.exit()
		return x

	def upgrade_all(self):
		print(self.ta.w("Identifying AUR-packages", ["white","bold"]))
		l = subprocess.check_output(self.get_aur_pkg).decode("utf-8").split('\n')
		needs_update = []
		was_error = []
		just_not = []
		length = len(l)
		num = 1
		for e in l:
			if e != "":
				name = e.split(" ")[0]
				version = e.split(" ")[1]

				to_print = "Checking: " + name
				spacer = " " * (40 - len(to_print))
				info = "[%i/%i]" % (num, length)
				bar = self.cu.gen_bar(num, length)
				back = "\r" * len(to_print)
				print(to_print + spacer + info + bar + back, end="")
				num += 1
				online_version = self.get_version(name)
				if online_version == "kpjkpjkpj":
					was_error.append(name)
					continue
				if not online_version == version:
					if not name in self.config["ignore_pkg"]:
						needs_update.append(name)
					else:
						just_not.append(name)
		print("" ,end="\n")
		lnu = len(needs_update)
		lwe = len(was_error)
		ljn = len(just_not)
		print(
			self.ta.w("%i" % (length - (lnu + lwe + ljn)), ["green", "bold"]) + 
			" up-to-date / " +
			self.ta.w("%i" % lwe, ["red", "bold"]) +
			" errors / " +
			self.ta.w("%i" % ljn, ["violet", "bold"]) +
			" excluded / " +
			self.ta.w("%i" % lnu, ["blue", "bold"]) +
			" updates"
		)
		print("Installing updates")
		for n in needs_update:
			self.install_pattern(n)

	def get_version(self, pattern):
		x = self.curl(self.com_url % (self.search_arg, pattern) )
		x = json.loads(x.decode("utf-8"))
		if x["type"] == "error":
			return "kpjkpjkpj"
		items = x["results"]
		if len(items) != 1:
			if items[0]["Name"] != pattern:
				# No distinct packet defined
				for i in items:
					if i["Name"] == pattern:
						return i["Version"]
					else:
						return "kpjkpjkpj"
		return items[0]["Version"]

	def info_pattern(self, pattern):
		x = self.curl(self.com_url % (self.info_arg, pattern) )
		x = json.loads(x.decode("utf-8"))
		if self.corrupted_response(x):
			sys.exit()
		return x

	def install_pattern(self, pattern):
		print(
			self.ta.s(["bold","white"]) + 
			"Download: " + 
			self.ta.s(["blue"]) + 
			pattern
		)
		x = self.curl(self.com_url % (self.search_arg, pattern) )
		x = json.loads(x.decode("utf-8"))
		if self.corrupted_response(x):
			sys.exit()
		name = x["results"][0]["Name"]
		got_it = False
		if len(x["results"]) > 1:
			for u in x["results"]:
				if u["Name"] == pattern:
					name = u["Name"]
					dl = u["URLPath"]
					got_it = True
			if not got_it:
				self.cu.print_warning("Specify your search pattern")
				sys.exit()
		else:
			name = x["results"][0]["Name"]
			dl = x["results"][0]["URLPath"]
		n = "%s%s" % (name, ".tar.gz")
		dl_url = "%s%s" % (self.base_url, dl)
		if self.cu.download(dl_url, "%s/%s" % (self.working_dir, n)):

			print(
				self.ta.s(["bold","white"]) + 
				"Install: " + 
				self.ta.s(["blue"]) + 
				name
			)
			print(self.ta.s(["bold","white"]) + ">> Unpacking")
			if not tarfile.is_tarfile("%s/%s" % (self.working_dir, n)):
				self.cu.print_warning("Did not find any tar-archive")
				sys.exit()
			fd = tarfile.open("%s/%s" % (self.working_dir, n), 'r:gz')
			fd.extractall(path = self.working_dir)
			os.chdir(os.path.join(self.working_dir, name))
			print(self.ta.s(["bold","white"]) + ">> Building package")
			if not os.system("makepkg -fs -i"):
				print(self.ta.s(["bold","white"]) + ">> Successfully built and installed")
			else:
				self.cu.print_warning("Error while building or installing")

	def show_search(self, dd):
		items = dd["results"]
		for item in items:
			name = item["Name"]
			version = item["Version"]
			desc = item["Description"]
			print(
				self.ta.s(["blue", "bold"]) + 
				name + 
				" " + 
				self.ta.s(["green"]) + 
				"(" + 
				version +
				")"
			)

	def show_info(self, dd):
		item = dd["results"]
		name = item["Name"]
		version = item["Version"]
		desc = item["Description"]
		url = item["URL"]
		license = item["License"]
		maintainer = item["Maintainer"]
		print("Name: %s" % name)
		print("Version: %s" % version)
		print("URL: %s" % url)
		print("License: %s" % license)
		print("Maintainer: %s" % maintainer)
		print("Description: %s" % desc)

	def corrupted_response(self, data):
		if data["type"] == "error":
			self.cu.print_warning("Did not find any corresponding entries (%s)" % data["results"])
			return True
		return False


class prog_itself(object):
	def __init__(self):
		self.app_name="Pyur"
		self.app_version="0.2.4"

aur().handle_start()
