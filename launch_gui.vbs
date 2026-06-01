Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "d:\vietlott"
objShell.Environment("Process")("PYTHONPATH") = "src;src/vietlott/predictor"
objShell.Run """C:\Users\ADMIN\AppData\Local\Programs\Python\Python313\python.exe"" src/vietlott/predictor/gui_app.py", 1, False
