$jsonPath = Get-Content 'D:\FUDO TECH\WEEKLY_OPTIMIZATION\confPath.json' | Out-String | ConvertFrom-Json
$terminalPath = $jsonPath.terminalPath
$ProyectPath = $jsonPath.proyectPath
$mt5OutPutPath  = $jsonPath.mt5OutPutPath
cd $terminalPath

$fileArray = Get-ChildItem -Path "$($ProyectPath)\2022_BT_ini" -Recurse -Filter *.ini 

$totalfiles = $fileArray.length
$i = 1
$percent = [math]::round($i/$totalfiles, 5)*100
$fileArray |
Foreach-Object {
    Write-Progress -Activity "Backtesting en Proceso " -Status "$percent% Complete:" -PercentComplete $percent
    $year = $_.Name.Substring(27,4)
    $yearWeek = $_.Name.Substring(27,$_.Name.length-4-27)
    Write-Host $yearWeek

    Copy-Item -Path "$($ProyectPath)\2022_BT_sets\$($yearWeek.Substring(4)).set" -Destination "$($mt5OutPutPath)\MQL5\Profiles\Tester"
    if (!(Test-Path "$($ProyectPath)\$($year)_BT_results\$($yearWeek).htm") ) {
        .\terminal64.exe /config:$($_.FullName)
        $btResult = "$($mt5OutPutPath)\$($yearWeek).htm"
        while (!(Test-Path $($btResult))) { 
            Start-Sleep 10 
        }
        Move-Item -Path $($btResult)  -Destination "$($ProyectPath)\$($year)_BT_results"  -PassThru
        Write-Host "Se ha movido el archivo:"
        Write-Host "$($btResult)"
        Write-Host "A la carpeta:"
        Write-Host "$($ProyectPath)\$($year)_BT_results"
    }
    Remove-Item "$($mt5OutPutPath)\MQL5\Profiles\Tester\$($yearWeek.Substring(4)).set"
    Write-Host "-----------------------------------------------------------------------------------------------"
    $i++ 
    $percent = [math]::round($i/$totalfiles, 5)*100
}

Write-Host "Todos los .ini ejecutados"




