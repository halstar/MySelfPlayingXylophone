#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

^j::

Send, l=0`n ; Disable logs
Sleep, 200
Send, `n
Sleep, 200

Send, v`n   ; Print tempo list values
Sleep, 200
Send, `n
Sleep, 3000

Send, e`n   ; Print controller  status
Sleep, 200
Send, `n
Sleep, 3000

Send, m`n   ; Print MIDI reader status
Sleep, 200
Send, `n
Sleep, 4000

Send, i=0`n ; Print MIDI file info by index
Sleep, 200
Send, `n
Sleep, 5000

Send, d=8`n ; Print MIDI file details by index
Sleep, 5000
Send, `n
Sleep, 200

Send, w`n ; Play welcome sound
Sleep, 4000
Send, `n
Sleep, 200

Send, n=60`n ; Play a single note
Sleep, 1000
Send, n=62`n
Sleep, 1000
Send, n=64`n

Sleep, 200
Send, `n
Sleep, 3000

Send, c=[60, 64, 67]`n ; Play a chord, i.e. several notes
Sleep, 1000
Send, c=[64, 67, 72]`n ; Play a chord, i.e. several notes
Sleep, 1000
Send, c=[67, 72, 76]`n ; Play a chord, i.e. several notes

Sleep, 200
Send, `n
Sleep, 3000

Send, o=8`n ; Start playing file, use file tempo
Sleep, 200
Send, `n
Sleep, 6000

Send, s`n ; Stop  playing file (interrupt)
Sleep, 200
Send, `n
Sleep 1000

Send, t=80`n ; Change file playing tempo
Sleep, 200
Send, `n
Sleep, 2000

Send, p=8`n ; Start playing file, use playing tempo
Sleep, 200
Send, `n
Sleep, 5000

Send, s`n ; Stop  playing file (interrupt)
Sleep, 200
Send, `n
Sleep, 2000

Send t=160`n ; Change file playing tempo
Sleep, 200
Send, `n
Sleep, 200

Send, p=8`n ; Start playing file, use playing tempo
Sleep, 200
Send, `n
Sleep, 4000

Send, s`n ; Stop  playing file (interrupt)
Sleep, 200
Send, `n
Sleep, 2000

Send, a`n ; Start playing all files in a row
Sleep, 200
Send, `n
Sleep, 5000

Send, q`n ; Enter quiet mode (don't trigger notes)
Sleep, 200
Send, `n
Sleep, 2000

Send, f`n ; Enter full  mode (trigger notes)
Sleep, 200
Send, `n
Sleep, 3000

Return

Send, l=1`n ; Activate ERROR log level
Sleep, 200
Send, `n
Sleep, 3000

Send, l=2`n ; Activate WARNING log level
Sleep, 200
Send, `n
Sleep, 3000

Send, l=3`n ; Activate INFO log level
Sleep, 200
Send, `n
Sleep, 5000

Send, l=4`n ; Activate DEBUG log level
Sleep, 200
Send, `n
Sleep, 5000

Send, l=0`n ; Disable logs 
Sleep, 200
Send, `n
Sleep, 2000

Send, h`n ; Display help reminder
Sleep, 200
Send, `n
Sleep, 3000

Send, r`n ; Press r to go for operational mode
Sleep, 200
Send, `n
Sleep, 1000

Return
