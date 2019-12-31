# ############################################################### #
#    compiles all the [[code]] contained in all html files
# ############################################################### #

import os
import xml.etree.ElementTree as ET
import re

#
# const
NOTEPADPP_LANG_FILE_PATH = ".\\langs.model.xml"
HTML_PATH = ".\\zout\\"
START_CODE_TAG = "[[code: "
END_CODE_TAG = "]]"

class CodeSyntax:

  def __init__(self, name):
    self.name = name
    tree = ET.parse(NOTEPADPP_LANG_FILE_PATH)
    root = tree.getroot()
    
    #<Language name="cs" ext="cs" commentLine="//" commentStart="/*" commentEnd="*/">
    elem = root.find(".//Languages/Language[@name='" + self.name + "']")
    self.commentLine = elem.attrib["commentLine"]
    self.commentStart = elem.attrib["commentStart"]
    self.commentEnd = elem.attrib["commentEnd"]
    
    # <Keywords name="instre1">abstract as base break case catch checked continue default delegate do else event explicit extern false finally fixed for foreach goto if implicit in interface internal is lock namespace new null object operator out override params private protected public readonly ref return sealed sizeof stackalloc switch this throw true try typeof unchecked unsafe using virtual while</Keywords>
    # <Keywords name="type1">bool byte char class const decimal double enum float int long sbyte short static string struct uint ulong ushort void</Keywords>
    self.keyInst = elem.find("./Keywords[@name='instre1']").text.split()
    self.keyType = elem.find("./Keywords[@name='type1']").text.split()

#
# 
def spanIt(code, spanType):
  return "<span type='" + spanType + "'>" + code + "</span>"

#
# actualize a template file
def convertCodeLines(codeLines, syntax):
  specials = ["(", ")", "{", "}", "[", "]", ":", "="]
  outCodeLines = []
  for line in codeLines:
    #-------------------------------------- comments (%%gestione parziale)
    lineStrp = line.strip()
    if syntax.commentLine and lineStrp.startswith(syntax.commentLine):
      outCodeLines.append(line.replace(lineStrp, spanIt(lineStrp, "comment")))
      continue
    
    stringFlag = False
    lineOut = ""
    for elem in re.split('(\W)', line):
      #-------------------------------------- strings
      if elem == "'" or elem == '"':
        if stringFlag:
          lineOut = lineOut + elem + "</span>"
        else:
          lineOut = lineOut + "<span type='string'>" + elem
        stringFlag = not stringFlag
        continue

      if stringFlag:
        lineOut = lineOut + elem
        continue
      
      #-------------------------------------- others...
      if elem in specials:
        lineOut = lineOut + spanIt(elem, "spec")
      elif elem in syntax.keyType:
        lineOut = lineOut + spanIt(elem, "type")
      elif elem in syntax.keyInst:
        lineOut = lineOut + spanIt(elem, "instr")
      else:
        lineOut = lineOut + elem

    outCodeLines.append(lineOut)

  return outCodeLines
  
#
# actualize a template file
def compileCode(filePath):
  outLines = []
  codeLines = []
  codeName = ""
  # print("------------------- " + filePath)
  for line in open(filePath, "r"):
    if line.startswith(START_CODE_TAG):
      codeName = line.replace(START_CODE_TAG, "").strip()
      codeLines = []
    elif line.startswith(END_CODE_TAG):
      syntax = CodeSyntax(codeName)
      outCodeLines = convertCodeLines(codeLines, syntax)
      outLines.extend(outCodeLines)
      codeName = ""
    elif codeName != "":
      codeLines.append(line)
    else:
      outLines.append(line)

  f = open(filePath, "w")
  f.write("".join(outLines))
  f.close()
  return

# ################################
#     main
# ################################

files = [os.path.join(HTML_PATH, f) for f in os.listdir(HTML_PATH) if os.path.isfile(os.path.join(HTML_PATH, f))]
for filePath in files:
  fileName, fileExt = os.path.splitext(filePath)
  if fileExt == ".html":
    compileCode(filePath)
