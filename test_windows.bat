@echo off
cd /d "C:\Dev\UEFN\temp\unreal-mcp\Python"
python -c "import socket; sock = socket.socket(); result = sock.connect_ex(('127.0.0.1', 55557)); print('Connected' if result == 0 else 'Not connected'); sock.close()"
pause