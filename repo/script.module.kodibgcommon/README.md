# How to use
1. Include an import statement in addon.xml:  
    `<import addon="script.module.kodibgcommon" version="1.0.9"/>`
    
2. Import in addon.py (or other .py files)  
_from kodibgcommon.utils import *_

# Easy access to addon settings
The settings objects allows easy access to addon settings as long as you know the setting's id.  
Just call _settings.id-of-the-setting_  
If you have a bool setting with id 'debug' i.e. `<setting id="debug">true</setting>`, calling settings.debug will return a boolean value of True or False.
```python
if settings.debug:  
  execute_function()
else:  
  execute_another_function()  
```  
if you have a setting holding a digit number i.e. `<setting id="id">1234</setting>`, calling setting.id will return 1234 as intiger.  
Any other settings are considered strings.
```python
if settings.id > 0:  
  execute_function(settings.id)
else:  
  execute_another_function()  
```  

# Easy log messages depending on whether addon's 'debug' setting is True or False 
*log(msg, level=xbmc.LOGDEBUG)* - the function logs a message to Kodi.log file, prepending the addon id.  
The message is visible only if addon's setting 'debug' is True.

# Other useful functions:
*get_addon()* - returns the current addon instance  
*get_addon_id()* - returns current addon id  
*get_addon_name()* - returns current addon name  
*get_addon_version()* - returns current addon version  
*get_profile_dir()* - returns addon profile directory.  
*get_addon_dir()* - returns addon install directory.  
*get_resources_dir()* - returns addon resources directory.  
*get_lib_dir()* - returns addon lib directory.  
*get_platform()* - returns OS type - Android, Windows, Linux etc.  
*get_kodi_build()* - returns current Kodi version and build number.  
*get_kodi_version()* - returns current Kodi version i.e. 18.01  
*get_kodi_major_version()* - returns Kodi major version i.e. 16, 17, 18 or above.  
*log_kodi_platform_version()* - returns Kodi version and OS type.  
*get_unique_device_id()* - returns an unique identifier by concatenating Kodi version, platform and uuid.  
*notify_error(message, duration=5000)* - raises an error notification message in Kodi's top right corner.  

*get_params()* - parses addon's URL and returns a dictionary of params.  
*make_url()* - transforms a dictionary into an addon URL (prepends the addon plugin path).  
