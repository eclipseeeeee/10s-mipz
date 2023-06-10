import re
import os

PATH = "./numpy"

STATEMENTS_LOGICAL = [
  "if",
  "elif",
  "else",
  "try",
  "catch",
  "with"
]

STATEMENTS_ITERATION = [
  "for",
  "while"
]

STATEMENTS_SOLITARY = [
  "break",
  "continue",
  "pass"
]

REGEX_DECLARATION = '.*(def.*\(.*\)).*'
REGEX_CALL        = '.*\(.*'
REGEX_ASSIGNMENT  = ".*[^=]=[^=].*"

def filter(name):
  return name.endswith(".py")

def listfiles(root):
  res = []
  
  for path, subdirs, files in os.walk(root):
    for name in files:
      fullpath = os.path.join(path, name)
      fullpath = fullpath.replace("\\", "/")
      if filter(fullpath):
        res.append(fullpath)
  
  return res

def read_lines(filepath):
    with open(filepath, 'r', encoding="utf8") as file: 
        data = file.read()
    return data.split('\n')


def is_empty_line(line):
  return len(line.strip()) == 0


def count_logical(lines):
  logical_lines = 0
  for line in lines:
    logical_lines += logical_line(line)
  return logical_lines

def logical_line(line):
  logical_lines = 0
  line = line.strip()

  arr = line.split()
  for s in STATEMENTS_LOGICAL:
    if s in line.split():
      logical_lines += arr.count(s)
        
  for s in STATEMENTS_ITERATION:
    if s in line.split():
      logical_lines += arr.count(s)
  
  for s in STATEMENTS_SOLITARY:
    arr = line.split()
    if len(arr) == 1 and s == arr[0]:
      logical_lines += 1  
  

  if "return" in arr:
    logical_lines += 1  

  if re.match(REGEX_CALL, line) and not re.match(REGEX_ASSIGNMENT, line):
    logical_lines += 1 

  if re.match(REGEX_ASSIGNMENT, line):
    logical_lines += 1
    
  if line.strip().endswith(":"):
    logical_lines += 1
  
  return logical_lines


def count_loc(lines):
  code_lines    = 0
  comment_lines = 0
  empty_lines   = 0
  
  logical_lines = 0
  
  docstring = False
  blockstring = False
  
  for line in lines:
    line = line.strip()
    
    if not docstring and not blockstring and not line.startswith("#"):
      logical_lines += logical_line(line)

    if   line.startswith("#") \
      or docstring and not (line.startswith('"""') or line.startswith("'''")) \
      or (line.startswith("'''") and line.endswith("'''") and len(line) >3)   \
      or (line.startswith('"""') and line.endswith('"""') and len(line) >3)   :
      comment_lines += 1
      
      
    if   line.endswith("(") and not blockstring \
      or line.startswith(")") and not blockstring:
      blockstring = not blockstring

    elif line.endswith("'''") and not docstring \
      or line.endswith('"""') and not docstring :
      comment_lines += 1
      docstring = not docstring

    elif line.startswith('"""') or line.startswith("'''") :
      comment_lines += 1
      docstring = not docstring
    
    elif is_empty_line(line)  :
      empty_lines += 1

    else:
      code_lines += 1

  return {
    "code"      : code_lines,
    "empty"     : empty_lines,
    "comment"   : comment_lines,
    "physical"  : len(lines),
    "logical"   : logical_lines
  }


def is_comment(line):
  return line.strip().startswith('#')


def loc_lines(filepath):
  lines = read_lines(filepath)
  
  res = count_loc(lines)
  return res

def main():
  files = listfiles(PATH)
      
  code_lines      = 0
  empty_lines     = 0
  comment_lines   = 0
  physical_lines  = 0
  logical_lines   = 0
  
  for f in files:
    res = loc_lines(f)
    
    code_lines     += res["code"]
    empty_lines    += res["empty"]
    comment_lines  += res["comment"]
    logical_lines  += res["logical"]
    physical_lines += res["physical"]
  
  print(f'code:          {code_lines}')
  print(f'empty:         {empty_lines}')
  print(f'comment:       {comment_lines}')
  print(f'logical:       {logical_lines}')
  print(f'physical:      {physical_lines}')
  print(f'comment level: {comment_lines/code_lines}')


main()