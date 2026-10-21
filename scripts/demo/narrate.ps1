param([string]$OutputDirectory = "output/showcase/audio")
$ErrorActionPreference = "Stop"
$repoDirectory = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$destination = Join-Path $repoDirectory $OutputDirectory
New-Item -ItemType Directory -Force $destination | Out-Null
$scenes = Get-Content (Join-Path $repoDirectory "showcase/storyboard.json") -Raw | ConvertFrom-Json
$voice = New-Object -ComObject SAPI.SpVoice
$englishVoice = @($voice.GetVoices() | Where-Object { $_.GetDescription() -like "*Zira*" })
if ($englishVoice.Count -eq 0) { throw "Microsoft Zira English voice is required for this recording." }
$voice.Voice = $englishVoice[0]
$voice.Rate = 0
$voice.Volume = 100
foreach ($scene in $scenes) {
    $stream = New-Object -ComObject SAPI.SpFileStream
    $path = Join-Path $destination ($scene.id + ".wav")
    $stream.Open($path, 3, $false)
    $voice.AudioOutputStream = $stream
    [void]$voice.Speak($scene.narration)
    $stream.Close()
    Write-Output ("Narration generated: " + $scene.id)
}
