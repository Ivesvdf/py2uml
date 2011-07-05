#/usr/bin/env bash

for dir in examples/*; do 
	NUMBER=$(echo $dir | sed 's/[a-z/]*//g')
	cd "examples/example$NUMBER"
	echo "### Example $NUMBER ###"
	echo "Command: " 
	echo ""
	echo -n "    " 
	cat run.sh | tail -n 1
	echo ""
	for pythonfile in *.py; do
		echo "*$pythonfile:*"
		echo ""
		cat $pythonfile | sed 's/^/    /'
	done
	echo ""
	echo "which generates  "
	echo "![](https://raw.github.com/Ivesvdf/py2uml/master/examples/example$NUMBER/output.png)"
	echo ""
	echo ""
	cd ../..
done
