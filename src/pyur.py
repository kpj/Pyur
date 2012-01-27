#!/usr/bin/python
import json, sys, os, tarfile, subprocess, argparse # stdlibs
import utils # own libs

class aur(object):
	def __init__(self):
		self.cu = utils.core_utils()
		self.curl = self.cu.curl
		self.ta = utils.text_attributes()
		self.prog = prog_itself()

		self.base_url = "http://aur.archlinux.org"
		self.com_url = "%s/rpc.php?type=%s&arg=%s" % (self.base_url, "%s", "%s")

		self.working_dir = "/tmp/%s-%s" % (self.prog.app_name, self.prog.app_version)
		self.check_working_dir()

		self.search_arg = "search"
		self.info_arg = "info"

		self.additional_pacman_args = ""

		self.get_aur_pkg = ["pacman", "-Qm"]

	def handle_start(self):
		todo, data = self.cu.parse_input(sys.argv)
		todo = "%s%s" % (todo, "      ")
		if todo[0] == "S":
			if todo[1] == "s":
				for d in data:
					self.show_search(self.search_pattern(d))
			elif todo[1] == "i":
				for d in data:
					self.show_info(self.info_pattern(d))
			elif todo[1] == " ":
				for d in data:
					self.install_pattern(d)
			elif todo[1] == "y":
				self.upgrade_all()

	def check_working_dir(self):
		try:
			os.mkdir(self.working_dir)
		except OSError:
			pass

	def handle_start2(self):
		parser = argparse.ArgumentParser(
			description='This tool is designed to cope with all aur-packets.', 
			epilog="Bugreports to googlemail.com@kpjkpjkpjkpjkpjkpj (use your brain) Any copyrights (just in case) go to kpj Licenses: <insert cool open-source licenses here, e.g. GPL>"
		)

		parser.add_argument(
			'-S', 
			action="store", 
			nargs="?", 
			default=False, 
			const=True,
			help="Access online mode / Install application", 
			metavar="name"
		)
		parser.add_argument(
			'-i', 
			action="append", 
			nargs='+', 
			help="Get information about apps", 
			metavar="name"
		)
		parser.add_argument(
			'-s',
			action="store", 
			nargs=1, 
			help="Search for an app", 
			metavar="name"
		)
		parser.add_argument(
			'-y',
			action="store_true",
			default=False,
			help="Update all aur-related packets"
		)
		parser.add_argument(
			'--noconfirm',
			action="store_true",
			default=False,
			help="Do not ask for any permissions"
		)

		args = parser.parse_args()
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
					print("And now?")
				else:
					self.install_pattern(args.S)
		else:
			self.cu.print_warning("No mode defined")

		if args.noconfirm:
			self.additional_pacman_args += "--noconfirm "

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
		length = len(l)
		num = 1
		for e in l:
			if e != "":
				name = e.split(" ")[0]
				version = e.split(" ")[1]

				to_print = "Checking " + name
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
					needs_update.append(name)
		print("" ,end="\n")
		lnu = len(needs_update)
		lwe = len(was_error)
		print(
			self.ta.w("%i" % (length - (lnu + lwe)), ["green"]) + 
			" up-to-date / " +
			self.ta.w("%i" % lwe, ["red"]) +
			" errors / " +
			self.ta.w("%i" % lnu, ["blue"]) +
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
		return items[0]["Version"]

	def info_pattern(self, pattern):
		x = self.curl(self.com_url % (self.info_arg, pattern) )
		x = json.loads(x.decode("utf-8"))
		if self.corrupted_response(x):
			sys.exit()
		return x

	def install_pattern(self, pattern):
		#self.cu.requires_root()
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
		n = "%s%s" % (x["results"][0]["Name"], ".tar.gz")
		dl = x["results"][0]["URLPath"] # First result fits best
		dl_url = "%s%s" % (self.base_url, dl)
		self.cu.download(dl_url, "%s/%s" % (self.working_dir, n))

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
		if not os.system("makepkg -fs"):
			print(self.ta.s(["bold","white"]) + ">> Successfully built")
		else:
			self.cu.print_warning("Error while building")
		print(self.ta.r())
		pkg_name = (name + 
			"-" + 
			x["results"][0]["Version"] + 
			"-" + 
			os.uname()[-1] + 
			".pkg.tar.xz")
		if not os.system("sudo pacman -U %s %s" % (pkg_name, self.additional_pacman_args)):
			print(self.ta.s(["bold","white"]) + ">> Successfully installed")
		else:
			if not os.system("sudo pacman -U %s %s" % ("%s*pkg.tar*" % name, self.additional_pacman_args)):
				print(self.ta.s(["bold","white"]) + ">> Successfully installed")
			else:
				self.cu.print_warning("Error while installing")
		print(self.ta.r())

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
		self.app_version="0.2.3"

aur().handle_start2()
