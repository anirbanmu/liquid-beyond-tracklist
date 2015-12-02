# -*- coding: utf-8 -*-

import sys, os, json, re, pafy, mutagen.easyid3, multiprocessing.dummy
from collections import namedtuple
from mutagen.easyid3 import EasyID3

if len(sys.argv) < 2:
    sys.exit('Please provide a JSON filepath which contains key -> value mappings of Filepath of MP3 -> YouTube URL.')

TrackDescriptor = namedtuple('TrackDescriptor', ['index', 'hours', 'minutes', 'seconds', 'artist', 'title'])

def track_entry(t):
    hours = int(t.hours)
    minutes = int(t.minutes) + hours * 60
    seconds = int(t.seconds)
    return '  TRACK %02d AUDIO\n    TITLE "%s"\n    PERFORMER "%s"\n    INDEX 01 %02d:%02d:00' % (t.index, t.title.strip(), t.artist, minutes, seconds)

def get_tracks_text(track_text):
    tracks = re.findall(u'^((?:\d{1,2}:){1,2})(\d{1,2})\s+(.+?)\s*(?:-|–)\s*(.+)$', track_text, re.MULTILINE)

    # Was every line that begins with a time stamp formatted correctly?
    if len(tracks) != len(re.findall(u'^(?:\d{1,2}:){1,2}(\d{1,2}).+$', track_text, re.MULTILINE)):
        return None

    track_entries = []
    for track in tracks:
        hours_minutes = [x for x in track[0].split(':') if x != '']
        hours_minutes = ('00', hours_minutes[0]) if len(hours_minutes) == 1 else tuple(hours_minutes)
        track_entries.append(track_entry(TrackDescriptor(len(track_entries) + 1, *(hours_minutes + track[1:]))))
    return '\n'.join(track_entries) if track_entries else None

def get_header_text(mp3):
    mp3_meta = EasyID3(mp3)
    return 'PERFORMER "%s"\nTITLE "%s"\nFILE "%s" WAVE\n' % (mp3_meta['artist'][0], mp3_meta['title'][0], os.path.basename(mp3))

Mp3YoutubePair = namedtuple('Mp3_Yt_Pair', ['mp3', 'yt'])

def generate_cue_sheet(p):
    possible_path = p.yt.replace('~', os.path.expanduser('~'))
    if os.path.isfile(possible_path):
        with open(possible_path, 'r') as f:
            track_text = f.read().decode('utf-8')
    else:
        track_text = pafy.new(p.yt, basic=False, gdata=True, size=False).description

    header = get_header_text(p.mp3)
    tracks = get_tracks_text(track_text)
    if header and tracks:
        return header + tracks
    return None

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        mp3_yt_pairs = [Mp3YoutubePair(mp3, yt) for mp3,yt in json.load(f).iteritems()]

        results = multiprocessing.dummy.Pool(processes=4).map(generate_cue_sheet, mp3_yt_pairs)

        for i,pair in enumerate(mp3_yt_pairs):
            if results[i]:
                cue_sheet_path = os.path.join(os.path.dirname(os.path.realpath(pair.mp3)), os.path.splitext(os.path.basename(pair.mp3))[0] + '.cue')
                with open(cue_sheet_path, 'w') as cue:
                    cue.write(results[i].encode('utf-8'))

        print 'Succeeded:\n' + '\n'.join([os.path.basename(mp3_yt_pairs[i].mp3) for i,r in enumerate(results) if r])
        print 'Failed:\n' + '\n'.join([os.path.basename(mp3_yt_pairs[i].mp3) for i,r in enumerate(results) if not r])