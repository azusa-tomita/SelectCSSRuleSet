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
			str = ""
			i = 0
			while str != key and i != view.size():
				i += 1
				str = view.substr( sel.begin() - i )
				print(i)
			else:
				return sublime.Region(sel.begin() - i,sel.begin() - i)

		nCurlyS = find('\{').end()
		nCurlyE = find('\}').end()
		nColon  = find(':').end()
		nSColon = find(';').end()


		if nCurlyS < 0 and nCurlyE < 0:
			bfCurlyE = rfind("}")
			view.sel().clear()
			view.sel().add(bfCurlyE)

		elif view.substr( sel.begin() - 1 ) == "}" and view.substr( sel.begin()) == "\n":
			view.sel().clear()
			view.sel().add(sublime.Region(sel.begin()-1,sel.begin()-1))

		elif (0 < nCurlyS and nCurlyS < nCurlyE) and ( ( nCurlyS < nColon and nCurlyS < nSColon ) or ( nColon < 0 and nSColon < 0 ) ):
				view.sel().clear()
				view.sel().add(sublime.Region(nCurlyS,nCurlyS))
		else:
			bfParenthesisS = rfind("(")
			bfColon = rfind(":")
			if bfColon < bfParenthesisS:
				view.sel().clear()
				view.sel().add(bfColon)

		view.run_command('expand_selection', {'to': 'brackets'})
		view.run_command('expand_selection', {'to': 'brackets'})
		cssBlock = view.sel()[0]
		cssBlockS = cssBlock.begin()
		ruleSetE = cssBlock.end()

		str = ""
		ruleSetS = ""
		i = 0
		while str != ";" and str != "{" and str != "}" and cssBlockS - i > -1:
			i += 1
			str = view.substr( cssBlockS - i )
		else:
			i -= 1
			while view.substr(cssBlockS - i) == "\n":
				i -= 1
			else:
				ruleSetS = cssBlockS - i

		view.sel().clear()
		view.sel().add(sublime.Region(ruleSetS,ruleSetE))

