#!/usr/bin/python3
"""
Fabric script that distributes an archive to web servers
"""

from fabric import task, Connection
from os.path import exists

# Remote server IPs with SSH usernames
env_hosts = ['ubuntu@54.224.252.175', 'ubuntu@54.175.30.67']


def deploy_archive(c, archive_path):
    """Distributes an archive to one web server (Connection `c`)"""
    if not exists(archive_path):
        print("Archive does not exist.")
        return False

    try:
        file_n = archive_path.split("/")[-1]
        no_ext = file_n.split(".")[0]
        release_dir = f"/data/web_static/releases/{no_ext}/"
        tmp_path = f"/tmp/{file_n}"

        # Upload archive
        c.put(archive_path, tmp_path)

        # Create release directory and extract
        c.run(f"mkdir -p {release_dir}")
        c.run(f"tar -xzf {tmp_path} -C {release_dir}")

        # Clean up archive and restructure
        c.run(f"rm {tmp_path}")
        c.run(f"mv {release_dir}web_static/* {release_dir}")
        c.run(f"rm -rf {release_dir}web_static")

        # Update symbolic link
        c.run("rm -rf /data/web_static/current")
        c.run(f"ln -s {release_dir} /data/web_static/current")

        print(f"Successfully deployed to {c.host}")
        return True

    except Exception as e:
        print(f" Deployment failed on {c.host}: {e}")
        return False


@task
def do_deploy(c, archive_path):
    """Distribute the archive to all configured web servers"""
    results = []
    for host in env_hosts:
        print(f"🔁 Connecting to {host}...")
        conn = Connection(host)
        results.append(deploy_archive(conn, archive_path))

    return all(results)
