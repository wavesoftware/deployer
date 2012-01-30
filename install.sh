sudo apt-get install python2.7 curl
pip=`command -v pip`
if [[ $? -eq 1 ]]; then
    curl http://python-distribute.org/distribute_setup.py | sudo python
    curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python
fi
sudo pip install virtualenv 
sudo pip install virtualenvwrapper

mkvirtualenv --distribute --no-site-packages deployproj

pip install -r pip.deps