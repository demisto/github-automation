from __future__ import absolute_import

from setuptools import find_packages, setup

with open('./README.md', 'r') as f:
    readme = f.read()


setup(
    name='github-automation',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    url='https://github.com/demisto/github-automation',
    license='MIT',
    author='Rony Kozakish & Dean Arbel',
    author_email='',
    description='GitHub automatic project manager tool',
    install_requires=[
        'click',
        'requests',
        'python-dateutil',
        'gql==3.0.0a5'
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    keywords=[
        "GitHub",
        "Project",
        "Manager",
        "github-automation",
        "project",
        "manage",
        "manager"
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires=">=3.7",
    entry_points={
        'console_scripts': ['github-automation = github_automation.cli.main:main']
    },
    classifiers=[
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
