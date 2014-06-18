import sublime
import sublime_plugin

class select_css_rule_set(sublime_plugin.TextCommand):
  def run(self, edit):
    view = self.view

    # find except the comment of CSS and SCSS
    def findStr(key, point = view.sel()[0].begin(), dir = "f"):
      keyLength = len(key)
      target = val = lineVal = ""
      cmtSCSSPos = cmtCSSPosS = cmtCSSPosE =  -1
      isCmtCSS = isCmtSCSS = False
      i = j = 0
      bfLines = view.split_by_newlines(sublime.Region(0, point + 1))
      currLineNum = len(bfLines) - 1

      if view.substr(bfLines[currLineNum]).find("//") >= 0:
        isCmtSCSS = True
        cmtSCSSPos = view.substr(bfLines[currLineNum]).find("//")

      j = currLineNum
      while j >= 0:
        val = view.substr(bfLines[j])
        if cmtCSSPosS != -1 and cmtCSSPosE != -1:
          break
        else:
          _s = val.rfind("/*")
          _e = val.rfind("*/")
          if cmtCSSPosS == -1 and _s != -1:
            cmtCSSPosS = bfLines[j].begin() + _s
          if cmtCSSPosE == -1 and _e != -1:
            cmtCSSPosE = bfLines[j].begin() + _e + 1
          j = j - 1
      if cmtCSSPosE < cmtCSSPosS:
        isCmtCSS = True

      if dir == "f":
        while view.size() - (point + i) != 0:
          val = view.substr(sublime.Region(point + i, point + i + keyLength))

          if val[0] == "/":
            if view.substr(point + i + 1) == "*":
              isCmtCSS = True
            if view.substr(point + i - 1) == "*":
              isCmtCSS = False

          if val[0] == "/":
            if view.substr(point + i + 1) == "/":
              isCmtSCSS = True

          if val[0] == "\n":
            if isCmtSCSS == True:
              isCmtSCSS = False

          if isCmtCSS == False and isCmtSCSS == False:
            if key == val:
              target = sublime.Region(point + i, point + i + keyLength)
              break
          i = i + 1
        else:
          target = sublime.Region(-1, -1)

      else:
        j = currLineNum
        while j >= 0:
          lineValS = bfLines[j].begin()
          lineValE = bfLines[j].end() - 1
          lineVal = view.substr(bfLines[j])

          if j == currLineNum:
            if isCmtSCSS == True:
              lineVal = view.substr(sublime.Region(lineValS, lineValS + cmtSCSSPos))
            else:
              lineVal = view.substr(sublime.Region(bfLines[j].begin(), point))
          else:
            cmtSCSSPos = lineVal.find("//")
            if cmtSCSSPos != -1:
              lineVal = view.substr(sublime.Region(lineValS, lineValS + cmtSCSSPos))

          i = 0
          while len(lineVal) - keyLength >= i:
            valE = len(lineVal) - i
            valS = valE - keyLength
            val = lineVal[valS:valE]

            sl = val.rfind("/")
            if sl != -1:
              if view.substr(lineValS + valS + sl - 1) == "*":
                isCmtCSS = True
              if view.substr(lineValS + valS + sl + 1) == "*":
                isCmtCSS = False

            if isCmtCSS == False and isCmtSCSS == False:
              if key == val:
                target = sublime.Region(lineValS + valS, lineValS + valE)
                break

            i = i + 1

          if target != "":
            break
          j = j - 1
        else:
          target = sublime.Region(-1, -1)
      return target


    sel = view.sel()[0]
    selS = sel.begin()

    # Adjustment of the cursor position for expand_selection
    nearestLCurly = findStr('{', point = selS).begin()
    nearestRCurly = findStr('}', point = selS).begin()
    nearestSColon = findStr(';', point = selS).begin()
    if view.substr(selS - 1) == ";" and view.substr(selS) == "\n":
      nearestSColon  = findStr(';', point = selS, dir = "r").begin()

    isSelector = False
    if nearestLCurly < 0:
      if nearestRCurly < 0:
        isSelector = True
      else:
        isSelector = False
    else:
      if nearestRCurly < 0:
        isSelector = False
      else:
        if nearestRCurly < nearestLCurly:
          isSelector = False
        else:
          if nearestSColon < 0:
            isSelector = True
          else:
            if nearestLCurly < nearestSColon:
              isSelector = True
            else:
              isSelector = False

    ## if selector
    if isSelector :
      view.sel().clear()
      view.sel().add(nearestLCurly)

    ## If there is a cursor just after {} and the back of the cursor was a newline
    if ((view.substr(selS - 1) == "}" or view.substr(selS - 1) == "{" ) and
        view.substr(selS) == "\n"):
      view.sel().clear()
      view.sel().add(sublime.Region(selS - 1, selS - 1))

    ## If there is a cursor inside of ()
    if (view.substr(selS) == "(" or                         # hoge:|(foo);
        view.substr(selS - 1) == ")" or                     # hoge:(foo)|;
        findStr(")", dir = "r") < findStr("(", dir = "r")   # hoge:(fo|o);
        ):
      view.sel().clear()
      view.sel().add(findStr(":", dir = "r").begin())

    ## If there is not a rule set after a cursor
    if nearestLCurly < 0 and nearestRCurly < 0:
      view.sel().clear()
      view.sel().add(findStr("}", dir = "r"))


    # The acquisition of css block
    view.run_command('expand_selection', {'to': 'brackets'})
    view.run_command('expand_selection', {'to': 'brackets'})
    cssBlock = view.sel()[0]


    # The acquisition of css rule set
    ruleSetPosE = cssBlock.end()

    rNearestLCurly = findStr('{', point = cssBlock.begin() - 1, dir = "r").end() 
    rNearestRCurly = findStr('}', point = cssBlock.begin() - 1, dir = "r").end()
    rNearestSColon = findStr(';', point = cssBlock.begin() - 1, dir = "r").end()
    ruleSetPosS = max(rNearestLCurly, rNearestRCurly, rNearestSColon)
    if ruleSetPosS == -1:
      ruleSetPosS = 0

    i = ruleSetPosS
    isCmtCSS = isCmtSCSS = False
    while i < cssBlock.begin():
      if isCmtCSS == True or isCmtSCSS == True:
        if isCmtCSS == True and view.substr(i) == "*" and view.substr(i + 1) == "/":
          isCmtCSS = False
          i = i + 1
        elif isCmtSCSS == True and view.substr(i) == "\n":
          isCmtSCSS = False
      elif view.substr(i) == "/" and view.substr(i + 1) == "*":
        isCmtCSS = True
      elif view.substr(i) == "/" and view.substr(i + 1) == "/":
        isCmtSCSS = True
      elif (view.substr(i) == "\n" or view.substr(i) == "\t" or view.substr(i) == " "):
        pass
      else:
        break
      i = i + 1
    ruleSetPosS = i

    view.sel().clear()
    view.sel().add(sublime.Region(ruleSetPosS, ruleSetPosE))
