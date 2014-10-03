#coding: utf-8

from configobj import ConfigObj
from guessit import guess_file_info
from opster import command
import os
import re
import shutil
import subprocess

HOME = os.getenv('USERPROFILE') or os.getenv('HOME')
CONF_PATH = os.path.join(HOME, '.tvsortrc')

def write_template_config():
    conf = ConfigObj(
        CONF_PATH,
        create_empty=True,
        write_empty_values=True,
    )

    conf['tv_shows_path'] = '/mnt/hdd0/plex/TV/'
    conf['move_files'] = True
    conf['delete_files'] = False

    conf.write()

def get_conf():
    if os.path.exists(CONF_PATH):
        return ConfigObj(CONF_PATH)
    else:
        write_template_config()
        print("Wrote example config to {0}".format(CONF_PATH))
        exit(0)

CONF = get_conf()

def not_sure(path):
    print("I'm not quite sure what {0} is".format(path))

def format_show(name):
    return re.sub(r'[^A-z0-9]+', '', name.title().replace(" ", "_"))

def season_path(guess):
    tv_dir = CONF['tv_shows_path']
    show = format_show(guess['series'])
    season = "S" + str(guess['season']).zfill(2)
    path = os.path.join(tv_dir, show, season)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def episode_filename(guess):
    title = format_show(guess['series']).replace("_", ".")
    season = str(guess['season']).zfill(2)
    episode = str(guess['episodeNumber']).zfill(2)
    container = guess['container']
    return "{title}.S{season}E{episode}.{container}".format(**locals())

def make_guess(path):
    guess = guess_file_info(path)
    try:
        guess['episodeNumber']
        guess['season']
        guess['series']
        guess['container']
        guess['type'] == 'episode'
        print("Found {0}".format(episode_filename(guess)))
        return guess
    except Exception as e:
        print("Not sure what {0} is ({1})".format(path, e))
        return False

def is_rar(path):
    exts = ['.r00', '.part1.rar', '.part01.rar', '.part001.rar',]
    return any(path.lower().endswith(ext) for ext in exts)

def is_video(path):
    exts = ['.mkv', '.avi', '.mp4', '.wemb', '.ogg', '.mov',
            '.wmv', '.m4v', '.m4p', '.mpg', '.mpeg',]
    return any(path.lower().endswith(ext) for ext in exts)

def get_files(path):
    files = []
    if os.path.isfile(path):
        files.append(path)

    for root, dirs, walk_files in os.walk(path):
        for f in walk_files:
            fpath = os.path.join(root, f)
            if "sample" in fpath.lower():
                continue
            else:
                files.append(fpath)
    
    return sorted(files)

@command()
def main(path):
    "Sort TV show episode(s)"
    root_path = path
    for path in get_files(root_path):
        if is_rar(path):
            directory = os.path.dirname(path)
            print("Extracting {0}".format(path))
            process = subprocess.Popen(['unrar', 'x', '-y', path, directory],
                                       stdout=open(os.devnull, 'wb'))
            process.wait()
    
    for path in get_files(root_path):
        if is_video(path):
            guess = make_guess(path)
            if guess:
                s_path = season_path(guess)
                ep_name = episode_filename(guess)
                ep_path = os.path.join(s_path, ep_name)
                if CONF['move_files']:
                    shutil.move(path, ep_path)
                else:
                    shutil.copy(path, ep_path)
    if CONF['delete_files']:
        if os.path.exists(root_path):
            shutil.rmtree(root_path)
