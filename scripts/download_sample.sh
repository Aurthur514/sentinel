#!/usr/bin/env bash
set -e
mkdir -p test_videos
cd test_videos
if [ ! -f sample.mp4 ]; then
  echo "Downloading sample video..."
  curl -L -o sample.mp4 https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4
  echo "Downloaded test_videos/sample.mp4"
else
  echo "sample.mp4 already exists"
fi
