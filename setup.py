import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='petsafe_smartfeed',
    version='1.3',
    author='Jordan Stremming',
    license='MIT',
    author_email='jcstremming@gmail.com',
    description='Provides ability to connect and control a PetSafe Smart Feed device using the PetSafe-SmartFeed API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/techzune/petsafe_smartfeed',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
