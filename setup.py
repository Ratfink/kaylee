from setuptools import setup

with open("README.rst") as file:
    long_description = file.read()

setup(
    name = "KayleeVC",
    version = "0.1.1",
    author = "Clayton G. Hobbs",
    author_email = "clay@lakeserv.net",
    description = ("Somewhat fancy voice command recognition software"),
    license = "GPLv3+",
    keywords = "voice speech command control",
    url = "https://github.com/Ratfink/kaylee",
    packages = ['kayleevc'],
    long_description = long_description,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later "
            "(GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Topic :: Home Automation"
    ],
    install_requires=["requests"],
    data_files = [
        ("/usr/share/kaylee", ["data/icon_inactive.png", "data/icon.png",
            "options.json.tmp"])
    ],
    entry_points = {
        "console_scripts": [
            "kaylee=kayleevc.kaylee:run"
        ]
    }
)
