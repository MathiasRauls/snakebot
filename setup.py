from setuptools import setup

setup(
    name="snake-bot",
    version="0.1.0",
    description="An AI trained to do nothing but play snake endlessly... 🐍",
    py_modules=["game"],  # your main file name
    entry_points={
        "console_scripts": [
            "snakebot=game:main",  # "snake" command runs game.py's main()
        ],
    },
	install_requires=[
		"pygame",
		"numpy",
		"torch",
		"torchvision",
	],
)