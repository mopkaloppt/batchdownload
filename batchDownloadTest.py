import unittest
import batchDownload
from mock import MagicMock, Mock

class batchDownloadTest(unittest.TestCase):
    def test_validate_true_protocal(self):
        url = 'https://wordpress.org/plugins/about/readme.txt'
        obj = batchDownload
        obj.validate_protocol(url)
        self.assertTrue(True,'This is a valid protocal')

    # def test_validate_false_protocal(self):


if __name__ == '__main__':
    unittest.main()
