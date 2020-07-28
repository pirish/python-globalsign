import setuptools


requirements = [
    'lxml',
    'requests',
    'zeep',
    'pyopenssl',
]

test_requirements = [
    'pytest',
    'requests-mock',
]

setuptools.setup(
    name="python-globalsign",
    version="0.0.1",
    url="https://github.com/pirish/python-",

    author="Patrick Irish",
    author_email="patscrap@gmail.com",

    description="Globalsign API",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'gs = globalsign.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
