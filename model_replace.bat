@echo off
:_start
set gc_path=E:\Programs\Grand Chase History

if not defined gc_path (
echo GrandChase path not defined
)

if defined gc_path (
echo Type the folder name
set /p _folder= Folder:
goto _pack_model
)

:_pack_model
echo Packing model

pause