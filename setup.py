from setuptools import setup

setup(
    name='ofxfix',
    url='https://github.com/tedcarnahan/ofxfix',
    author='Ted Carnahan',
    author_email='ted@tedcarnahan.com',
    description="A bit of code to demonstrate how to write simple OFX financial data cleanup",
    version='0.1',
    install_requires=[
        'click',
        'click-log',
        'ofxtools',
    ],
    entry_points='''
    [console_scripts]
    ofxfix=ofxfix:cli
    ''',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
