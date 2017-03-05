# -*- coding: utf-8 -*-
from urllib import urlretrieve, urlcleanup
from urllib2 import Request, urlopen, URLError
from urlparse import urlparse
import os
import paramiko
from multiprocessing import Pool
from progress.bar import Bar


# Specify where you want the file to be saved locally here
# Revise this to prompt user to specify destination on command prompt
destination = '/Users/maprangsuwanbubpa/Desktop/batchDownload/'


def validate_protocol(url):
    req = Request(url)
    if req.has_data() is None:
        print ' '
        print 'The given URL contains no data'
        return

    scheme = ['http', 'https', 'ftp', 'sftp']
    protocols = set(scheme)
    protocol = urlparse(url)

    if protocol.scheme in protocols and protocol.scheme == 'sftp':
        print ' '
        # Perhaps need to use urllib user_prompt
        username = raw_input('Enter username: ')
        password = raw_input('Enter password: ')
        sftp_download(url, username, password)
    elif protocol.scheme in protocols:
        if not is_too_large(url):
            batch_download(url)
        else:
            buffer_stream(url)
    else:
        print ' '
        print 'The given URLs do not have valid protocols'
        return False


def is_too_large(url):
    req = Request(url)
    response = urlopen(req)
    resp_metadata = response.info()['Content-Length']
    if resp_metadata >= 536870912:  # 0.5GB or more
    # if resp_metadata >= 1073741824:  # 1GB or more
        return True
    else:
        return False


def buffer_stream(url):
    print ' '
    print 'Buffering...'
    response = urlopen(url)
    buffer_chunk = 4096  # use os.stat(path).st_blksize to determine a good chunk size for os stream
    with open(get_local_path(url), 'wb') as f:
        while True:
            chunk = response.read(buffer_chunk)
            if not chunk:
                break
            f.write(chunk)
    response.close()


def batch_download(url):
    req = Request(url)
    try:
        print ' '
        print 'Start downloading...'
        response = urlopen(req)
    except URLError as e:
        # No network connection or Invalid URL or The specified server doesn't exist.
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        # HTTP Response that is not 200.
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        # Retrieve a redirected URL, if there is one.
        real_url = response.geturl()
        print real_url
        saved_to = get_local_path(real_url)
        urlretrieve(real_url, saved_to)

        meta_data = response.info()['Content-Length']
        file_on_disk = os.stat(saved_to).st_size
        print 'Content-Length: ' + meta_data
        print 'File on Disk after Download: ' + str(file_on_disk)

        remove_partially_downloaded(real_url, response, saved_to, file_on_disk)

        urlcleanup()
    return


def remove_partially_downloaded(url, meta_data, local_path_to_file, file_on_disk):
    # meta_data = response.info()['Content-Length']
    # file_on_disk = os.stat(local_path_to_file).st_size
    print 'Content-Length: ' + meta_data
    print 'File on Disk after Download: ' + str(file_on_disk)

    partial_download = int(meta_data) - file_on_disk

    if partial_download > 0:
        print 'The following partially downloaded file ' + get_filename_from_url(url) + ' will be removed'
        os.remove(local_path_to_file)
    else:
        return


def sftp_download(url, user, passwrd):
    print ' '
    print 'Start downloading sftp...'
    ssh = paramiko.SSHClient()
    # automatically adds server's host keys without prompting,
    # assuming that for this assignment, security is not concerned.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(url, username=user, password=passwrd)
        ssh.connect('10.170.21.93', username="abhishek", password="@bhishek$")
    except paramiko.SSHException:
        print 'Connection Failed'

    sftp = ssh.open_sftp()

    if not is_too_large(url):
        remote_path = urlparse(url).path
        sftp.get(remote_path, get_local_path(url), callback=None)
    else:
        buffer_stream(url)

    sftp.close()
    ssh.close()


def get_filename_from_url(url):
    filename = url.split('/')[-1].split('#')[0].split('?')[0]
    # Just in case the URL path doesn't specify the file name
    # set the filename default to no_name
    if len(filename) <= 0:
        filename = 'no_name'
    return filename


def get_local_path(url):
    return destination + get_filename_from_url(url)


def main():
    urls = raw_input('Enter your URLs separated by comma with no space (e.g. url1,url2,url3): ')
    urls = urls.split(',')
    print urls

    bar = Bar('Processing', max=len(urls), fill='█', suffix='%(percent)d%%')
    pool = Pool()
    for i in pool.imap(validate_protocol, urls):
        # Sequential version
        # for url in urls:
        #     validate_protocol(url)
        bar.next()
    bar.finish()


if __name__ == "__main__":
    main()