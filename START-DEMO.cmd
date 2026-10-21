@echo off
title LavishCars - Local Showcase
cd /d "%~dp0apps\web"
set "API_INTERNAL_ORIGIN=http://127.0.0.1:8000"
echo Starting the local LavishCars storefront.
echo Keep this window open while recording.
echo Open http://localhost:3000 when Ready appears.
call npm start
pause
