set dst=_deploy
rd /s/q %dst%
md %dst%
robocopy webServer %dst% /e /xf config.json log.txt /xd __pycache__ /w:1
explorer %dst%