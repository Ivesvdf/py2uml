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

		self.classes = dict()

	def processFiles(self,filenames):
		for file in filenames:
			log("Processing file " + file)
			self.processFile(file)

	def processFile(self,filename):
		try:
			modulename = filename.replace("/", ".").replace(".py", "")
			module = __import__(modulename, fromlist=modulename.split('.')[1:])
		except ImportError:
			# Maybe no __init__.py file present in dir, try making one
			pos = filename.rfind("/")
			package = filename[:pos+1]
			initfile = package + "__init__.py"
			if pos >= 0:
				try:
					f = open(initfile)
				except IOError:
					log("No __init__.py file present in " + package)
					log("Creating __init__.py file in " + package)
					f = open(initfile, "w")
					f.close()
					log("Trying to load once again")
					module = __import__(modulename,
							fromlist=modulename.split('.')[1:])
					log("Removing __init__ file")
					import os
					os.remove(initfile)
					os.remove(initfile + "c")
		self.processModule(module)

	def processModule(self,module):
		log("Processing module " + str(module))
		for name in dir(module):
			something = getattr(module, name)

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

		
		if not name in self.classes:
			self.classes[name] = ClassNode(name, someClass.__bases__)

		for someName in dir(someClass):
			something = getattr(someClass, someName)

			if inspect.ismethod(something):
				self.processMethod(something, self.classes[name])

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

		for c in self.classes.values():
			line(classnameToDot(c.name) + " [")
			out.write("label = \"{" + c.name + "||")
			
			for method in c.methods:
				out.write("+ " + method.__name__)
				argspec = inspect.getargspec(method)
				out.write(inspect.formatargspec(*(argspec[:2])) + "\l")

			out.write("}\"\n")
			line("]")

		out.write("""
		edge [
                arrowhead = "empty"
        ]
		""")

		for c in self.classes.values():
			for parent in c.parents:
				line(classnameToDot(c.name) + " -> " +
						classnameToDot(parent.__name__))

		line("}")

if __name__ == "__main__":
	log("Starting processing of argument vector")
	proc = Processor()
	proc.processFiles(sys.argv[1:])
	proc.toDot(sys.stdout)
