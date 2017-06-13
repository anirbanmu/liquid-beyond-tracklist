# liquid-beyond-tracklist
Generates cue sheet files (.cue) for the Liquid &amp; Beyond mixes

#### Dependencies
+ [pafy](https://pypi.python.org/pypi/pafy/0.4.2)
+ [mutagen](https://pypi.python.org/pypi/mutagen/1.31)

#### Configuration
+ JSON file that has the file paths of Liquid & Beyond mixes mapped to their corresponding YouTube links. (See default.json to see an example)


#### Usage
+ `python generate_cue_sheet.py default.json`
