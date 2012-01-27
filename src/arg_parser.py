import argparse

def setup_argparser():
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
	return parser.parse_args()
