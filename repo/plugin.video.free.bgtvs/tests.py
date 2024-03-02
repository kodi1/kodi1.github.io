
import os
import unittest
import tempfile
from resources.lib.assets import DbAsset

class Tests(unittest.TestCase):
    
    def setUp(self):
        self.asset = DbAsset(
            temp_dir=tempfile.gettempdir()
            , url='https://github.com/hristo-genev/uWsgiApps/raw/master/freetvandradio/tvs.sqlite3'
            # , log_delegate=print
            )        
        
    def test_is_expired_returns_true_when_asset_is_missing(self):
        '''
        is_expired should return true when the asset file is missing
        '''  
        self.assertFalse(self.asset.is_expired())
        
        
    def test_is_expired_returns_true_when_asset_is_older_than_24_hours(self):
        '''
        is_expired returns true when the asset file is created more than 24 hours ago
        '''
        os.utime(self.asset.file_path, (1650463529, 1650463529))
        self.assertTrue(self.asset.is_expired())
        
            
    def test_update_downloads_asset_when_expired(self):
        '''
        update downloads asset from internet when asset is expired
        '''
        if os.path.exists(self.asset.file_path):
            os.remove(self.asset.file_path)
        self.assertFalse(os.path.isfile(self.asset.file_path))
        
        if self.asset.is_expired():
            self.asset.update()

        self.assertTrue(os.path.isfile(self.asset.file_path))
        self.assertFalse(self.asset.is_expired())
        
    def test_force_update(self):
        '''
        update downloads asset from internet when asset is expired
        '''
        self.assertTrue(os.path.isfile(self.asset.file_path))       
        self.asset.update()

        self.assertTrue(os.path.isfile(self.asset.file_path))
        self.assertFalse(self.asset.is_expired())    
        
    def test_is_expired_returns_false_when_asset_is_not_older_than_24_hours(self):
        '''
        is_expired returns true when the asset file is created more than 24 hours ago
        '''
        self.assertTrue(os.path.isfile(self.asset.file_path))
        self.assertFalse(self.asset.is_expired())
        
    
    def test_using_local_file(self):
        '''
        is_expired returns true when the asset file is created more than 24 hours ago
        '''
        self.asset = DbAsset(
            file_path=os.path.join(tempfile.gettempdir(), 'tvs.sqlite3')
        )
        self.assertFalse(self.asset.is_expired())
            
        
if __name__ == '__main__':
    unittest.main()