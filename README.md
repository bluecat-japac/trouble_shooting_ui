# Trouble Shooting UI

Trouble-shooting commands UI for perform DNS and network connectivity tests from the DNS server

## Set up BDDS

Open firewall for ping, traceroute and add permission for traceroute

1. Run this command to open ICMP

    ```
    echo "iptables -A icmp_packets -p ICMP --icmp-type echo-request -j ACCEPT
    iptables -A icmp_packets -p ICMP --icmp-type echo-reply -j ACCEPT
    iptables -A OUTPUT -p UDP --dport 33434:33689 -j ACCEPT
    " > fw
    custom_fw_rules --import-rules fw
    ```
2. Run this command to add permission for traceroute

    ```
   chmod 755 /usr/bin/traceroute.db
    ```

## Setup Gateway workflow and install 3rd Python libraries

1. Use the **Gateway Management** to import workflow function(version 19.8.1)

    ![Import](images/import.png?raw=true)
    
    Note: If any error occurs, just ignore because it is acceptable.
    
2. Execute this command to install 3rd Python libraries with correct path of gateway and trouble_shooting_ui workflow directories:

    ```bash
    docker exec bluecat_gateway pip install --target /bluecat_gateway/customizations/integrations -r /bluecat_gateway/workflows/trouble_shooting_ui/requirements.txt
    docker restart bluecat_gateway
    ```

3. Navigate to **Workflow Permission**. Add permission to access trouble shooting ui workflow.

    ![Permission](images/permission.png?raw=true)

## Set up BAM

#### Check User

1. Access to BAM then select **Administration** tab. Tabs remember the page you last worked on, so select the tab again to ensure you're on the Administration page.

    ![Administration](images/administration.png?raw=true)

2. Under **User Management**, click **Users and Groups**. Check if **User** has **API User** and **GUI User** or not.

    ![Users and Group](images/users_and_group.png?raw=true)

3. If already has GUI and API permissions, this step below is not necessary. Go to [Create UDF for Trouble Shooting from BAM](#UDF)

### User

#### Create User with API and GUI permission

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

#### Setting and changing default access rights for user

1. Under User Management, click **Access Rights Settings**

2. Click **Default Access Rights**

3. Under **Access Rights**, click **New**, or click the name of a user, and click **Edit**

    ![Object Types in Administration Tab > Access Rights Settings](images/default_access_right.png?raw=true "Optional Title")

4. Under **Users and Groups**, select a username from the drop-down menu and click **Add**. The user is added to a list below the drop-down menu.

5. Under **Access Right**, define the type of access right. From the **Default Access** list, select an option: **View** — users can see objects, but cannot add, delete, or change objects.

6. Click **Add**

    ![Add Access Rights Settings](images/add_access_right.png?raw=true "Optional Title")

### Create User Define Field(UDF) for Server object

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
    | `Display Name` | Troubleshooting |
    | `Default Value` | Troubleshooting |
    | `Label` | Troubleshooting |
    | `URL` | **http://`<gateway-ip>`:`<port>`/trouble_shooting_ui/trouble_shooting_ui_endpoint** |

    Sample as below picture:

    ![Sample User-Defined Field](images/04.png?raw=true "Optional Title")

6. Click **Add** button to finish.

7. After finish, go back to **Details** tab of this **Server**. The UDF will appear and click it to redirect to Trouble Shooting UI.

### Workflow to run command

 ![ UI ](images/ui.png?raw=true)

1. Default **BAM IP** get in config file

2. Select one **Configuration** in BAM

3. Choose **Server** in **Configuration**. It varies according to the configuration selected.

4. Select **Tool**

    | Name | Description |
    | --- | --- |
    | `ping` | Network administration utility used to test the reachability of a host on an Internet Protocol (IP) network and to measure the round-trip time for messages sent from the originating host to a destination computer.  |
    | `dig` (Domain Information Groper) | Network administration command-line tool for querying the Domain Name System (DNS). |
    | `tracerouter` | Computer network diagnostic commands for displaying the route (path) and measuring transit delays of packets across an Internet Protocol (IP) network.|

5. Input correct **Parameters**

    > Note: The error message will appear when input wrong format of **Parameters**

6. Click **SUBMIT** button.

    > Note: The **SUBMIT** button is only enable after selecting DNS/DHCP server(s), choosing trap OID and sticking at least one **SNMP version**

7. The command results will appear in **Result** field.

### Generate SSH key with PEM format to use

1. Run this command:

    ```
    ssh-keygen -m PEM
    ```

    * Enter file in which the key was saved: **path/to/trouble_shooting_ui/ssh** with the name of SSH key is "key"

        > example: /trouble_shooting_ui/ssh/key

    * No passphrase

2. Copy SSH key to the server

    ```
    ssh-copy-id -i <key> <user>@<host>
    ```