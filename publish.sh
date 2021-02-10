python3 setup.py sdist
twine upload dist/*
rm -rf dist
rm -rf build
