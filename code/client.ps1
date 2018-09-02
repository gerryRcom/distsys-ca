#Create log directory if it doesn't exist
New-Item -ItemType Directory -Force -Path c:\_IT\log | Out-Null
#Get all required events for the past 6 hours from the Application log
$events = Get-EventLog -LogName Application -After (Get-Date).AddHours(-6) | Where-Object {$_.Source -eq "Microsoft-Windows-Backup"}
#Export all required events to individual .xml files. Ensure unique name by generating a GUID for each filename
Foreach ($event in $events)
{
    $guid = New-Guid
    $logName = "c:\_IT\log\" + $env:computername + "$" + $guid + ".xml"
    $event | Export-Clixml -Path $logName
}

#Pull list of nodes from txt DNS txt record
$txtRecords = Resolve-DnsName gerryr.com -Type TXT
$activeNodes = $()
$nodeResponse = $()
Foreach ($record in $txtRecords)
{
    #find the specific txt record, it will begin with the word "nodes"
    $content = $record.Strings
    If ($content.SubString(0,5) -eq 'nodes')
    {
        #extract the node names, i.e. everything after the initial "nodes" word, $ used as a delimiter
        Foreach ($item in $content.SubString(6).split('$'))
        {
            $node = $item+".gerryr.com"
            If (Test-Connection -ComputerName $node -Quiet)
            {
                If(Test-NetConnection -Computername $node -Port 80)
                {
                    $activeNodes += $node
                    $nodeResponse += (test-netconnection -computername $node).PingReplyDetails.RoundTripTime
                }                
            }
    }
    Write-Host $activeNodes
    Write-Host $nodeResponse
    }
}
