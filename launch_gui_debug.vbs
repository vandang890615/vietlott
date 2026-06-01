Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "d:\vietlott"
objShell.Environment("Process")("PYTHONPATH") = "src;src/vietlott/predictor"
returnCode = objShell.Run("cmd.exe /c ""C:\Users\ADMIN\AppData\Local\Programs\Python\Python313\python.exe"" src/vietlott/predictor/gui_app.py > d:\vietlott\gui_error.txt 2>&1", 0, True)
Set fso = CreateObject("Scripting.FileSystemObject")
Set f = fso.OpenTextFile("d:\vietlott\gui_error.txt", 1)
If Not f.AtEndOfStream Then
    MsgBox f.ReadAll, vbCritical, "Lỗi khởi chạy Vietlott"
Else
    MsgBox "Không có lỗi nhưng app đã thoát. Return code: " & returnCode, vbInformation, "Thông báo"
End If
f.Close
