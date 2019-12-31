# ####################### #
#  compiles the site
# ####################### #

#
# const
SRC_PATH = ".\\src\\"
TEMPLATE_PATH = ".\\template\\"
OUTPUT_PATH = ".\\zout\\"
SRC_EXT = ".txt"
OUT_EXT = ".html"
SITE_FILE_PATH = SRC_PATH + "site.txt"
INDEX_FILE_NAME = "index"
ABOUT_FILE_NAME = "about"
IDX_OUT_FILE_PATH = OUTPUT_PATH + INDEX_FILE_NAME + OUT_EXT
ART_TMPL_FILE_PATH = TEMPLATE_PATH + "article" + OUT_EXT
VAR_ARTICLE_LIST = "article_list"
VAR_ARTICLE_BEGIN = "article_begin"
VAR_ARTICLE_END = "article_end"

#
# get all variable in a text file
def getVariables(filePath):
  key = ""
  resDict = {}
  for line in open(filePath, "r"):
    line = line.rstrip()
    
    #skip empty lines or comments
    if not line or line.startswith("#"):
      continue

    #manage multi-line field
    if key != "":
      if line == "}}":
        key = ""
        continue
      resDict[key] = resDict[key] + "\n" + line if key in resDict else line
      continue

    #<key>: <value>
    pos = line.index(":")
    value = line[pos+1:].lstrip()
    key = line[:pos]
    
    #if it's a multi-line field it keeps 'key' set
    if value != "{{":
      resDict[key] = value
      key = ""

  return resDict

#
# actualize a template file
def actualize(templatePath, dstPath, d, d2):
  d.update(d2)
  file = open(dstPath, "w")
  for line in open(templatePath, "r"):
    for key, value in d.items():
      line = line.replace("{{ " + key + " }}", value)
    file.write(line)
  file.close()
  return
  
#
# actualize a template file
def insertArticle(indexPath, artDic, artNext):
  artTemplate = []
  outLines = []
  artSection = False
  for line in open(indexPath, "r"):
    if VAR_ARTICLE_BEGIN in line:
      artSection = True
      artTemplate.append(line)
    elif VAR_ARTICLE_END in line:
      artSection = False
      artTemplate.append(line)

      #if there'll be another article...
      if artNext:
        outLines.append("\n")
        outLines.extend(artTemplate)
    elif artSection:
      artTemplate.append(line)

      #actualize the article section
      for key, value in artDic.items():
          line = line.replace("{{ " + key + " }}", value)
      outLines.append(line)
    else:
      outLines.append(line)

  f = open(indexPath, "w")
  f.write("".join(outLines))
  f.close()
  return

# ################################
#     main
# ################################

# site variables
siteDic = getVariables(SITE_FILE_PATH)

# actualize index.html with site variables
actualize(TEMPLATE_PATH + INDEX_FILE_NAME + OUT_EXT, IDX_OUT_FILE_PATH, siteDic, {})

# articles
articles = siteDic[VAR_ARTICLE_LIST].split("\n")

# articles loop
lastIdx = len(articles) - 1
for i, article in enumerate(articles):
  # article variables
  artDic = getVariables(SRC_PATH + article + SRC_EXT)
  
  # actualize the article
  actualize(ART_TMPL_FILE_PATH, OUTPUT_PATH + article + OUT_EXT, siteDic, artDic)
  
  # insert article in index.html
  insertArticle(IDX_OUT_FILE_PATH, artDic, i != lastIdx)

# about.html
aboutDic = getVariables(SRC_PATH + ABOUT_FILE_NAME + SRC_EXT)
actualize(ART_TMPL_FILE_PATH, OUTPUT_PATH + ABOUT_FILE_NAME + OUT_EXT, siteDic, aboutDic)
