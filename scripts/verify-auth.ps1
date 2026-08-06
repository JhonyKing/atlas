$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot\..\apps\backend
try {
  & .\.venv\Scripts\python.exe -m pytest tests/unit/auth tests/contract/auth tests/integration/auth tests/integration/security/test_cross_user_resources.py tests/integration/security/test_private_upload_pipeline.py -q
} finally {
  Pop-Location
}
