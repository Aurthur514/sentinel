$dest = Join-Path $PSScriptRoot '..\test_videos'
if (!(Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }
$path = Join-Path $dest 'sample.mp4'
if (!(Test-Path $path)) {
    Write-Host "Downloading sample video..."
    Invoke-WebRequest -Uri 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4' -OutFile $path
    Write-Host "Downloaded $path"
} else {
    Write-Host "sample.mp4 already exists at $path"
}
