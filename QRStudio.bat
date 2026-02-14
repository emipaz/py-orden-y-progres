@echo off
setlocal
set "PROJECT_DIR=D:\py-orden-y-progres"
pushd "%PROJECT_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_DIR%\run_qrstudio.ps1" %*
popd
endlocal
