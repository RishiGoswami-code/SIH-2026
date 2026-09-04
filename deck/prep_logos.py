# -*- coding: utf-8 -*-
"""
Fetches and normalises the technology logos used on the Technical Approach
slide: downloads each source image, converts to RGBA, drops a solid white
background where the source has no alpha, trims transparent margins and caps
the long edge at 256 px.

The prepared PNGs are committed under deck/assets/logos, so this only needs
re-running to add a logo or refresh a source. Requires network access.

    python prep_logos.py

Sources
  python, cpp, nvidia, pytorch, opencv, docker, ubuntu
      github.com/github/explore — topic artwork
  ros
      commons.wikimedia.org — "Robot Operating System logo.svg", rendered to
      PNG by the MediaWiki thumbnailer

Logos are the trademarks of their respective owners and are used nominatively
to identify the technology stack. See drishti-ugv/REFERENCES.md section 6.1.
"""
import io
import json
import os
import urllib.request

from PIL import Image

DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logos")

GH_TOPIC = "https://raw.githubusercontent.com/github/explore/main/topics/{0}/{0}.png"
WM_API = ("https://commons.wikimedia.org/w/api.php?action=query"
          "&titles=File:Robot%20Operating%20System%20logo.svg"
          "&prop=imageinfo&iiprop=url&iiurlwidth=512&format=json")

UA = {"User-Agent": "drishti-ugv-logo-prep/1.0 (SIH 2026 PS 26126)"}
MAX_EDGE = 256
WHITE_CUT = 244          # channel value above which a pixel counts as background


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def ros_thumb_url():
    """Resolve the current PNG thumbnail URL for the ROS logo SVG."""
    pages = json.loads(get(WM_API))["query"]["pages"]
    return next(iter(pages.values()))["imageinfo"][0]["thumburl"]


def clean(raw):
    im = Image.open(io.BytesIO(raw)).convert("RGBA")

    # No usable alpha? knock out a near-white background.
    if im.getchannel("A").getextrema()[0] == 255:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, _ = px[x, y]
                if r > WHITE_CUT and g > WHITE_CUT and b > WHITE_CUT:
                    px[x, y] = (r, g, b, 0)

    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
    return im


def main():
    os.makedirs(DST, exist_ok=True)

    sources = {n: GH_TOPIC.format(n) for n in
               ("python", "cpp", "nvidia", "pytorch", "opencv", "docker", "ubuntu")}
    sources["ros"] = ros_thumb_url()

    for name, url in sorted(sources.items()):
        out = clean(get(url))
        out.save(os.path.join(DST, name + ".png"))
        print("%-10s %-9s %s" % (name, "%dx%d" % out.size, url.split("?")[0]))


if __name__ == "__main__":
    main()
