import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libgen_api",
    packages=["libgen_api"],
    version="1.0.0",
    description="Search Library genesis by Title or Author",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/harrison-broadbent/libgen-api",
    download_url="https://github.com/harrison-broadbent/libgen-api/archive/v1.0.0.tar.gz",
    author="Harrison Broadbent",
    author_email="mail@harrisonbroadbent.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords=["libgen search", "libgen api", "search libgen", "search library genesis"],
    install_requires=["bs4", "requests", "lxml"],
)
