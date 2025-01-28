from setuptools import setup, find_packages

setup(
    name='kake',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'kake': [
            'views/*.py', 
            'models/*.py', ]
    },
    install_requires=[
        'django',
        'psycopg2-binary',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
)
