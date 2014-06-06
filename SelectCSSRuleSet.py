import sublime
import sublime_plugin

class select_css_rule_set(sublime_plugin.TextCommand):
	def run(self, edit):
		
		view = self.view
		sel = view.sel()[0]

		def find(key):
			res = view.find(key,sel.begin())
			if res:
				return res
			else:
				return sublime.Region(-1,-1)

		def rfind(key):
			val = ""
			i = 0
			while val != key and sel.begin() - i != 0:
				i += 1
				val = view.substr( sel.begin() - i )
			else:
				return sublime.Region(sel.begin() - i,sel.begin() - i)

		nearestOpCurly = find('\{').end()
		nearestClCurly = find('\}').end()
		if view.substr( sel.begin() - 1 ) == ";" and view.substr( sel.begin()) == "\n":
			nearestSColon  = rfind(';').end()
		else:
			nearestSColon  = find(';').end()

		currentStr = find('\}').end()


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

		if view.substr( sel.begin() ) == "(" or view.substr( sel.begin() - 1 ) == ")" or rfind("(") > rfind(")"):
			view.sel().clear()
			view.sel().add(rfind(":"))

		if view.substr( sel.begin() - 1 ) == "}" and view.substr( sel.begin()) == "\n":
			view.sel().clear()
			view.sel().add(sublime.Region(sel.begin()-1,sel.begin()-1))

		if nearestOpCurly < 0 and nearestClCurly < 0:
			view.sel().clear()
			view.sel().add(rfind("}"))


		view.run_command('expand_selection', {'to': 'brackets'})
		view.run_command('expand_selection', {'to': 'brackets'})
		cssBlock = view.sel()[0]
		cssBlockOp = cssBlock.begin()
		ruleSetCl = cssBlock.end()


		str = ""
		ruleSetOp = ""
		i = 0
		while str != ";" and str != "{" and str != "}" and cssBlockOp - i > -1:
			i += 1
			str = view.substr( cssBlockOp - i )
		else:
			i -= 1
			while view.substr(cssBlockOp - i) == "\n":
				i -= 1
			else:
				ruleSetOp = cssBlockOp - i

		view.sel().clear()
		view.sel().add(sublime.Region(ruleSetOp,ruleSetCl))

