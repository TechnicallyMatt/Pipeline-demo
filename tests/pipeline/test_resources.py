from src.pipeline.resources import SFTPResource
import pytest


@pytest.fixture
def files():
    return {
        'root_file.dat': 'root file contents',
        'tmp': {},
        'a_dir': {'somefile.txt': "File content"},
        'listed_dir': {
            'a': 'a_contents',
            'b': 'b_contents',
            'subdir': {'sub_c': 'sub_c_contents', 'subsubdir': {'subsub_d': 'subsub_d_contents'}},
        },
    }


class TestSFTPResource:
    @staticmethod
    def test_open_close_connection(sftpserver, files):
        with sftpserver.serve_content(files):
            res = SFTPResource(hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw')
            assert res.connected is False
            res.connect()
            assert res.connected is True
            res.close()
            assert res.connected is False

    @staticmethod
    def test_put_file(sftpserver, files):
        with sftpserver.serve_content(files):
            with SFTPResource(
                hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw'
            ) as sftp_resource:
                assert not sftp_resource.exists('/tmp/somefile.txt')
                with open('/tmp/somefile.txt', 'w+') as f:
                    f.write('This is a file!')
                sftp_resource.put_file('/tmp/somefile.txt')
                assert sftp_resource.exists('/tmp/somefile.txt')

    @staticmethod
    def test_get_file(sftpserver, files):
        with sftpserver.serve_content(files):
            with SFTPResource(
                hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw'
            ) as sftp_resource:

                assert sftp_resource.exists('/a_dir/somefile.txt')
                sftp_resource.put_file('/tmp/somefile.txt')
                assert sftp_resource.exists('/tmp/somefile.txt')

    @staticmethod
    @pytest.mark.parametrize(
        'test_file',
        [
            '/root_file.dat',
            '/a_dir/somefile.txt',
            'listed_dir/a',
            'listed_dir/subdir/sub_c',
            '/listed_dir/subdir/subsubdir/subsub_d',
        ],
    )
    def test_exists(sftpserver, files, test_file):
        with sftpserver.serve_content(files):
            with SFTPResource(
                hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw'
            ) as sftp_resource:
                assert sftp_resource.exists(test_file)

    @staticmethod
    @pytest.mark.parametrize(
        'test_file',
        [
            'root_file.data',
            '/b_dir/somefile.txt',
            'listed_dir/c',
            'listed_dir/subdir/b',
            '/listed_dir/subdir/subsubdir/sub_c',
        ],
    )
    def test_not_exists(sftpserver, files, test_file):
        with sftpserver.serve_content(files):
            with SFTPResource(
                hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw'
            ) as sftp_resource:
                assert not sftp_resource.exists(test_file)

    @staticmethod
    @pytest.mark.parametrize(
        'ls_params, expected_output',
        [
            ({'path': 'listed_dir', 'include_dirs': False}, ['a', 'b']),
            ({'path': 'listed_dir', 'include_dirs': True}, ['a', 'b', 'subdir']),
            ({'path': '/', 'include_dirs': False}, ['root_file.dat']),
            ({'path': '/', 'include_dirs': True}, ['root_file.dat', 'tmp', 'a_dir', 'listed_dir']),
        ],
    )
    def test_list(sftpserver, files, ls_params, expected_output):
        with sftpserver.serve_content(files):
            with SFTPResource(
                hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw'
            ) as sftp_resource:
                assert [x.filename for x in sftp_resource.ls(**ls_params)] == expected_output

    @staticmethod
    @pytest.mark.skip(reason='Unfinished - hangs near completion - fix tree()?')
    def test_tree(sftpserver, files):
        with sftpserver.serve_content(files):
            with SFTPResource(
                hostname=sftpserver.host, port=sftpserver.port, username='user', password='pw'
            ) as sftp_resource:
                sftp_resource.tree('listed_dir')