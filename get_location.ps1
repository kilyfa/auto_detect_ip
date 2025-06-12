# get_location.ps1
Add-Type -AssemblyName System.Device

$watcher = New-Object System.Device.Location.GeoCoordinateWatcher
$watcher.Start()

# Tunggu sampai lokasi siap atau ada data
while (($watcher.Status -ne 'Ready') -and ($watcher.Status -ne 'NoData')) {
    Start-Sleep -Milliseconds 100
}

if ($watcher.Status -eq 'Ready') {
    $latitude = $watcher.Position.Location.Latitude
    $longitude = $watcher.Position.Location.Longitude
    
    # Cetak latitude dan longitude dalam format yang mudah diurai oleh Python
    Write-Output "Latitude: $latitude, Longitude: $longitude"
} else {
    Write-Error 'Access Denied for Location Information or No Data'
    # Keluar dengan kode error jika lokasi tidak bisa didapatkan
    exit 1 
}