from django.test.utils import setup_test_environment
setup_test_environment()
from django.test import Client
import sys
import json
import io
from django.contrib.auth.models import User
try:
    c = Client()
    u, _ = User.objects.get_or_create(username='tester')
    c.force_login(u)
    from django.core.files.uploadedfile import SimpleUploadedFile
    f = SimpleUploadedFile("resume.pdf", b"%PDF-1.4...", content_type="application/pdf")
    res = c.post('/analyze/', {'jd_text': 'Software Engineer required', 'resume_file': f})
    print('STATUS CODE:', res.status_code)
    try:
        print('RESPONSE:', res.json())
    except:
        print('RAW:', res.content)
except Exception as e:
    import traceback
    traceback.print_exc()
