[app]

title = XT-ScalperPro
package.name = xtscalperpro
package.domain = com.trading

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0

requirements = python3,kivy==2.3.0,ccxt,pandas,gradio,aiohttp,aiofiles,certifi,charset-normalizer,idna,multidict,yarl,aiosignal,frozenlist,attrs,typing-extensions,numpy,python-dateutil,pytz,requests,urllib3,setuptools,pillow,cryptography,pycparser,cffi,python-dotenv,aiohappyeyeballs,pydantic,pydantic-core,fastapi,starlette,uvicorn,httpx,httpcore,anyio,sniffio,h11,websockets

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 31
android.minapi = 21
android.ndk = 25b
android.gradle_dependencies = 

android.enable_androidx = True

android.archs = arm64-v8a,armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1
