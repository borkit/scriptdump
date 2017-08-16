import-module awspowershell

#AWS stored Credential names
$profile_list = $ENV:AWSProfiles -split ";"

#Path for log file
$path_log = $ENV:Path_log

#Uses Value "From Port in AWS" SSH is 22, RDP is 3389. This script expects a standard port 22 maps to port 22 design  
$Search_ports = $ENV:Ports_list -split ";"


function Get-externalCDR() {
    try {
    $ip = $(invoke-restmethod 'https://api.ipify.org?format=json' | select -expandproperty IP) + "/32"
    return $ip
    } catch {
    return $false
    }
}


#Allowed IP Ranges.
$Allowed_IP_Ranges = Get-ExternalCDR

foreach($profile in $profile_list) {

#Incase of Security group overlap clear the id list for every profile
[array]$updated_group_id = $NULL

#Set the AWS profile to use
Set-AWSCredentials -ProfileName $profile

#Iterate through all possible regions
$region_list = Get-AWSRegion | select -expandproperty Region
    foreach($region in $region_list) {
    
    $Instance_list = Get-EC2Instance -region $region |select -expandproperty instances
    $VPC_list = Get-EC2Vpc -Region $region
        foreach ($VPC in $VPC_list) {
        $Instance_list | Where-Object {$_.VpcId -eq $VPC.VpcId} | foreach-object {
            $Instance_name = ($_.Tags | Where-Object {$_.Key -eq 'Name'}).Value
            $SecurityGroups = $_.SecurityGroups.GroupName
            $SecurityGroupID = $_.SecurityGroups.GroupID
                if($updated_group_id -notcontains $SecurityGroupID) {
                    foreach($port in $Search_Ports) {
                        if($Found_IP_List = $(Get-EC2SecurityGroup $SecurityGroupID -Region $region ).IpPermissions | where { $_.FromPort -eq "$port" } | select -expandproperty IPRange) {
                        $Removable_IPs = Compare-Object -ReferenceObject $Allowed_IP_Ranges -DifferenceObject $Found_IP_List | where { $_.SideIndicator -eq "=>" } | select -expandproperty InputObject                           
                            foreach($IP_Current_Rule in $Removable_IPs) {
                                $Time = Get-date -format "s"
                                echo "$Time : Removing $IP_Current_Rule from $SecurityGroups ( $SecurityGroupID ) with $profile in $region found on $Instance_name"
                                echo "$Time : Removing $IP_Current_Rule from $SecurityGroups ( $SecurityGroupID ) with $profile in $region found on $Instance_name" >> $path_log
                                Try {
                                $Firewall_rule = @{ IpProtocol="tcp"; FromPort="$port"; ToPort="$port"; IpRanges= "$IP_Current_Rule" }
                                Revoke-EC2SecurityGroupIngress -GroupId $SecurityGroupID -IpPermissions $Firewall_rule -Region $region
                                } catch {
                                echo "$Time ERROR: REMOVING $port for $SecurityGroups ($SecurityGroupID)"
                                echo "$Time ERROR: REMOVING $port for $SecurityGroups ($SecurityGroupID)" >> $Path_log
                                $_
                                $_ >> $Path_log
                                exit 1
                                }
                            }
                        
                        $Allowed_IPs = Compare-Object -ReferenceObject $Allowed_IP_Ranges -DifferenceObject $Found_IP_List | where { $_.SideIndicator -eq "<=" } | select -expandproperty InputObject
                            foreach($IP in $Allowed_IPs) {
                                if($Found_IP_List -notcontains $IP) {
                                $Time = Get-date -format "s"
                                echo "$Time : Adding $IP from $SecurityGroups ( $SecurityGroupID ) with $profile in $region found on $Instance_name"
                                echo "$Time : Adding $IP from $SecurityGroups ( $SecurityGroupID ) with $profile in $region found on $Instance_name" >> $path_log
                                Try {
                                $Firewall_rule = @{ IpProtocol="tcp"; FromPort="$port"; ToPort="$port"; IpRanges= "$IP" }
                                Grant-EC2SecurityGroupIngress -GroupId $SecurityGroupID -IpPermission @( $Firewall_rule ) -Region $region
                                } catch {
                                echo "$Time ERROR: ADDING $port for $SecurityGroups ($SecurityGroupID)"
                                echo "$Time ERROR: ADDING $port for $SecurityGroups ($SecurityGroupID)" >> $Path_log
                                $_
                                $_ >> $Path_log
                                exit 1
                                }
                            }
                        }
                    }
                $updated_group_id += $SecurityGroupID.Trim()    
                }
            }
        }
    }
}