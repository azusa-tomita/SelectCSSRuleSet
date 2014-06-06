import sublime
import sublime_plugin

class select_css_rule_set(sublime_plugin.TextCommand):
	def run(self, edit):

		view = self.view
		sel = view.sel()[0]

		def find(key,dir="f"):
			val = ""
			i = 0
			if (dir == "f"):
				target = view.size()
			else:
				target = 0
			while val != key and target - (sel.begin() + i) != 0:
				if (dir == "f"):
					i += 1
				else:
					i -= 1
				val = view.substr( sel.begin() + i )
			else:
				if val == key:
					return sublime.Region(sel.begin() + i,sel.begin() + i)
				else:
					return sublime.Region(-1,-1)


		nearestOpCurly = find('{').end()
		nearestClCurly = find('}').end()
		if view.substr( sel.begin() - 1 ) == ";" and view.substr( sel.begin()) == "\n":
			nearestSColon  = find(';',"r").end()
		else:
			nearestSColon  = find(';').end()


		isSelector = False
		if nearestOpCurly < 0:
			if nearestClCurly < 0:
				isSelector = True
			else:
				isSelector = False
		else:
			if nearestClCurly < 0:
				isSelector = False
			else:
				if nearestClCurly < nearestOpCurly:
					isSelector = False
				else:
					if nearestSColon < 0:
						isSelector = True
					else:
						if nearestOpCurly < nearestSColon:
							isSelector = True
						else:
							isSelector = False


		if isSelector :
			view.sel().clear()
			view.sel().add(nearestOpCurly)

		if view.substr( sel.begin() ) == "(" or view.substr( sel.begin() - 1 ) == ")" or find("(","r") > find(")","r"):
			view.sel().clear()
			view.sel().add(find(":","r"))

		if view.substr( sel.begin() - 1 ) == "}" and view.substr( sel.begin()) == "\n":
			view.sel().clear()
			view.sel().add(sublime.Region(sel.begin()-1,sel.begin()-1))

		if nearestOpCurly < 0 and nearestClCurly < 0:
			view.sel().clear()
			view.sel().add(find("}","r"))



		view.run_command('expand_selection', {'to': 'brackets'})
		view.run_command('expand_selection', {'to': 'brackets'})
		cssBlock = view.sel()[0]

		str = ""
		i = 0
		while str != ";" and str != "{" and str != "}" and cssBlock.begin() - i > -1:
			i += 1
			str = view.substr( cssBlock.begin() - i )
		else:
			i -= 1
			while view.substr(cssBlock.begin() - i) == "\n":
				i -= 1
			else:
				ruleSetOp = cssBlock.begin() - i

		view.sel().clear()
		view.sel().add( sublime.Region(ruleSetOp,cssBlock.end()) )

