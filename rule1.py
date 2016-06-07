import sys
import understand
import parser
import model as m

""" Using understand get the method name in which error occur"""

path = "/home/asvikr/Aurea_savvion.udb"
cur_file = "/mnt/ashish/Codenation_Project/Project/Aurea_savvion/output/trunk/bmmain/sbm/src/com/savvion/sbm/bizlogic/server/WFWorkItem.java"
line_no = 2089

p = parser.Parser()
tree = p.parse_file(sys.argv[1])

block_list = []

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
		self.predicate_list = []
		self.lines = []
		self.if_true = []
		self.if_false = []
		self.block = []
		self.to = 0

	def print_lines(self):
		print(self.lines)

	def print_predicate_list(self):
		print(self.predicate_list)

	def print_if_true(self):
		print(self.if_true)

	def print_if_false(self):
		print(self.if_false)


	def visit_IfThenElse(self,method_decl):
		# if self.first_method:
		# 	print
		# 	print('ifthenelse:')
		# 	self.first_method = False

		#print(method_decl)
		self.lines.append(method_decl.lineno)
		self.predicate_list.append(method_decl.predicate)
		self.if_true.append(method_decl.if_true)
		self.if_false.append(method_decl.if_false)

		try:
			if (method_decl.if_false is not None):
				self.block.append((method_decl.if_false.startline,method_decl.if_false.endline))
				self.to+=1
				#print(method_decl.if_false.startline,method_decl.if_false.endline)
		except AttributeError:
			pass

		try:
			if (method_decl.if_true is not None):
				self.block.append((method_decl.if_true.startline,method_decl.if_true.endline))
				self.to+=1
				#print(method_decl.if_true.startline,method_decl.if_true.endline)
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
	for line in (st,en+1):
		lexemes = lex.lexemes(line,line)
		for lexeme in lexemes:
			en = lexeme.ent()
			if en:
				if (en.simplename=='throw') or (en.simplename=='return'):
					return True


	return False

def find_condition(line,lex):

	while line>0:
		lexemes = lex.lexemes(line,line)
		pp = False
		for lexeme in lexemes:

			if (lexeme.text()=='(' or lexeme.text()==')'):
				continue

			if pp==True:
				en = lexeme.ent()

				if en:
					#print(lexeme.text())
					
					if str(en.type())!="boolean":
						return ("-1",0)
					else:
						val = lexeme.text()
						#print(val)
						p = 1
						while(lexeme.next()!=None):
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
					#print(back_dict[line])
					cond = find_condition(back_dict[line],lex)
					if cond[1]==1:
						return (cond[0],0)
					else:
						return (cond[0],1)
					
			elif lexeme.text() == "if":
				pp = True

		line-=1


def get_condition(ifclass,lex,block_list):

	condition = []
	sz_list = len(block_list)
	for i in range(sz_list):
		cond = find_condition(block_list[i][0],lex)
		#print(cond)
		if cond[0]=="-1":
			return condition
		else:
			condition.append(cond)

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
		if cond==condition:
			ch = check(ifclass.block[i][0],ifclass.block[i][1],lex)
			if ch==True:
				return ch

	return False


""" Main function """

if __name__=='__main__':

	key = "wiID"
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
				#par = en.parent.split(".")[-1]
				par = en.parent().simplename()
				print(par)

				method_line = get_method_line(par,line_no,lex)

				#print(method_line)



	ifclass = MyVisitor()

	tree.accept(ifclass)
	#ifclass.print_lines()
	print()
	#ifclass.print_predicate_list()
	print()
	#ifclass.print_if_false()
	print()
	#ifclass.print_if_true()
	print()

	sz = len(ifclass.block)

	#print(ifclass.to,sz)

	front_dict = dict()

	back_dict = dict()

	idx = 0

	for i in range(0,sz):
		front_dict[ifclass.block[i][0]] = ifclass.block[i][1]
		back_dict[ifclass.block[i][1]] = ifclass.block[i][0]


	for i in range(0,sz):
		if (line_no >= ifclass.block[i][0]) and (line_no<ifclass.block[i][1]):
			idx = i
			block_list.append(ifclass.block[i])
			


	
	target_line = max(target_line,method_line)
	#print(target_line)

	condition = get_condition(ifclass,lex,block_list)
	condition.sort()
	print(condition)
	if len(condition)==0:
		check = False
	else:
		check = match_condition(condition,ifclass,target_line,lex,idx)

	
	if check:
		print("False Positive")
	else:
		print("True Positive")


