# Introduction

This project I created to install custom applications on Hisense TV.

It implements simple HTTP and DNS server needed to host Hisense App Store locally.

# tl;dr

10 simple steps to install the application on your TV:

1. Download the code from this repository
2. Install required python modules (ssl and dnslib)
3. Update the config file - use your local IP addresses
4. Update index.html file - add your own web-applications or use my list
5. Run server.py
6. Change the DNS settings on your TV
7. Open https://vidaahub.com/ on your TV (ignore SSL certificate issue)
8. Install the application
9. Switch the DNS settings on your TV back,
10. Restart TV

# Description of Vidaa Platform

Vidaa OS is based on Linux, VIDAA platform supports two types of applications; web-based applications and native applications. It is a browser-based environment that supports standard HTML5, CSS, Javascript, Javascript Library (e.g., jQuery), UI Framework (e.g., Bootstrap), Javascript Framework (e.g., Vue, Angular) as well as some VIDAA proprietary System API.

## Requirements to Web Applications

You can open almost any website with heavy javascript, media content and streams. Obviously, there are some limitations. But I selected a few requirements to the applications which can be considered as potential candidate for installing on Vidaa device:

1. The APP should be fully navigable with the remote control using the following keys:4 ways(Up/Down/Left/Right), OK, and Back.

2. Because when an app is launched, it opens in a full screen in a new window on the TV, it runs completely “chromeless”, with no address bar or user interface controls. The APP MUST have the ability to exit by pressing the remote control’s Back key on the homepage with a simple call to the window.close() method.

## Installing Web Application on Vidaa

In older versions (at least in the versions developed in 2022) there was a method when any web-application could be installed using the URL `hisense://debug`. So, if your Vidaa device was developed before 2022 - try to google how to use debug mode.

For the newer versions (actual in 2024) the debug mode is not allowed. But you still can install the web-based application using Javascript functions supported by the browser.

## Installing the application on *new* Vidaa

Vidaa System API has the interface (internal functions) to retrive information about the device (`Hisense_GetDeviceID( )`, `Hisense_GetFirmWareVersion( )`, `Hisense_GetModelName()`, etc.), you can call these functions from any website in the browser.

You need to use the function `Hisense_installAp()` to install the application:

```javascript
Hisense_installApp(
    "ApplicationName_debug", "ApplicationName", 
    "image_url","image_url", "image_url"
    "ApplicationURL",
    'store', 
    function(status) {
        status ? 
            // installation failed
            :
            // installation successful 
            (
                refreshAppsOnHisenseUI("ApplicationName_debug")
            );
    }
);
```

Don't ask me about these parameters. I did not find the documentation for `Hisense_installApp()` function:
- ApplicatioName - the name of the application;
- ApplicationName_debug - the same as above, but add the suffix "_debug". I don't know why;
- image_url - this is the application icon that will be displayed on the TV. Use png format and the resolution from 220x220px to 400x400px;
- ApplicationURL - the link to the HTML5 application. For example: `https://hisense.tv.twitch.tv/` or `https://hisense.vevo.com`;
- 'store' - leave it as 'store';
- function() - callback function. It only needed to refresh the status in the browser.

## Uninstalling the application on *new* Vidaa

```javascript
Hisense_uninstallApp(
    "ApplicationName_debug", 
    function(status) {
        !status ? 
            // uninstallation failed
            :
            // uninstallation successful  
            (
                refreshAppsOnHisenseUI()
            );
    }
);
```

## Important: why Hisense_installApp() and Hisense_uninstallApp() won't run

So, if you just add these functions to your website and try to run on Vidaa device - most likely you will get the "function not found" error.

There is a reason for this: **these functions only work if you run them from the website vidaahub.com**. 

And this is why I created this simple project.

# Vidaa-Apppstore Project

So, this project implements only two functions:

1. Run simple web-server, which returns only one HTML page with a couple `Hisense_installApp()` and `Hisense_uninstallApp()` functions;
2. Run simple DNS server, which returns the response for the name resolution request for the hostname "vidaahub.com".

Once you run this project - you will need to change the network settings on your TV and open the page "https://vidaahub.com/" - you will see the app store and will be able to install the applications.

There are two ways how you can run this application:

- using python;
- using .exe file (I added only Windows release)

## Run App Store Server using Python

It is tested and works on Python 3.8 and higher.

It uses only a few additional modules: dnslib and ssl. Install them using pip3 or system package manager:

```shell
pip3 install dnslib
pip3 install ssl
```

