cd "C:\Program Files\MetaTrader 5"
$ProyectPath = "C:\Users\mesev\Documents\BackUp\TRABAJO\FUDO\FUDO TECHNOLOGIES\Backtest MT5\EURUSD\WEEKLY_OPTIMIZATION"
$fileArray = Get-ChildItem -Path "$($ProyectPath)\AllOpt" -Recurse -Filter *.ini 

$totalfiles = $fileArray.length
$i = 1
$percent = [math]::round($i/$totalfiles, 5)
$fileArray |
Foreach-Object {
    Write-Progress -Activity "Optimizaciones en Proceso " -Status "$percent% Complete:" -PercentComplete $percent
    $year = $_.Name.Substring(25,4)
    $yearWeek = $_.Name.Substring(25,$_.Name.length-4-25)
    Write-Host $yearWeek
    if (!(Test-Path "$($ProyectPath)\$($year)\$($yearWeek).xml")) {
        .\terminal64.exe /config:$($_.FullName)
        $optResult = "C:\Users\mesev\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\$($yearWeek).xml"
        while (!(Test-Path $($optResult))) { 
            Start-Sleep 30 
        }
        Move-Item -Path $($optResult)  -Destination "$($ProyectPath)\$($year)"  -PassThru
        Write-Host "Se ha movido el archivo:"
        Write-Host "$($optResult)"
        Write-Host "A la carpeta:"
        Write-Host "$($ProyectPath)\$($year)"
    }
    Write-Host "-----------------------------------------------------------------------------------------------"
    $i++ 
    $percent = [math]::round($i/$totalfiles, 5)
}

Write-Host "Todos los .ini ejecutados"




