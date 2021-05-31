#!/usr/bin/python


import getopt
import json
import math
import sys
import urllib.request
import re

from sources.Writer import ConsoleWriter, FileWriter

YOUTUBE_KEY = "AIzaSyAp1IRyb1FWWg1ixdES8HUxnVTgUdAjmcU&playlistId=PL8YZyma552VcePhq86dEkohvoTpWPuauk"


class YouTubeApi:

    def __init__(self, key) -> None:
        super().__init__()
        self.key = key

    def playlistItems_list(self, playlistId, maxResults = 1000):
        link = "https://www.googleapis.com/youtube/v3/playlistItems?key=" + \
               self.key \
               + "&playlistId=" + playlistId \
               + "&maxResults=" + str(maxResults) \
               + "&part=snippet"

        return urllib.request.urlopen(link)

    def videos_list(self, ids):
        link = "https://www.googleapis.com/youtube/v3/videos?key=" + self.key \
               + "&id=" + ",".join(ids) \
               + "&part=contentDetails"

        return urllib.request.urlopen(link)


class YouTubeVideo:

    def __init__(self, id, title) -> None:
        super().__init__()
        self.id = id
        self.link = f"https://youtu.be/{id}"
        self.title = title
        self._duration = None

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    def time(self):
        duration = self.duration

        hours = math.floor(duration / 3600)
        duration = duration - hours * 3600
        minutes = math.floor(duration / 60)
        seconds = duration - minutes * 60

        time = ""
        if hours > 0:
            time = time + str(hours) + ":"

        time = time + str(f"{minutes:02d}") + ":" + str(f"{seconds:02d}")

        return time

    def beautify(self):
        return "[" + self.title + "](" + self.link + ") " + self.time()


def parseTime(time):
    seconds = 0

    hour_match = re.search("\d+H", time)
    if hour_match:
        seconds += int(hour_match.group()[:-1]) * 3600

    minute_match = re.search("\d+M", time)
    if minute_match:
        seconds += int(minute_match.group()[:-1]) * 60

    seconds_match = re.search("\d+S", time)
    if seconds_match:
        seconds += int(seconds_match.group()[:-1])

    return seconds


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "f:i:", ["id=", "file="])
    except getopt.GetoptError:
        print('ERROR while parsing arguments')
        sys.exit(2)

    output = None

    for opt, arg in opts:
        if opt in ('-i', '--id'):
            id = arg
        elif opt in ('-f', '--file'):
            output = arg

    if output is None:
        writer = ConsoleWriter()
    else:
        writer = FileWriter(output)

    api = YouTubeApi(YOUTUBE_KEY)
    videos = {}

    with api.playlistItems_list(id) as playlist_url:
        playlist_resp = json.loads(playlist_url.read().decode())
        for item in playlist_resp["items"]:
            snippet = item["snippet"]
            title = snippet["title"]
            id = snippet["resourceId"]["videoId"]
            videos[id] = YouTubeVideo(id, title)

    with api.videos_list(videos.keys()) as videos_url:
        videos_resp = json.loads(videos_url.read().decode())
        for item in videos_resp["items"]:
            video = videos[item["id"]]
            duration = item["contentDetails"]["duration"]
            video.duration = parseTime(duration) - 1

        writer.write("\"title\",\"link\",\"time\",\"todoist\"")

        showedVideos = []

        for item in videos.values():
            if item.duration is None:
                print(
                    f"WARNING: Video with id {item.id} is hidden because it is "
                    f"private video!")
                continue
            else:
                showedVideos.append(item)

        for item in showedVideos:
            writer.write("\""
                         + "\",\"".join([item.title, item.link,
                                         item.time(), item.beautify()])
                         + "\"")


if __name__ == "__main__":
    main(sys.argv[1:])
