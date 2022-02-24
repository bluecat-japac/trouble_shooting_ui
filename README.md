# Trouble Shooting UI

Trouble-shooting commands UI for perform DNS and network connectivity tests from the DNS server

## Requirements

- BlueCat Gateway Version: 19.8.1 or later
- BAM/BDDS Version: 9.1 or later

## Setup BlueCat DNS

Open firewall for `ping`, `traceroute` and add permission for `traceroute` in Trouble Shooting UI:

1. Run this command to open ICMP

    ```
    echo "iptables -A icmp_packets -p ICMP --icmp-type echo-request -j ACCEPT
    iptables -A icmp_packets -p ICMP --icmp-type echo-reply -j ACCEPT
    iptables -A OUTPUT -p UDP --dport 33434:33689 -j ACCEPT
    " > fw
    custom_fw_rules --import-rules fw
    ```
2. Run this command to add permission <br>
   For `traceroute`:

    ```
    chmod 755 /usr/bin/traceroute.db
    ```
   For `ping`:
    ```
    chmod u+s /bin/ping
    ```
   For accessing the `named.conf`: 
    ```
    echo "bluecat ALL = NOPASSWD: /bin/cat /jail/named/etc/named.conf" > /etc/sudoers.d/catnamedconf
    ```

# Setup BAM
### BAM Backup by Gateway workflow
Run this command to add permission:

1. Run backup:
    ```
    echo "bluecat ALL=(ALL) NOPASSWD:/usr/bin/perl /usr/local/bcn/backup.pl -i default" > /etc/sudoers.d/runbackup
    ```
2. For accessing the backup status file: 
    ```
    echo "bluecat ALL=(ALL) NOPASSWD:/bin/cat /etc/bcn/backup_status.dat" > /etc/sudoers.d/readstatus
    ```
3. Read and Download backup file:
    ```
    chmod 755 /data && chmod 777 /data/backup
    ```

# Setup Tcpdump for BAM/BDDS(s)
Run this command to add permission:

1. Run this command to add permission for running Tcpdump:
    ```
    echo "bluecat ALL = NOPASSWD: /usr/sbin/tcpdump" > /etc/sudoers.d/tcpdump
    ```
   
    ```
    echo "bluecat ALL = NOPASSWD: /usr/bin/killall" > /etc/sudoers.d/killall
    ```
   
    ```
    echo "bluecat ALL = NOPASSWD: /usr/bin/timeout" > /etc/sudoers.d/timeout
    ```
2. Run command to add permission for removing Tcpdump:
    Set permission for executed script:
    ```
    echo "bluecat ALL=(ALL) NOPASSWD:/usr/local/bluecat/remove_tcpdump.sh" > /etc/sudoers.d/remove_tcpdump
    ```
   
    Set permission for script file:
    ```
    chmod 755 /usr/local/bluecat/remove_tcpdump.sh
    ```
   
### BAM UI
#### Check User

1. Access to BAM then select **Administration** tab. Tabs remember the page you last worked on, so select the tab again to ensure you're on the Administration page.

    ![Administration](images/administration.png?raw=true)

2. Under **User Management**, click **Users and Groups**. Check if **User** has **API User** and **GUI User** or not.

    ![Users and Group](images/users_and_group.png?raw=true)