Then update the configuration file (see below) and simply run 

```shell
python3 server.py
```

## Run App Store Server using binaries (.exe file) on Windows

Just donwload the file from the releases. Then copy the files from this repository:

- config.json
- ssl/vidaahub.com.*
- index-en.html
- index-ru.html

Update the configuration file and run the `server.exe` file

### Compile your own .exe file

Btw, if you want to compile the .exe file from .py - you can use `pyinstaller`.

```shell
pip3 install pyinstaller
cd /project/dir/
pyinstaller --onefile server.py
```

## Configuration file

### General section
Server address - is the local IP address of your computer where you will run this server. Keep in mind that this IP address should be accessible from your the browser on your Smart TV. Or in other words, Vidaa and your computer should be in the same local network (wifi, lan):

```json
    "server_address": "192.168.100.12",
```

Set false ot true for these 3 parameters if you do or do not need to run HTTP, HTTPS and DNS server:

```json
    "enable_dns_server": false,
    "enable_https_server": true,
    "enable_http_server": true,
```

### HTTP server
Next, if you run HTTP server - update these parameters:

```json
    "http_port": 8080,
    "html_file": "index-en.html",
```
If you change the port to the default port for HTTP - 80 - you will need to run the server from root or administrator.

For `html_file` - see information below.

### HTTPS server

If you run HTTPS server - update these parameters:
```json
    "https_port": 8443,
    "ssl_keyfile": "ssl/vidaahub.com.key",
    "ssl_certfile": "ssl/vidaahub.com.crt",
    "html_file": "index-en.html",
```

These certificates - are self-signed certificates. When you run the server and open the page https://vidaahub.com/ in your browser - you will get the warn "certificate is invalid". You will need to accept it and open the page.

If you want to genereate your own self-signed certificate - use the utility `openssl` as follows:

```shell
openssl req -x509 -newkey rsa:4096 \
 -keyout vidaahub.com.key -out vidaahub.com.crt \
 -sha256 -days 3650 -nodes \
 -subj "/C=XX/ST=StateName/L=CityName/O=Vidaa Hub Local/OU=Vidaa Hub/CN=vidaahub.com"
```

If you change the port to the default port for HTTPS - 443 - you will need to run the server from root or administrator.

### DNS server

Finally, if you run DNS server, be sure that you run it as a privileges user (administrator, root or run it with sudo) - because the DNS server will always listen on the privileged port 53.

In this section you will need at least one record: "vidaahub.com" - it will be used by your TV to make the install and uninstall functions available. Do not change the hostname and type, but change the address to the IP address of the computer (system) where you ring this code. Most likely it will be the same address as you pointed above in `"server_address"`.

Additionally, if you use javacript (jquery libraries) or other media content (e.g. icons) loaded from the other sites - add theirs name and IP address to this section. In my example I added ajax.googleapis.com - which I use to load jQuery in my script.

```json
    "dns_records": [
        {
            "hostname": "vidaahub.com",
            "type": "A",
            "address": "192.168.100.12"
        },
        {
            "hostname": "ajax.googleapis.com",
            "type": "A",
            "address": "216.58.215.74"
        },
        ...
    ]
```

## Update HTML files

In the configuration file you should point index.html file that will be returned by the server. You can write your own file - it should be any HTML file where you will add the buttons and functions `Hisense_installApp()` and `Hisense_uninstallApp()`. 

Or you can use my files from this repository as a template. I created two versions: "international" (index-en.html) and local (index-ru.html) - for the users from Ukraine or Belarus (or Russia).

If you use my file - just add or modify the lines in `apps` array:

```javascript
var apps = [
...
    {category:'my',appid:'vidaa_windy',name:'Windy',url:'https://www.windy.com/',text:'Windy'},
	{category:'official',appid:'vidaa_twitch',name:'twitch',url:'https://hisense.tv.twitch.tv/',text:'Twitch'},
	{category:'official',appid:'vidaa_vevo',name:'Vevo',url:'https://hisense.vevo.com',text:'Vevo'},
...
]
```
So, if you want to add a new application - just copy&paste one of these lines, and update the name, icon, url.

# Operations on Hisense TV

Once you launch the DNS and HTTP/HTTPS server - you can open this store on your Hisense TV. Go to network settigns (on TV) and change the DNS server to the local IP address that you set in the configuration file above.

Next open the browser on TV, and put the address "https://vidaahub.com/".

If you set everything properly - you should see Vidaa App Store. Click "install" or "uninstall" next to each application.