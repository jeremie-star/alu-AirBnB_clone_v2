#!/usr/bin/python3
"""
Fabric script to generate .tgz archive
execute: fab -f 1-pack_web_static.py do_pack
"""

from fabric import task
from datetime import datetime
import os

@task
def do_pack(c):
    """
    Generate a .tgz archive from the web_static folder
    """
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    archive = f'versions/web_static_{now}.tgz'
    os.makedirs("versions", exist_ok=True)
    result = c.local(f'tar -cvzf {archive} web_static')

    if result.ok:
        print(f"Archive created: {archive}")
        return archive
    else:
        print(" Failed to create archive")
        return None
