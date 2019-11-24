#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Media file sorter:
# Scan all files on source_path, creates subdirectories on destination path
# then copies there files according creation date
#
# 1. source path to scan
# 2. destination path where to store sorted media

import sys
import shutil
import exiftool
import locale
from datetime import date
from pathlib import Path, PurePath
from glob import glob

def usage():
    print("media_sorter <source_path> <destination_path>")
    exit(0)

class DirScanner(object):
    def __init__(self, path):
        self.path = path
    
    def get_images(self):
        search_path = "%s/**/*.jpg" % self.path
        return glob(search_path, recursive=True)

    def get_videos(self):
        search_path = "%s/**/*.mp4" % self.path
        return glob(search_path, recursive=True)


class MediaSorter(object):
    def __init__(self, mediafiles):
        locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
        self.mediafiles = mediafiles

    def __get_meta_data(self):
        if not self.mediafiles:
            return []

        with exiftool.ExifTool() as et:
            return et.get_metadata_batch(self.mediafiles)

    def __get_create_date(self, datestr):
        return date.fromisoformat(datestr.split(" ")[0].replace(":","-"))

    def __get_month_name(self, dt):
        dt.strftime()

    def __copy_sorted_file(self, source_file, datestr, sorted_path):
        create_date_obj = self.__get_create_date(datestr)

        year = "%s" % create_date_obj.year
        month = "%02d-%s" % (create_date_obj.month, create_date_obj.strftime("%B"))
        sorted_path = PurePath(sorted_path).joinpath(year, month)
        Path(sorted_path).mkdir(parents=True, exist_ok=True)

        shutil.copy(source_file, sorted_path)

    def __sort_media(self, dest_path, media_path, media_create_tag):
        sorted_path = PurePath(dest_path).joinpath(media_path)
        unsorted_path = PurePath(dest_path).joinpath(media_path, "unsorted")
        Path(unsorted_path).mkdir(parents=True, exist_ok=True)

        metadata = self.__get_meta_data()
        for md in metadata:
            try:
                source_file = md["SourceFile"]
                create_date_str = md[media_create_tag]
                self.__copy_sorted_file(source_file, create_date_str, sorted_path)
                
            except KeyError:
                shutil.copy(md["SourceFile"], unsorted_path)

            except Exception as e:
                print("[%s] Error: %s" % (md["SourceFile"], e))
                shutil.copy(md["SourceFile"], unsorted_path)

    def sort_images(self, dest_path):
        self.__sort_media(dest_path, "pictures", "EXIF:DateTimeOriginal")

    def sort_videos(self, dest_path):
        self.__sort_media(dest_path, "videos", "QuickTime:CreateDate")


if __name__ == "__main__":

    if len(sys.argv) < 3:
        usage()

    source_path = sys.argv[1]
    dest_path = sys.argv[2]

    ds = DirScanner(source_path)
    img_files = ds.get_images()
    vid_files = ds.get_videos()

    imgSorter = MediaSorter(img_files)
    imgSorter.sort_images(dest_path)

    vidSorter = MediaSorter(vid_files)
    vidSorter.sort_videos(dest_path)
