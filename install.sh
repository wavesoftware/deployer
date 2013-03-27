#!/bin/bash

INSTALLER=$(readlink -f $0)
ROOT=$(dirname $INSTALLER)
ENV='dev'
if [ "$1" == "prod" ]; then
	ENV='prod'
fi
	
python=`command -v python2.7`
if [[ $? -ne 0 ]]; then
	sudo apt-get install python2.7
	python=`command -v python2.7`
fi
curl=`command -v curl`
if [[ $? -ne 0 ]]; then
	sudo apt-get install curl
	curl=`command -v curl`
fi

pip=`command -v pip`
if [[ $? -ne 0 ]]; then
    curl http://python-distribute.org/distribute_setup.py | sudo $python
    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo $python
    pip=`command -v pip`
fi

if [ "$ENV" != "prod" ]; then
	x=$(command -v virtualenv)
	if [[ $? -ne 0 ]]; then
		sudo $pip install virtualenv
	fi
	x=$($pip freeze | grep virtualenvwrapper)
	if [[ $? -ne 0 ]]; then 
		sudo $pip install virtualenvwrapper
	fi
	# if virtualenvwrapper.sh is in your PATH (i.e. installed with pip)
    source `which virtualenvwrapper.sh`
    #source /path/to/virtualenvwrapper.sh # if it's not in your PATH
	x=$(lsvirtualenv | grep deploy-source)
	if [[ $? -ne 0 ]]; then
		mkvirtualenv --distribute --no-site-packages deploy-source
	fi
	cdvirtualenv
	echo $ROOT > ./.project
	cd $ROOT
	workon deploy-source
	pip install -r pip.deps
else
	sudo pip install -r pip.deps
fi
