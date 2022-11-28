for %%i in (%*) do (
	ffmpeg -i %%i -vcodec libx264 -vf "transpose=2" %%~ni%temp.mp4
	DEL %%i
	REN %%~nitemp.mp4 %%~nxi
)