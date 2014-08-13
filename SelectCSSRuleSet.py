import sublime
import sublime_plugin

class select_css_rule_set(sublime_plugin.TextCommand):

  def run(self, edit):
    view = self.view

    # CSS/SCSSのコメント内を対象外で検索
    def findStr(key, point = view.sel()[0].begin(), dir = "f"):
      keyLength = len(key)
      target = val = lineVal = ""
      cmtSCSSPos = cmtCSSPosS = cmtCSSPosE =  -1
      isCmtCSS = isCmtSCSS = False
      i = j = 0
      bfLines = view.split_by_newlines(sublime.Region(0, point + 1))
      currLineNum = len(bfLines) - 1

      # pointがSCSSコメント内にあるか
      if view.substr(bfLines[currLineNum]).find("//") >= 0:
        cmtSCSSPos = view.substr(bfLines[currLineNum]).find("//")
        isCmtSCSS = True

      # pointがCSSコメント内にあるか
      i = currLineNum
      while i >= 0:
        val = view.substr(bfLines[i])
        if cmtCSSPosS != -1 and cmtCSSPosE != -1:
          break
        else:
          _s = val.rfind("/*")
          _e = val.rfind("*/")
          if cmtCSSPosS == -1 and _s != -1:
            cmtCSSPosS = bfLines[i].begin() + _s
          if cmtCSSPosE == -1 and _e != -1:
            cmtCSSPosE = bfLines[i].begin() + _e + 1
          i -= 1
      if cmtCSSPosE < cmtCSSPosS:
        isCmtCSS = True

      if dir == "f":
        i = 0
        while view.size() - (point + i) != 0:
          _v = point + i
          val = view.substr(_v)
          if point > 0 and len(val) > 0:
            if val[0] == "/":
              if view.substr(_v + 1) == "*":
                isCmtCSS = True
              if view.substr(_v - 1) == "*":
                isCmtCSS = False

            if val[0] == "/":
              if view.substr(_v + 1) == "/":
                isCmtSCSS = True

            if val[0] == "\n":
              if isCmtSCSS == True:
                isCmtSCSS = False

          if isCmtCSS == False and isCmtSCSS == False:
            if key == val:
              target = sublime.Region(_v, _v + 1)
              break
          i += 1
        else:
          target = sublime.Region(-1, -1)

      else:
        i = currLineNum
        while i >= 0:
          lineValS = bfLines[i].begin()
          lineVal = view.substr(bfLines[i])

          if i == currLineNum:
            if isCmtSCSS == False:
              lineVal = view.substr(sublime.Region(bfLines[i].begin(), point))
            else:
              lineVal = view.substr(sublime.Region(lineValS, lineValS + cmtSCSSPos))
          else:
            cmtSCSSPos = lineVal.find("//")
            if cmtSCSSPos != -1:
              lineVal = view.substr(sublime.Region(lineValS, lineValS + cmtSCSSPos))


          j = 1
          while len(lineVal) >= j:
            val = lineVal[-j]
            _v = lineValS + len(lineVal) - j

            if val == "/":
              if view.substr(_v - 1) == "*":
                isCmtCSS = True
              if view.substr(_v + 1) == "*":
                isCmtCSS = False

            if isCmtCSS == False:
              if key == val:
                target = sublime.Region(_v, _v + 1)
                break
            j += 1

          if target != "":
            break

          isCmtSCSS = False
          i -= 1

        else:
          target = sublime.Region(-1, -1)
      return target

    try:
      sel = view.sel()[0]
      selS = sel.begin()

      # インターポレーション内にカーソルがある場合、外側に移動
      _f1 = findStr('{', point = selS, dir = "r")
      _f2 = findStr('}', point = selS, dir = "r")
      if view.substr(_f1.begin() - 1) == "#":
        if _f1.begin() > _f2.begin():
          view.sel().clear()
          view.sel().add(_f1.begin() - 1)
      selS = view.sel()[0].begin()

      # セレクタ位置にある場合は{}の内側に、
      # それ以外は;または}に移動
      _f3 = findStr(';', point = selS)

      _f4 = findStr('{', point = selS)
      while view.substr(_f4.begin() - 1) == "#":
        _f4 = findStr('{', point = _f4.begin() + 1)

      _f5 = findStr('}', point = selS)
      _tmp = findStr('{', point = selS)
      if view.substr(_tmp.begin() - 1) == "#":
        while _tmp.begin() < _f5.begin():
          _tmp = findStr('{', point = _f5.begin() )
          _f5 = findStr('}', point = _f5.begin() + 1 )

      pos = min(_f3.begin(),_f4.begin(),_f5.begin())
      if pos != -1:
        if pos == _f4.begin():
          pos = pos + 1
        view.sel().clear()
        view.sel().add(pos)

      # 宣言ブロック選択
      view.run_command('expand_selection', {'to': 'brackets'})
      view.run_command('expand_selection', {'to': 'brackets'})

      # (....)|; など、括弧の直後にカーソルがある場合、expand_selectionが直前の括弧に奪われるため、
      # 選択範囲の始点が"{"でない場合はもう一度expand_selectionを実行
      _tpl = view.sel()[0].begin()
      if view.substr(_tpl) != "{":
        view.run_command('expand_selection', {'to': 'brackets'})
      else:
        ## 選択範囲の始点が"{"の場合でも、インターポレーションの場合同様にexpand_selectionが奪われるため、再度実行
        if view.substr(_tpl - 1) == "#":
          _old = view.sel()[0]
          view.run_command('expand_selection', {'to': 'brackets'})
          _new = view.sel()[0]
          ## グローバルの変数宣言で#{}を使っている場合、expand_selectionで選択されてしまうため、解除
          if _old == _new:
            view.sel().clear()
            view.sel().add(pos)
      cssBlock = view.sel()[0]
      

      # 選択範囲をルールセットに拡張
      ruleSetPosE = cssBlock.end()
      ## グローバルの変数宣言では、;も選択範囲に含める
      if view.substr(ruleSetPosE) == ";":
        ruleSetPosE = ruleSetPosE + 1

      rNearestSColon = findStr(';', point = cssBlock.begin() - 1, dir = "r").end()
      rNearestLCurly = findStr('{', point = cssBlock.begin() - 1, dir = "r").end() 
      rNearestRCurly = findStr('}', point = cssBlock.begin() - 1, dir = "r").end()

      # 前方にインターポレーションがある場合、それ無視してその前の{}を探す
      if view.substr(rNearestLCurly - 2) == "#":
        _tpl = findStr('}', point = rNearestLCurly - 2,).end()
        if _tpl >= rNearestRCurly:
          while view.substr(rNearestLCurly - 2) == "#":
            rNearestRCurly = findStr('}', point = rNearestLCurly - 1, dir = "r").end()
            rNearestLCurly = findStr('{', point = rNearestLCurly - 1, dir = "r").end()

      ruleSetPosS = max(rNearestLCurly, rNearestRCurly, rNearestSColon)

      # 前方のコメント、行頭改行は無視する
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
        elif view.substr(i) == "\n" or view.substr(i) == "\t" or view.substr(i) == " ":
          pass
        else:
          break
        i = i + 1
      ruleSetPosS = i

      if ruleSetPosE > 0:
        view.sel().clear()
        view.sel().add(sublime.Region(ruleSetPosS, ruleSetPosE))
    except:
      pass
