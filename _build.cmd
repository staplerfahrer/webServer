set dst=_deploy\hoard
rd /s /q %dst%
md %dst%
md %dst%\resources

copy webServer\config.json.example                 %dst%\
copy webServer\config.py                           %dst%\
copy webServer\filesystem.py                       %dst%\
copy webServer\gallery.html                        %dst%\
copy webServer\handle_directory.py                 %dst%\
copy webServer\handle_file.py                      %dst%\
copy webServer\handle_request.py                   %dst%\
copy webServer\handle_thumbnail.py                 %dst%\
copy webServer\log.py                              %dst%\
copy webServer\main.py                             %dst%\
copy webServer\resources.py                        %dst%\
copy webServer\requirements.txt                    %dst%\
copy webServer\stats.py                            %dst%\
copy webServer\thumbnail.html                      %dst%\
copy webServer\resources\Enso.png                  %dst%\resources\
copy webServer\resources\Enso.png_LICENSE          %dst%\resources\
copy webServer\resources\favicon.svg               %dst%\resources\
copy webServer\resources\style.css                 %dst%\resources\
copy webServer\resources\thumbnail-bad-picture.png %dst%\resources\
copy webServer\resources\thumbnail-placeholder.png %dst%\resources\
copy webServer\resources\viewer-mask.png           %dst%\resources\

copy LICENSE   %dst%\LICENSE
copy README.md %dst%\README.md
explorer %dst%