3. If already has GUI and API permissions, this step below is not necessary. Go to [Create UDF for Trouble Shooting from BAM](#UDF)

#### User

##### Create User with API and GUI permission

1. Under **Users** in **Users and Groups** above, click **New**. To edit a user, click the user name.

2. Enter the correct input

    | Field | Description |
    | --- | --- |
    | `Username`  | Type username . This name cannot contain spaces |
    | `Password` | Type password |
    | `Confirm Password` | Type a confirm password |
    | `Access Type` |  Must be **GUI and API** |

    Sample as below picture

    ![New User](images/new_user.png?raw=true)

    > Note: Remember to select **Access Type** is **GUI and API**

3. Click Add or Update to return to the **Users and Groups** page.

##### Setting and changing default access rights for user

1. Under User Management, click **Access Rights Settings**

2. Click **Default Access Rights**

3. Under **Access Rights**, click **New**, or click the name of a user, and click **Edit**

    ![Object Types in Administration Tab > Access Rights Settings](images/default_access_right.png?raw=true "Optional Title")

4. Under **Users and Groups**, select a username from the drop-down menu and click **Add**. The user is added to a list below the drop-down menu.

5. Under **Access Right**, define the type of access right. From the **Default Access** list, select an option: **View** — users can see objects, but cannot add, delete, or change objects.

6. Click **Add**

    ![Add Access Rights Settings](images/add_access_right.png?raw=true "Optional Title")

#### Create User Define Field(s) for Server object

1. Access to BAM then select **Administration** tab

2. From **Data Management** section choose **Object Types**

    ![Object Types in Administration Tab > Data Management section](images/01.png?raw=true "Optional Title")

3. From **Server** category choose **Server** object

    ![Choose Server Object](images/02.png?raw=true "Optional Title")

4. In **Server** object type page, select **New** and create an **User-Defined Field** from **Fields** table

    ![Create new User-Defined Field](images/03.png?raw=true "Optional Title")

5. Input these fields

    | Field | Default |
    | --- | --- |
    | `Name`  | udf-server-troubleshoot-wf |
    | `Display Name` | Trouble Shooting |
    | `Type` | Workflow |
    | `Default Value` | Troubleshooting |
    | `Label` | Troubleshooting |
    | `URL` | **http://`<gateway-ip>`:`<port>`/trouble_shooting_ui/trouble_shooting_ui_endpoint** |

    Sample as below picture:

    ![Sample User-Defined Field](images/04.png?raw=true "Optional Title")

6. Click **Add** button to finish.

7. After finish, go back to **Details** tab of this **Server**. The **Trouble Shooting** UDF will appear and click it to redirect to Trouble Shooting UI.

## Setup Workflow

## Generate SSH key with PEM format to use

1. Create **ssh** folder in **path/to/trouble_shooting_ui**

    ```
    mkdir ssh
    ```

2. Run this command to generate SSH key:

    ```
    cd ssh/
    ssh-keygen -m PEM
    ```

    * Enter file in which the key was saved: **path/to/trouble_shooting_ui/ssh** with the name of SSH key is "key"

        > Example: /trouble_shooting_ui/ssh/key

    * Note: No passphrase


3. Set permission for key:

    ```
    chmod 755 ssh/key
    ```

4. Copy SSH key to the Server

    * Run this command:

        ```
        ssh-copy-id -i <key> <user>@<host>

        Example: ssh-copy-id -i key bluecat@192.168.88.88
        ```

        > Note: currently, workflow use the **bluecat** user in server
     
    * Run this command to set new password for **user**:

        ```
        passwd <user>
        ```

## Deployment
### 1. Deploy Docker Container

1. Pull image from Registry:

    ```
    docker login registry.bluecatlabs.net
    docker pull <image-registry-name>:<tag>
    ```
    
    > Example: docker pull registry.bluecatlabs.net/professional-services/japac-tma/trouble_shooting_ui:trouble-shooting-master

    Or copy the <image>.tar.gz file to the host machine and run cmd:
    
    ```
    docker load -i <image>.tar.gz
    ```

2. Run Gateway Container
    
    Run cmd:

    ```
    docker run -d --name <container-name> -p <port>:8000  -v <gateway-log-dir>:/logs/ -e BAM_IP=<bam-ip>  <image-name>:<tag>
    
    Where
            <port>                     Port of Gateway
            <gateway-log-dir>          Path of the gateway log
            <bam-ip>                   IP of BAM
            <image-name>        Can use Image name or ID
    ```
    
    If use Trouble shooting with Gateway version *20.12.1* or later:
      1. Additional to `environment`:
      - `SESSION_COOKIE_SECURE`=`false`
      2. Configure **Security** in Gateway UI:
      - **Content Security Policy** to accept to load CSS by enter URLs to `Policy` input
      - **Cache Control**: `No Cache`

      ![Cache Control](images/cache_control.png?raw=true)

### 2. Import workflow by  **Gateway Management**

1. Use the **Gateway Management** to import workflow function

    ![Import](images/import.png?raw=true)
    
    Note: If any error occurs, just ignore because it is acceptable.
    
2. Execute this command to install 3rd Python libraries with correct path of gateway and trouble_shooting_ui workflow directories:

    ```bash
    docker exec bluecat_gateway pip install -r /bluecat_gateway/workflows/trouble_shooting_ui/requirements.txt
    docker restart bluecat_gateway
    ```

3. Navigate to **Workflow Permission**. Add permission to access trouble shooting ui workflow.

    ![Permission](images/permission.png?raw=true)

### Copy SSH key folder
Run this cmd to copy ssh setup in <a href="#setup-workflow">Setup workflow</a>.

```bash
docker cp ssh/ trouble-shooting:/builtin/workflows/trouble_shooting_ui/
docker restart <container-name>
```

### Workflow UI
#### Trouble Shooting UI
 ![ UI ](images/ui.png?raw=true)

1. Default **BAM IP** get in config file

2. Select **Configuration** in BAM

3. Choose **Server** in **Configuration**. It varies according to the configuration selected.

4. Select **Tool**

    | Name | Description |
    | --- | --- |
    | `ping` | Network administration utility used to test the reachability of a host on an Internet Protocol (IP) network and to measure the round-trip time for messages sent from the originating host to a destination computer.  |
    | `dig` (Domain Information Groper) | Network administration command-line tool for querying the Domain Name System (DNS). |
    | `tracerouter` | Computer network diagnostic commands for displaying the route (path) and measuring transit delays of packets across an Internet Protocol (IP) network.|

5. Input correct **Parameters**

6. Click **SUBMIT** button.

    > Note: The **SUBMIT** button is only enable after selecting DNS/DHCP server(s), choosing trap OID and sticking at least one **SNMP version**

7. The command results will appear in **Result** field.
#### BAM Backup By Gateway UI
Gateway Web can trigger BAM backup command and can download backup file.

 ![ BAM Backup UI ](images/bam_backup.png?raw=true)

1. Backup data will read backup file list from pre-defined directory (`/data/backup`)

2. If the number of file greater than max count file, the backup run button will disable unless delete some files.
    > Note: <br> 
    `MAX_COUNT_FILE` variables store in `<extract-dir>/bam_backup/config.ini`<br> (default is **10**)
   
3. Click `Run` button to run backup
    > Note: The backup profile will always be **default**
   
4. Click `Check Status` button to check the status of backup

5. Select `Download` icon download backup file

6. Choose the checkbox and click `Delete Selected` button to delete multiple backup file 
#### Analyze Traffic Tcpdump By Gateway UI
Gateway Web can trigger Tcpdump command and can download capture file.

 ![ Tcpdump UI ](images/tcp_dump.png?raw=true)
 
1. Select **Configuration** in Gateway. Default, as BAM doesn't need to select configuration. 

2. Choose **Server** and **BAM** in **Server**. BDDS(s) varies according to the selected configuration.

3. Choose **Interface** in **Server** or **BAM**. It varies according to the server or BAM selected

4. Select **Port** to capture. If **Port** is empty, mean capture all.

5. Select **Packets** to capture
    > Note: The input must be an integer, between 0 and 1000.

6. Input optional command: Free style input with more optional Tcpdump.

7. Select **Max capture file size**
    > Note: The input must be an integer, between 0 and 20.

8. Select **Max capture time** 
    > Note: The input must be an integer, between 0 and 300.

9. Click `START` button to start Tcpdump, when it completely run, it will write capture packet(s) to a capture.cap file.
   Tcpdump will always create output to same output file. If start Tcpdump during it is running, the request is ignored.
    > Note: Can choose either packets to capture or max capture file size to start
   
10. Click `STOP` button to stop a process of Tcpdump.
    
    If stop Tcpdump when it has already stopped, the request is ignored.

11. Click `DOWNLOAD CAPTURE` button to download the capture file (./capture.cap) from BAM/BDDS(s) to the local.

12. Click `GET STATUS` button to show message that Tcpdump is running or stopped.

#### Remove Tcpdump By Gateway UI
From Gateway Web, user can remove the Tcpdump package.
##### Install:
1. Copy the `remove_tcpdump.sh` script into `/usr/local/bluecat` in BAM/BDDS(s)
   (File `remove_tcpdump.sh` is provided standalone)
2. Configure sudo to allow execution of this script for the **bluecat** user.

    Set permission for executed script:
    ```
    echo "bluecat ALL=(ALL) NOPASSWD:/usr/local/bluecat/remove_tcpdump.sh" > /etc/sudoers.d/remove_tcpdump
    ```
   
    Set permission for script file:
    ```
    chmod 755 /usr/local/bluecat/remove_tcpdump.sh
    ```

#### Remove package
 ![ Remove Tcpdump UI ](images/05.png?raw=true)
1. Select **Configuration** in Gateway. Default, as BAM doesn't need to select configuration.
2. Choose **Server**. User can choose multiple BAM/BDDS(s) varies according to the selected configuration.
3. Click **remove**. Display the result according to server in table:
- If package has already removed, the process is ignored.
- If package has installed, tcpdump will be removed.


