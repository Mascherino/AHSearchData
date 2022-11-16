import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MoMBot",
    version="1.0.0",
    author="Keedosuul",
    author_email="code@keedosuul.de",
    description="A python based discord bot for providing useful commands for Million on Mars",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    install_requires=["requests",
                      "certifi>=2017.4.17",
                      "chardet",
                      "idna",
                      "urllib3",
                      "discord.py",
                      "pyourls3",
                      "apscheduler"]
)