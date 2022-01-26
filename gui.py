import PySimpleGUI as sg
import cv2

cap = cv2.VideoCapture()
cap.open(0, cv2.CAP_DSHOW)

layout = [[sg.Text("Camera", size=(60, 1), justification="center")],
          [sg.Image(filename="", key="-IMAGE-")]]

# Create the window
window = sg.Window("Demo", layout)

# Create an event loop
while True:
    event, values = window.read(timeout=20)

    if event == "OK" or event == sg.WIN_CLOSED:
        break

    ret, frame = cap.read()
    if ret:
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


window.close()
