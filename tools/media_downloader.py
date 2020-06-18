from pathlib import Path
import os
import shutil


downloads = [
    {
        'gcloud': 'gs://clipperstorage/youtube/thumbnails',
        'dir_path': Path('../videos/thumbnails')
    },

    {
        'gcloud': 'gs://clipperstorage/youtube/video/intro.mov',
        'file_path': Path('../videos/intro.mov')
    },

    {
        'gcloud': 'gs://clipperstorage/youtube/video/outro.mp4',
        'file_path': Path('../videos/outro.mp4')
    }
]

for download in downloads:
    if 'dir_path' in download.keys():
        if os.path.exists(download['dir_path']):
            shutil.rmtree(download['dir_path'])
        
        os.mkdir(download['dir_path'])
        cmd = 'gsutil cp -r {} {}'.format(download['gcloud'], download['dir_path'])
        os.system(cmd)
    elif 'file_path' in download.keys():
        if os.path.exists(download['file_path']):
            os.remove(download['file_path'])
        
        cmd = 'gsutil cp -r {} {}'.format(download['gcloud'], download['file_path'])
        os.system(cmd)
