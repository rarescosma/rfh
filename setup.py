from setuptools import setup
from rfh.version import __version__

desc = "Rofi helpers for tmux, tuya, ..."

setup(
    name="rfh",
    version=__version__,
    description=desc,
    author="Rares Cosma",
    author_email="rares@getbetter.ro",
    keywords="rofi tmux tuya alacritty i3 manage switch",
    packages=["rfh"],
    license="MIT",
    install_requires=[
        "python-rofi==1.0.1",
        "sh",
        "i3ipc>=2.0.1",
        "click",
        "tuyapy==0.1.4",
        "lenses==1.1.0",
        "xdg",
        "requests==2.26.0"
    ],
    entry_points="""
        [console_scripts]
        rfh=rfh.main:main
    """,
    zip_safe=False,
)
