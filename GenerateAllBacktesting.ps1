cd "C:\Program Files\MetaTrader 5"
$ProyectPath = "C:\Users\mesev\Documents\BackUp\TRABAJO\FUDO\FUDO TECHNOLOGIES\Backtest MT5\EURUSD\WEEKLY_OPTIMIZATION"
$fileArray = Get-ChildItem -Path "$($ProyectPath)\2021_BT_ini" -Recurse -Filter *.ini 

$totalfiles = $fileArray.length
$i = 1
$percent = [math]::round($i/$totalfiles, 5)
$fileArray |
Foreach-Object {
    Write-Progress -Activity "Backtesting en Proceso " -Status "$percent% Complete:" -PercentComplete $percent
    $year = $_.Name.Substring(27,4)
    $yearWeek = $_.Name.Substring(27,$_.Name.length-4-27)
    Write-Host $yearWeek

    Copy-Item -Path "$($ProyectPath)\2021_BT_sets\$($yearWeek.Substring(4)).set" -Destination "C:\Users\mesev\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Profiles\Tester"
    if (!(Test-Path "$($ProyectPath)\$($year)_BT_results\$($yearWeek).htm") ) {
        .\terminal64.exe /config:$($_.FullName)
        $btResult = "C:\Users\mesev\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\$($yearWeek).htm"
        while (!(Test-Path $($btResult))) { 
            Start-Sleep 10 
        }
        Move-Item -Path $($btResult)  -Destination "$($ProyectPath)\$($year)_BT_results"  -PassThru
        Write-Host "Se ha movido el archivo:"
        Write-Host "$($btResult)"
        Write-Host "A la carpeta:"
        Write-Host "$($ProyectPath)\$($year)_BT_results"
    }
    Remove-Item "C:\Users\mesev\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Profiles\Tester\$($yearWeek.Substring(4)).set"
    Write-Host "-----------------------------------------------------------------------------------------------"
    $i++ 
    $percent = [math]::round($i/$totalfiles, 5)
}

Write-Host "Todos los .ini ejecutados"




