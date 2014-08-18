import sublime
import sublime_plugin

class select_css_rule_set(sublime_plugin.TextCommand):
  try:
    def run(self, edit):
      view = self.view

      # CSS/SCSSのコメント内を除外して検索
      def findStr(key, start = view.sel()[0].begin(), dir = "f"):

        ## 現在位置がコメント内かどうかと、現在行までの情報を取得
        def checkCurtLine():
          _bfLines = view.split_by_newlines(sublime.Region(0, start + 1))
          _curtLineNum = len(_bfLines) - 1
          def _scss():
            return view.substr(_bfLines[_curtLineNum]).find("//")

          def _css():
            i = _curtLineNum
            _posS = _posE = -1;
            while i >= 0:
              _v = view.substr(_bfLines[i])
              _cmtS = _v.rfind("/*")
              _cmtE = _v.rfind("*/")
              if _posS == -1 and _cmtS != -1:
                _posS = _bfLines[i].begin() + _cmtS

              if _posE == -1 and _cmtE != -1:
                _posE = _bfLines[i].begin() + _cmtE + 1

              if _posS != -1 and _posE != -1:
                break
              i -= 1
            return _posS,_posE

          class _res(object):
            beforeTextRegions = _bfLines
            lineNum = _curtLineNum
            class scss():
              cmtStartPos = _scss()
              cmtEndPos = _bfLines[_curtLineNum].end if cmtStartPos != -1 else -1
              isCmt = True if cmtStartPos != -1 else False
            class css():
              cmtStartPos = _css()[0]
              cmtEndPos = _css()[1]
              isCmt = True if cmtStartPos > cmtEndPos else False
          return _res

        def findForward(curt):
          i = 0
          _res = ""
          _css = curt.css.isCmt
          _scss = curt.scss.isCmt
          while view.size() - (start + i) != 0:
            _p = start + i
            _target = view.substr(_p)

            if _target == "/":
              _css = True if view.substr(_p + 1) == "*" else _css
              _css = False if view.substr(_p - 1) == "*" else _css
              _scss = True if view.substr(_p + 1) == "/" else _scss
            elif _target == "\n":
              _scss = False if _scss == True else False

            if _css == False and _scss == False and _target == key:
              _res = sublime.Region(_p, _p + 1)
              break
            i += 1
          else:
            _res = sublime.Region(-1, -1)
          return _res

        def findReverse(curt):
          _bf = curt.beforeTextRegions
          _n = curt.lineNum
          _css = curt.css.isCmt
          _scss = curt.scss.isCmt
          _scssP = curt.scss.cmtStartPos
          i = _n
          _res = ""
          while i >= 0:
            _linePosS = _bf[i].begin()
            _lineStr = view.substr(_bf[i])

            if i == _n:
              if _scss == False:
                _lineStr = view.substr(sublime.Region(_linePosS, start))
              else:
                _lineStr = view.substr(sublime.Region(_linePosS, _linePosS + _scssP))
            else:
              _scssP = _lineStr.find("//")
              if _scssP != -1:
                _lineStr = view.substr(sublime.Region(_linePosS, _linePosS + _scssP))

            j = 1
            while len(_lineStr) >= j:
              _target = _lineStr[-j]
              _p = _linePosS + len(_lineStr) - j

              if _target == "/":
                _css = True if view.substr(_p - 1) == "*" else _css
                _css = False if view.substr(_p + 1) == "*" else _css

              if _css == False and _target == key:
                _res = sublime.Region(_p, _p + 1)
                break
              j += 1

            if _res != "":
              break

            _scss = False
            i -= 1

          else:
            _res = sublime.Region(-1, -1)
          return _res

        _curt = checkCurtLine()
        _res = findReverse(_curt) if dir == "r" else findForward(_curt)

        return _res


      # 選択範囲再設定
      def resetSelection(target):
        view.sel().clear()
        view.sel().add(target)
        return view.sel()[0]

      # インターポレーション内にカーソルがある場合、外側に移動
      def moveOutFromIntrpl(point):
        _s = findStr('{', start = point, dir = "r").begin()
        _e = findStr('}', start = point, dir = "r").begin()
        if view.substr(_s - 1) == "#" and _s > _e:
          _res = resetSelection(_s - 1).begin()
        else:
          _res = view.sel()[0].begin()
        return _res

      # セレクタ位置にある場合は{}の内側に、それ以外は;または}に移動
      def moveIntoDcBlock(point):
        if view.substr(point - 1) == "}" or view.substr(point - 1) == ";":
          resetSelection(point - 1).begin()
        _p = moveOutFromIntrpl(point)

        _c = findStr(';', start = _p).begin()
        _s = findStr('{', start = _p).begin()
        _e = findStr('}', start = _p).begin()
        
        if _s < _e:
          while view.substr(_s - 1) == "#":
            _s = findStr('{', start = _e + 1 ).begin()
            _e = findStr('}', start = _e + 1 ).begin()
            if _s > _e:
              break

        _lst = [_c,_s,_e]
        def _f(x): return x > -1
        _lst = list(filter(_f, _lst))
        _pos = min(_lst) if _lst != [] else False
        _res = resetSelection(_pos).begin() if _pos else False
        return _res


      # 宣言ブロック選択
      def selectDeclarationBlock(point):

        ## カーソルが（）や[]の直後にある場合、
        ## 宣言ブロックが選択されず、直前の括弧が選択されてしまうので調整する
        def adjustSelection(region):
          _p = region.begin()

          ### 選択範囲の宣言ブロックではない場合 expand_selectionを再実行
          ### （始点が"("、"["の場合か、"#{"の場合）
          if view.substr(_p) != "{" or (view.substr(_p) == "{" and view.substr(_p - 1) == "#"):
            view.run_command('expand_selection', {'to': 'brackets'})
            #### 再実行しても選択範囲が変わらない場合
            #### 直上に{}が存在しない = グローバルの変数宣言のため選択範囲を解除
            if _p == view.sel()[0].begin():
              resetSelection(view.sel()[0].end())

          return view.sel()[0]

        _mv = moveIntoDcBlock(point)
        if _mv:
          view.run_command('expand_selection', {'to': 'brackets'})
          view.run_command('expand_selection', {'to': 'brackets'})
          adjustSelection(view.sel()[0])
        return view.sel()[0]



      # 選択範囲の始点を宣言ブロックからルールセットに拡張
      def expandRulesetStartPositon(region):
        _declaration = region
        _posE = _declaration.end()

        ## グローバルの変数宣言では、;も選択範囲に含める
        _posE += 1 if view.substr(_posE) == ";" else 0

        _c = findStr(';', start = _declaration.begin() , dir = "r").end()
        _s = findStr('{', start = _declaration.begin() , dir = "r").end()
        _e = findStr('}', start = _declaration.begin() , dir = "r").end()

        ## 前方にインターポレーションがある場合、それ無視してその前の{}を探す
        while view.substr(_s - 2) == "#":
          if findStr('}', start = _s - 2,).end() >= _e:
            _e = findStr('}', start = _s - 1, dir = "r").end()
            _s = findStr('{', start = _s - 1, dir = "r").end()
          else:
            break

        _posS = max(_s, _e, _c)

        ## 拡張した選択範囲のうち、コメントと行頭改行分をもどす
        i = _posS
        _cssCmt = _scssCmt = False
        while i < _declaration.begin():
          if view.substr(i) == "/":
            if view.substr(i + 1) == "*":
              _cssCmt = True
            if view.substr(i + 1) == "/":
              _scssCmt = True
          elif view.substr(i) == "*":
            if view.substr(i + 1) == "/":
              _cssCmt = False
              i += 2
          elif view.substr(i) == "\n":
            _scssCmt = False
          
          if _cssCmt == False and _scssCmt == False:
            if view.substr(i) == "\n" or view.substr(i) == "\t" or view.substr(i) == " ":
              pass
            else:
              break
          i += 1

        _posS = i

        if _posE > 0:
          resetSelection(sublime.Region(_posS, _posE))

      sel = selectDeclarationBlock( view.sel()[0].begin() )
      expandRulesetStartPositon(sel)

  except:
    pass
