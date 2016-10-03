from setuptools import setup, find_packages

setup(
	name='jit',
	version='0.1',
	packages=find_packages(),
	py_modules=['jit'],
	include_package_data=True,
	install_requires=[
		'Click',
		'GitPython'
	],
	entry_points='''
		[console_scripts]
		jit=jit:cli
	'''
)
	