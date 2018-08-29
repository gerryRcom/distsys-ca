#Create log directory if it doesn't exist
New-Item -ItemType Directory -Force -Path c:\_IT\log | Out-Null
#Get all required events for the past 6 hours from the Application log
$events = Get-EventLog -LogName Application -After (Get-Date).AddHours(-6) | Where-Object {$_.Source -eq "Microsoft-Windows-Backup"}
#Export all required events to individual .xmls files. Ensure unique name by generating a GUID for each filename
Foreach ($event in $events)
{
    $guid = New-Guid
    $logName = "c:\_IT\log\" + $env:computername + "$" + $guid + ".xml"
    $event | Export-Clixml -Path $logName
}

$txtRecords = Resolve-DnsName gerryr.com -Type TXT
$splitter = "."
Foreach ($record in $txtRecords)
{
    $content = $record.Strings
    If ($content.SubString(0,4) -eq 'zoho')
    {
        Write-Host $content.Split($splitter)
    }

}
