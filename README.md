# hoard Media Server

\* It's actually not so terrible now \*

# Bare Bones but FAST Media Server for Private Networks

<img width="1702" height="963" alt="image" src="https://github.com/user-attachments/assets/fb78ad80-e100-4e42-abb8-908865629c7d" />

* Install Python 3.11 or newer.
* Make sure to install it to your system's %PATH% variable
* Rename *config.json.example* to *config.json*
* Edit *config.json* to suit your needs

You *ABSOLUTELY MUST* modify the line to point to your pictures directory:

    "root": "N:\\Pictures",

Install pillow:

    pip install pillow

To start the server:

    python main.py

* Optionally, for video thumbnails, download *ffmpeg.exe* (start server to see instructions)
* Optionally, for Canon Raw file support, download *dcraw.exe* (start server to see instructions)

