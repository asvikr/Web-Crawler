import sys
import understand
import parser
import model as m
import re

""" Using understand get the method name in which error occur"""

path = "/home/asvikr/Aurea_savvion.udb"
cur_file = "/mnt/ashish/Codenation_Project/Project/Aurea_savvion/output/trunk/bmmain/sbm/src/com/savvion/sbm/bizlogic/storeevent/BSUtil.java"
line_no = 310
key = "val"

p = parser.Parser()
tree = p.parse_file(sys.argv[1])

block_list = []

child_list = {}

""" Get lexer of file""" 

def get_lexer(filename):

	file = db.lookup(filename)[0]
	lex = file.lexer()
	return lex

""" My visitor class give all necessary things in if else condition statement """

class MyVisitor(m.Visitor):

	def __init__(self):
		super(MyVisitor,self).__init__()
		self.first_field = True
		self.first_method = True
		self.block = []

	def visit_IfThenElse(self,method_decl):
		self.predicate_list.append(method_decl.predicate)

		try:
			if (method_decl.if_false is not None):
				self.block.append((method_decl.if_false.startline,method_decl.if_false.endline))
				self.to+=1
		except AttributeError:
			pass

		try:
			if (method_decl.if_true is not None):
				self.block.append((method_decl.if_true.startline,method_decl.if_true.endline))
				self.to+=1
		except AttributeError:
			pass

		return True

""" Get line numer of method in which error occur this will decide target line upto which program check """

def get_method_line(par,line_no,lex):
	while line_no>0:
		lexemes = lex.lexemes(line_no,line_no)
		for lexeme in lexemes:
			en = lexeme.ent()
			if en:
				if "Method" in en.kindname():
					if en.simplename() == par:
						ref = en.ref()
						return ref.line()

		line_no-=1
	return 1

""" Check for keyword "throw" or "return" """

def check(st,en,lex):
	for line in range(st,en+1):
		#print(line)
		lexemes = lex.lexemes(line,line)
		for lexeme in lexemes:
			if (lexeme.text()=='throw') or (lexeme.text()=='return'):
				return True
	return False

def find_condition(ifclass,line,lex):

	while line>0:
		lexemes = lex.lexemes(line,line)
		pp = False
		for lexeme in lexemes:

			if (lexeme.text()=='(' or lexeme.text()==')'):
				continue

			if pp==True:
				en = lexeme.ent()

				if en:
					if str(lexeme.text())==key:
						lexeme = lexeme.next()
						chk = 1
						for l in lexemes:
							
							if l.text()=="==":
								chk = 1
							elif l.text()=='!=':
								return ("-1",0)
							elif l.text()=="null":
								 for kk in child_list[line]:
								 	block_list.append(kk)
								 return ("-1",0)
							

					if str(en.type())!="boolean":
						return ("-1",0)
					else:
						val = lexeme.text()
						p = 1
						while(True):
							if lexeme.text()=='!=':
								p = 0
							elif lexeme.text()=='==':
								p = 1
							elif lexeme.text()==')':
								return (val,p)
							elif lexeme.text()=='false':
								return (val,1^p)
							elif lexeme.text()=='true':
								return (val,p)
							lexeme = lexeme.next()
						

			if lexeme.text() == "else":

				if line in back_dict:
					cond = find_condition(ifclass,back_dict[line],lex)
					if cond[1]==1:
						return (cond[0],0)
					else:
						return (cond[0],1)
					
			elif lexeme.text() == "if":
				pp = True

		line-=1

""" Get all condition for comparing with original condition """

def get_condition(ifclass,lex,block_list):

	condition = []
	sz_list = len(block_list)
	for i in range(len(block_list)):
		cond = find_condition(ifclass,block_list[i][0],lex)
		condition.append((cond,block_list[i]))

	return condition

""" Match conditions to check any throws or any return satement are there """

def match_condition(condition,ifclass,target_line,lex,idx):

	sz = len(condition)
	if sz==0:
		return False

	for i in range(idx-1,0,-1):
		if ifclass.block[i][0]<target_line:
			return False
		cond = get_condition(ifclass,lex,[(ifclass.block[i][0],ifclass.block[i][1])])
		for conds in cond:
			if conds[0]==condition:
				ch = check(conds[1][0],conds[1][1],lex)
				if ch==True:
					return ch

	return False

""" Main function """

if __name__=='__main__':

	db = understand.open(path)
	lex = get_lexer(cur_file)
	lexemes = lex.lexemes(line_no,line_no)
	define_at = line_no
	for lexeme in lexemes:
		en = lexeme.ent()
		if en:
			if str(en.simplename())==key:

				for refs in en.refs("Definein"):
					target_line = refs.line()
					break

				ref = en.ref()
				define_at = ref.line()
				par = en.parent().simplename()
				print(par)
				method_line = get_method_line(par,line_no,lex)

	ifclass = MyVisitor()
	tree.accept(ifclass)

	sz = len(ifclass.block)
	front_dict = dict()
	back_dict = dict()
	idx = 0

	for i in range(0,sz):
		front_dict[ifclass.block[i][0]] = ifclass.block[i][1]
		back_dict[ifclass.block[i][1]] = ifclass.block[i][0]
		child = []
		child_list[ifclass.block[i][0]] = list()

		for j in range(0,sz):
			if i==j:
				continue
			else:
				if (ifclass.block[j][0]>ifclass.block[i][0]) and (ifclass.block[j][1]<ifclass.block[i][1]):
					child.append(ifclass.block[j])

		child_list[ifclass.block[i][0]] = child

	for i in range(0,sz):
		if (line_no >= ifclass.block[i][0]) and (line_no<ifclass.block[i][1]):
			idx = i
			break
			
	target_line = max(target_line,method_line)

	condition = find_condition(ifclass,ifclass.block[idx][0],lex)
	print(condition)
	if condition[0]=='-1':
		check = False
	else:
		check = match_condition(condition,ifclass,target_line,lex,idx)
	
	if check:
		print("False Positive")
	else:
		print("True Positive")


