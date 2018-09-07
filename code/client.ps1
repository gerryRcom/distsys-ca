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
$activeNodes = @()
$nodeResponses = @()
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
            If (Test-NetConnection -ComputerName $node -InformationLevel Quiet)
            {
                If(Test-NetConnection -Computername $node -Port 22)
                {
                    $activeNodes += $node
                    $nodeResponses += (test-netconnection -computername $node).PingReplyDetails.RoundTripTime
                }                
            }
    }
}
}

#Quick error check in case there was a connection issue between connectivity tests resulting node discrepancy
$aN = $activeNodes.Count
$nR = $nodeResponses.Count
If($activeNodes.Count -eq 0 -or $nodeResponses.Count -eq 0 -or $aN -ne $nR)
{
    exit
}

#Determine the fastest responder from list of available nodes
$nodeIndex = $aN - 1
$selectedNode = 0
if($nodeIndex -eq 0)
{
    $selectedNode = $activeNodes[$nodeIndex]
}
else 
{
    While($nodeIndex -gt 0)
{
    If($nodeResponse[$nodeIndex] -lt $nodeResponses[$nodeIndex - 1])
    {
        $selectedNode = $activeNodes[$nodeIndex]
    }
    else {
        $selectedNode = $activeNodes[$nodeIndex - 1]
    }
    $nodeIndex--
}
}

##
## Begin Transfer of files to selected server
## Code exaple taken from here: https://winscp.net/eng/docs/library_powershell
##

#Get password from text file on system
$Path = "C:\_IT\log\credentials.txt"
$values = Get-Content $Path | Out-String | ConvertFrom-StringData

try
{
    # Load WinSCP .NET assembly
    Add-Type -Path "C:\_IT\log\WinSCP\WinSCPnet.dll"
 
    # Setup session options
    $sessionOptions = New-Object WinSCP.SessionOptions -Property @{
        Protocol = [WinSCP.Protocol]::Sftp
        HostName = $selectedNode
        UserName = $values.user
        Password = $values.password
        #SshHostKeyFingerprint = "ssh-rsa 2048 xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
        GiveUpSecurityAndAcceptAnySshHostKey = "True"
    }
 
    $session = New-Object WinSCP.Session
 
    try
    {
        # Connect
        $session.Open($sessionOptions)
 
        # Upload files
        $transferOptions = New-Object WinSCP.TransferOptions
        $transferOptions.TransferMode = [WinSCP.TransferMode]::Binary
 
        $transferResult = $session.PutFiles("C:\_IT\log\*.xml", "/home/log-transfer/incoming-logs/", $False, $transferOptions)
 
        # Throw on any error
        $transferResult.Check()
 
        # Print results
        #foreach ($transfer in $transferResult.Transfers)
        #{
        #    Write-Host "Upload of $($transfer.FileName) succeeded"
        #}
    }
    finally
    {
        # Disconnect, clean up
        $session.Dispose()
    }
    #Once sucessful transfer has occured, transfer log files to log-archive folder and delete log archives older than 7 days
    Get-ChildItem -Path "C:\_IT\log\*.xml" -Recurse | Move-Item -Destination "C:\_IT\log\log-archives"
    Get-ChildItem -Path "C:\_IT\log\log-archives\" -Recurse | Where-Object {($_.LastWriteTime -lt (Get-Date).AddDays(-7))} | Remove-Item -Force
    exit 0
}
catch
{
    #Write-Host "Error: $($_.Exception.Message)"
    exit 1
}
