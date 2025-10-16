import unittest
from sfdx_utils import get_metadata_info

class TestCalculator(unittest.TestCase):

    def test_metadata_info_email_report_dashboard(self):
        self.assertEqual(get_metadata_info('force-app/main/default/email/Test/TestEmail.email-meta.xml'), ('EmailTemplate','Test/TestEmail'))
        self.assertEqual(get_metadata_info('force-app/main/default/reports/Test/TestReport.report-meta.xml'), ('Report','Test/TestReport'))
        self.assertEqual(get_metadata_info('force-app/main/default/dashboards/Test/TestDashboard.dashboard-meta.xml'), ('Dashboard','Test/TestDashboard'))
    
    def test_metadata_info_object(self):
        self.assertEqual(get_metadata_info('force-app/main/default/objects/TestObject/recordTypes/testRecordType.recordType-meta.xml'), ('RecordType','TestObject.testRecordType'))
    
    def test_metadata_info_lwc(self):
        self.assertEqual(get_metadata_info('force-app/main/default/lwc/test_lwc/test_lwc.js'),('LightningComponentBundle','test_lwc'))
    
    def test_metadata_info_customMetadata(self):
        self.assertEqual(get_metadata_info('force-app/main/default/customMetadata/TestCustomMetadata.testMetadata1.md-meta.xml'),('CustomMetadata','TestCustomMetadata.testMetadata1'))
    
    def test_metadata_info_other(self):
        self.assertEqual(get_metadata_info('force-app/main/default/profiles/TestProfile.profile-meta.xml'),('Profile','TestProfile'))

if __name__ == "__main__":
    unittest.main()
