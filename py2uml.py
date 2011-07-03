#!/usr/bin/env python
import sys
import inspect

def log(string):
	sys.stderr.write("LOG: " + string + "\n")

class ClassNode:
	def __init__(self, name, parents):
		self.name = name
		self.methods = []
		self.parents = parents


	def addMethod(self, method):
		self.methods.append(method)

class Processor:
	def __init__(self):
		self.visited = set()

		self.modules = dict()

	def processFiles(self,filenames):
		import os
		sys.path.append(os.getcwd())
		log("currently in " + str(os.getcwd()))
		for file in filenames:
			log("Processing file " + file)
			self.processFile(file)

	def processFile(self,filename):
		moduleName = filename.replace("./", "").replace(".py", "").replace("/", ".")

		if filename.find("__init__.py") >= 0:
			log("Ignoring __init__.py file")
			return

		log("Processing file for module " + moduleName)
		__import__(moduleName, locals(), globals())
		self.processModule(sys.modules[moduleName])

	def processModule(self,module):
		log("Processing module " + str(module))
		for (name, something) in inspect.getmembers(module):
			if type(something) == dict:
				continue 

			if repr(something) in self.visited:
				continue 

			self.visited |= set([repr(something)])

			if inspect.isclass(something):
				self.processClass(something)

			#elif inspect.ismodule(something):
			#	self.processModule(something)

			else:
				#log(str(type(something)))
				pass #log(str(something))

	def processClass(self,someClass):
		name = someClass.__name__
		log("Processing class: " + name + " in module " + someClass.__module__)
		moduleName = someClass.__module__

		if not moduleName in self.modules:
			self.modules[moduleName] = list()

		classNode = ClassNode(name, someClass.__bases__)
		self.modules[moduleName].append(classNode)

		for (someName, something) in inspect.getmembers(someClass):
			if inspect.ismethod(something):
				self.processMethod(something, classNode)

	def processMethod(self,someMethod, classNode):
		log("Processing method: " + someMethod.__name__)
		classNode.addMethod(someMethod)

	def toDot(self, out):
		line = lambda s: out.write(s + "\n")
		out.write("""
digraph G {
		fontname = "Bitstream Vera Sans"
        fontsize = 8
		rankdir=BT

        node [
                fontname = "Bitstream Vera Sans"
                fontsize = 8
                shape = "record"
        ]

        edge [
                fontname = "Bitstream Vera Sans"
                fontsize = 8
        ]
""")

		classnameToDot = lambda name :  "Class" + name

		def isPublic(method):
			if method.__name__.find("_") == 0 and \
				method.__name__.rfind("_") < len(method.__name__)-1:
				return False
			else:
				return True

		def writeDecl(out, method, symbol):
			out.write(symbol + " ")

			out.write(method.__name__)
			argspec = inspect.getargspec(method)
			out.write(inspect.formatargspec(*(argspec[:2])) + "\l")

		for (name, module) in self.modules.items():
			if len(module) > 1:
				line("subgraph cluster{modulename} {".replace("{modulename}",
					name.replace(".", "")))
				line("   label = \"Module " + name + "\"")

			for c in module:
				line(classnameToDot(c.name) + " [")


				out.write("label = \"{" + c.name + "|")
				
				for method in c.methods:
					if not isPublic(method):
						writeDecl(out, method, "-")

				out.write("|")
				
				for method in c.methods:
					if isPublic(method):
						writeDecl(out, method, "+")

				out.write("}\"\n")
				line("]")

			if len(module) > 1:
				line("}")

		out.write("""
		edge [
                arrowhead = "empty"
        ]
		""")

		for module in self.modules.values():
			for c in module:
				for parent in c.parents:
					line(classnameToDot(c.name) + " -> " +
							classnameToDot(parent.__name__))

		line("}")

if __name__ == "__main__":
	log("Starting processing of argument vector")
	proc = Processor()
	proc.processFiles(sys.argv[1:])
	proc.toDot(sys.stdout)
