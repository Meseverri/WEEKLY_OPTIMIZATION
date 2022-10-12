$jsonPath = Get-Content 'D:\FUDO TECH\WEEKLY_OPTIMIZATION\confPath.json' | Out-String | ConvertFrom-Json
$terminalPath = $jsonPath.terminalPath
$ProyectPath = $jsonPath.proyectPath
$mt5OutPutPath  = $jsonPath.mt5OutPutPath
cd $terminalPath

$fileArray = Get-ChildItem -Path "$($ProyectPath)\AllOpt" -Recurse -Filter *.ini 

$totalfiles = $fileArray.length
$i = 1
$percent = [math]::round($i/$totalfiles, 5)*100
$fileArray |
Foreach-Object {
    Write-Progress -Activity "Optimizaciones en Proceso " -Status "$percent% Complete:" -PercentComplete $percent
    $year = $_.Name.Substring(25,4)
    $yearWeek = $_.Name.Substring(25,$_.Name.length-4-25)
    Write-Host $yearWeek
    if (!(Test-Path "$($ProyectPath)\$($year)\$($yearWeek).xml")) {
        #$mt5Process
        do {
            .\terminal64.exe /config:$($_.FullName)
            Start-Sleep 5
            $optResult = "C:\Users\mesev\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\$($yearWeek).xml"
            $mt5Process = Get-Process "metatester64"
            while (!(Test-Path $($optResult)) -and ($mt5Process -ne $null)) { 
                Start-Sleep 30
                $mt5Process = Get-Process "metatester64"
            }
        } while (($mt5Process -eq $null) -and !(Test-Path $($optResult)))
        Move-Item -Path $($optResult)  -Destination "$($ProyectPath)\$($year)"  -PassThru
        Write-Host "Se ha movido el archivo:"
        Write-Host "$($optResult)"
        Write-Host "A la carpeta:"
        Write-Host "$($ProyectPath)\$($year)"
    }
    Write-Host "-----------------------------------------------------------------------------------------------"
    $i++ 
    $percent = [math]::round($i/$totalfiles, 5)*100
}

Write-Host "Todos los .ini ejecutados"