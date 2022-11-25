from setuptools import setup, find_packages

setup(
    name='qympy',
    version='1.0',
    license='MIT',
    author="Yi-An Chen",
    author_email='r08222011@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/r08222011/Qympy',
    keywords='quantum machine learning, quantum computation, sympy, qiskit',
    install_requires=[
        'numpy',
        'sympy',
        'qiskit',
        'pylatexenc',
        'matplotlib',
    ],
)