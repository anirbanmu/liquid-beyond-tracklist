# -*- coding: utf-8 -*-

import sys, os, json, re, pafy, mutagen.easyid3
from collections import namedtuple
from mutagen.easyid3 import EasyID3

if len(sys.argv) < 2:
    sys.exit('Please provide a JSON filepath which contains key -> value mappings of Filepath of MP3 -> YouTube URL.')

track_descriptor = namedtuple('track_descriptor', ['index', 'hours', 'minutes', 'seconds', 'artist', 'title'])

def track_entry(t):
    hours = int(t.hours)
    minutes = int(t.minutes) + hours * 60
    seconds = int(t.seconds)
    return '  TRACK %02d AUDIO\n    TITLE "%s"\n    PERFORMER "%s"\n    INDEX 01 %02d:%02d:00' % (t.index, t.title.strip(), t.artist, minutes, seconds)

def get_tracks_text(yt_url):
    video_info = pafy.new(yt_url)
    tracks = re.findall(u'^(\d\d):(\d\d):(\d\d)\s+(.+)\s+(?:-|–)\s+(.+)$', video_info.description, re.MULTILINE)

    # Was every line that begins with a time stamp formatted correctly?
    if len(tracks) != len(re.findall(u'^(\d\d):(\d\d):(\d\d).+$', video_info.description, re.MULTILINE)):
        return None

    track_entries = []
    for track in tracks:
        track_entries.append(track_entry(track_descriptor(len(track_entries) + 1, *track)))
    return '\n'.join(track_entries) if track_entries else None

def get_header_text(mp3):
    mp3_meta = EasyID3(mp3)
    return 'PERFORMER "%s"\nTITLE "%s"\nFILE "%s" WAVE\n' % (mp3_meta['artist'][0], mp3_meta['title'][0], os.path.basename(mp3))

def generate_cue_sheet(yt_url, mp3):
    return get_header_text(mp3) + get_tracks_text(yt_url)

with open(sys.argv[1], 'r') as f:
    success = []
    failure = []
    for mp3, yt in json.load(f).iteritems():
        try:
            cue_sheet_text = generate_cue_sheet(yt, mp3).encode('utf-8')
            cue_sheet_path = os.path.join(os.path.dirname(os.path.realpath(mp3)), os.path.splitext(os.path.basename(mp3))[0] + '.cue')
            with open(cue_sheet_path, 'w') as cue:
                cue.write(cue_sheet_text)
                success.append(mp3)
        except:
            failure.append(mp3)
    print "Succeeded:"
    for s in success:
        print '    ' + os.path.basename(s)
    print "Failed:"
    for f in failure:
        print '    ' + os.path.basename(f)