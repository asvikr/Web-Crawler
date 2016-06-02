import understand


""" path is path to udb file"""

path = "/home/asvikr/Aurea_savvion.udb"
cur_file = "/mnt/ashish/Codenation_Project/Project/Aurea_savvion/output/trunk/bmmain/sbm/src/com/savvion/sbm/bizlogic/client/BLCommand.java"



""" Finding the method name in which error is found """

def get_method(lex,line,key):
	lexemes = lex.lexemes(line,line)
	for lexeme in lexemes:
		if lexeme.text()==key:
			ents = lexeme.ent()

			for refs in ents.refs("Setby"):
				if refs.line()==line:
					m_name = refs.ent().name().split(".")
					method = m_name[-1]
					return method


""" Get lexer of given file """

def get_lexer(filename):

	file = db.lookup(filename)[0]
	lex = file.lexer()
	return lex


""" check_fun try to find .lock() thing from error point upto where method is declared if lock is
find then return True as flag for indicating false positive """

def check_fun(lex,line,method):	
	while line>0:
		#print(line,method)
		lexemes = lex.lexemes(line,line)
		for lexeme in lexemes:
			en = lexeme.ent()
			if en:
				if "Method" in en.kindname():
					if en.simplename()==method:
						ret = False
						for refs in en.refs("Callby"):
							n_line = refs.line()
							n_method = refs.ent().name().split(".")[-1]
							n_file = refs.file().longname()
							#print(n_line,n_method,n_file)
							if str(n_file) != cur_file:
								n_lex = get_lexer(n_file)
							else:
								n_lex = lex

							ret = check_fun(n_lex,n_line-1,n_method)
							if ret==False:
								return ret

						return ret
				
				if str(en.type())=="Lock":
					n_lex = lexeme.next().next()
					#print(n_lex.text())
					n_en = n_lex.ent()
					#print(n_en.simplename())
					if n_en.simplename() == "lock":
						return True
					else:
						return False
		line-=1

	return False

""" main function """
""" currently taking manually line number and keyword"""

if __name__=='__main__':

	db = understand.open(path)
	lines = [2535,2543]
	keyword = ["server","bl"]
	lex = get_lexer(cur_file)

	c = 0
	""" Checking each line where error occurs """
	for line in lines:
		method = get_method(lex,line,keyword[c])
		line-=1

		""" Start our function """
		res = check_fun(lex,line,method)

		if res==True:
			print("false positive")
		else:
			print("true positive")
		c+=1
