import sublime
import sublime_plugin

class select_css_rule_set(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view

		def findStr(key, point = view.sel()[0].begin(),dir="f"):
			keyLength = len(key)
			res = val = lineVal = ""
			isCSSComment = isSassComment = False
			i = j = sass = cssOp = cssCl =  0
			beforeLine = view.split_by_newlines ( sublime.Region(0,point) )
			currentLine = len(beforeLine) - 1

			if view.substr( beforeLine[currentLine] ).find("//") > 0:
				isSassComment = True
				sass = view.substr( beforeLine[currentLine] ).find("//")

			j = currentLine
			while j >= 0:
				val = view.substr( beforeLine[j] )
				if cssOp and cssCl:
					break
				else:
					if cssOp == 0 and val.rfind("/*") != -1:
						cssOp = beforeLine[j].begin() + val.rfind("/*")
					if cssCl == 0 and val.rfind("*/") != -1:
						cssCl = beforeLine[j].begin() + val.rfind("*/") + 1
					j = j - 1

			if cssCl < cssOp:
				isCSSComment = True

			if dir == "f":
				while view.size() - (point + i) != 0:
					val = view.substr( sublime.Region( point + i,point + i + keyLength) )

					if val[0] == "/":
						if view.substr(point + i + 1) == "*":
							isCSSComment = True
						if view.substr(point + i - 1) == "*":
							isCSSComment = False

					if val[0] == "/":
						if view.substr(point + i + 1) == "/":
							isSassComment = True

					if val[0] == "\n":
						if isSassComment == True:
							isSassComment = False

					if isCSSComment == False and isSassComment == False:
						if key == val:
							res = sublime.Region( point + i,point + i + keyLength)
							break
					i = i + 1
				else:
					res = sublime.Region( -1,-1)

			else:
				j = currentLine
				while j >= 0:
					lineValS = beforeLine[j].begin()
					lineValE = beforeLine[j].end()-1
					lineVal = view.substr( beforeLine[j] )

					if j == currentLine:
						lineVal = view.substr( sublime.Region(beforeLine[j].begin(),point) )

						if isSassComment == True:
							lineVal = view.substr( sublime.Region(lineValS,lineValS + sass) )
					else:
						sass = lineVal.find("//")
						if sass != -1:
							lineVal = view.substr( sublime.Region(lineValS,lineValS + sass) )

					i = 0
					while len(lineVal)-keyLength >= i:
						valE = len(lineVal)-i
						valS = valE - keyLength
						val = lineVal[valS:valE]

						sl = val.rfind("/")
						if sl != -1:
							if view.substr(lineValS + valS + sl -1) == "*":
								isCSSComment = True
							if view.substr(lineValS + valS + sl +1) == "*":
								isCSSComment = False

						if isCSSComment == False and isSassComment == False:
							if key == val:
								res = sublime.Region( lineValS + valS,lineValS + valE)
								break

						i = i + 1

					if res !="":
						break
					j = j - 1
				else:
					res = sublime.Region( -1,-1)
			return res

		sel = view.sel()[0]
		nearestOpCurly = findStr('{',point = sel.begin()).begin()
		nearestClCurly = findStr('}',point = sel.begin()).begin()
		nearestSColon  = findStr(';',point = sel.begin()).begin()
		if view.substr( sel.begin() - 1 ) == ";" and view.substr( sel.begin()) == "\n":
			nearestSColon  = findStr(';',point = sel.begin(),dir="r").begin()

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

		if (view.substr( sel.begin() - 1 ) == "}" or view.substr( sel.begin() - 1 ) == "{") and view.substr( sel.begin()) == "\n":
			view.sel().clear()
			view.sel().add(sublime.Region(sel.begin()-1,sel.begin()-1))

		if view.substr( sel.begin() ) == "(" or view.substr( sel.begin() - 1 ) == ")" or findStr("(",dir="r") > findStr(")",dir="r"):
			view.sel().clear()
			view.sel().add(max(findStr("{",dir="r").begin(),findStr("}",dir="r").begin()))

		if nearestOpCurly < 0 and nearestClCurly < 0:
			view.sel().clear()
			view.sel().add(findStr("}",dir="r"))

		view.run_command('expand_selection', {'to': 'brackets'})
		view.run_command('expand_selection', {'to': 'brackets'})
		cssBlock = view.sel()[0]


		fNearestOpCurly = findStr('{',point = cssBlock.begin()-1,dir="r").end() 
		fNearestClCurly = findStr('}',point = cssBlock.begin()-1,dir="r").end()
		fNearestSColon  = findStr(';',point = cssBlock.begin()-1,dir="r").end()

		ruleSetOp = max(fNearestOpCurly, fNearestClCurly, fNearestSColon)

		i = ruleSetOp
		isCSSComment = isSassComment = False
		while i < cssBlock.begin():
			if isCSSComment == True or isSassComment == True:
				if isCSSComment == True and view.substr(i) == "*" and view.substr(i + 1) == "/":
					isCSSComment = False
					i = i + 1
				elif isSassComment == True and view.substr(i) == "\n":
					isSassComment = False
			elif view.substr(i) == "/" and view.substr(i + 1) == "*":
				isCSSComment = True
			elif view.substr(i) == "/" and view.substr(i + 1) == "/":
				isSassComment = True
			elif (view.substr(i) == "\n" or
						view.substr(i) == "\t" or
						view.substr(i) == " "
					):
				pass
			else:
				break
			i = i + 1
		ruleSetOp = i

		view.sel().clear()
		view.sel().add( sublime.Region(ruleSetOp,cssBlock.end()) )
