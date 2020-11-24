import setuptools

setuptools.setup(
    name="PDF Highlighting",
    version="0.1",
    packages=setuptools.find_packages(),
    author="indico",
    author_email="scott.levin@indico.io",
    tests_require=["pytest>=5.2.1"],
    python_requires=">=3.6",
    install_requires=[
        "astroid==2.3.3",
        "attrs==19.3.0",
        "certifi==2020.4.5.1",
        "chardet==3.0.4",
        "Faker==4.0.3",
        "fonttools==4.7.0",
        "idna==2.9",
        "indico-client>=3.1.7",
        "isort==4.3.21",
        "lazy-object-proxy==1.4.3",
        "mccabe==0.6.1",
        "msgpack==1.0.0",
        "msgpack-numpy==0.4.4.3",
        "numpy>=1.15.4",
        "pdf-annotate==0.11.0",
        "pdfrw==0.4",
        "Pillow==7.1.1",
        "PyMuPDF==1.16.17",
        "python-dateutil==2.8.1",
        "requests==2.23.0",
        "six==1.14.0",
        "text-unidecode==1.3",
        "typed-ast==1.4.1",
        "urllib3==1.25.8",
        "wrapt==1.11.2",
    ],
)
