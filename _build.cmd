set dst=_deploy\hoard
rd /s /q %dst%
md %dst%
md %dst%\resources

copy webServer\config.json.example                 %dst%\config.json.example
copy webServer\config.py                           %dst%\config.py
copy webServer\filesystem.py                       %dst%\filesystem.py
copy webServer\gallery.html                        %dst%\gallery.html
copy webServer\handle_directory.py                 %dst%\handle_directory.py
copy webServer\handle_file.py                      %dst%\handle_file.py
copy webServer\handle_request.py                   %dst%\handle_request.py
copy webServer\handle_thumbnail.py                 %dst%\handle_thumbnail.py
copy webServer\log.py                              %dst%\log.py
copy webServer\main.py                             %dst%\main.py
copy webServer\resources.py                        %dst%\resources.py
copy webServer\requirements.txt                    %dst%\requirements.txt
copy webServer\stats.py                            %dst%\stats.py
copy webServer\thumbnail.html                      %dst%\thumbnail.html
copy webServer\resources\favicon.svg               %dst%\resources\favicon.svg
copy webServer\resources\style.css                 %dst%\resources\style.css
copy webServer\resources\thumbnail-bad-picture.png %dst%\resources\thumbnail-bad-picture.png
copy webServer\resources\thumbnail-placeholder.png %dst%\resources\thumbnail-placeholder.png

copy LICENSE   %dst%\LICENSE
copy README.md %dst%\README.md
explorer %dst%
