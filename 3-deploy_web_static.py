#!/usr/bin/python3
"""
Fabric script based on the file 2-do_deploy_web_static.py that creates and
distributes an archive to the web servers

execute: fab -f 3-deploy_web_static.py deploy -i ~/.ssh/id_rsa -u ubuntu
"""

from fabric import task, Connection, SerialGroup
from datetime import datetime
import os

# Define your remote servers
env_hosts = ['ubuntu@3.83.255.189', 'ubuntu@3.82.143.28']

@task
def do_pack(c):
    """Generate a .tgz archive of web_static directory"""
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    archive = f"versions/web_static_{now}.tgz"

    os.makedirs("versions", exist_ok=True)
    result = c.local(f"tar -cvzf {archive} web_static")

    if result.ok:
        print(f" Archive created: {archive}")
        return archive
    else:
        print("Archive creation failed")
        return None

@task
def do_deploy(c, archive_path):
    """Deploys the archive to the web servers"""
    if not os.path.exists(archive_path):
        print(" Archive path doesn't exist.")
        return False

    file_name = archive_path.split("/")[-1]
    no_ext = file_name.split(".")[0]
    release_path = f"/data/web_static/releases/{no_ext}/"
    tmp_path = f"/tmp/{file_name}"

    try:
        c.put(archive_path, tmp_path)
        c.run(f"mkdir -p {release_path}")
        c.run(f"tar -xzf {tmp_path} -C {release_path}")
        c.run(f"rm {tmp_path}")
        c.run(f"mv {release_path}web_static/* {release_path}")
        c.run(f"rm -rf {release_path}web_static")
        c.run("rm -rf /data/web_static/current")
        c.run(f"ln -s {release_path} /data/web_static/current")
        print("  Deployment successful")
        return True
    except Exception as e:
        print(f" Deployment failed: {e}")
        return False

@task
def deploy(c):
    """Packs and deploys to all servers"""
    archive_path = do_pack(c)
    if archive_path is None:
        print(" Packaging failed")
        return False

    success = True
    for host in env_hosts:
        print(f" Connecting to {host}...")
        conn = Connection(host)
        if not do_deploy(conn, archive_path):
            success = False
    return success
