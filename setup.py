from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='qympy',
    version='1.0.2',
    license='MIT',
    author="Yi-An Chen",
    author_email='r08222011@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
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