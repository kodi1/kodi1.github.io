import os
import hashlib
import xml.etree.ElementTree as et

class AddonsXmlGenerator:
  """
      Generates a new addons.xml file from each addons addon.xml file
      and a new addons.xml.md5 hash file. Must be run from the root of
      the checked-out repo. Only handles single depth folder structure.
  """      
      
  def generate_repo_addonsxml(self):
    '''
    Iterate through all addons in the repository and copy each addon.xml to the repository addons.xml
    '''
    addons_folders = os.listdir( "." )
    xml = et.Element("addons")
    for addon_folder in addons_folders:
      if ( not os.path.isdir(addon_folder) or addon_folder.startswith(".") or addon_folder.startswith("_") ): 
        continue
      addon_xml_path = os.path.join( addon_folder, "addon.xml" )          
      addon_xml = self._get_addon_xml(addon_xml_path)
      if addon_xml:
        xml.append(addon_xml)
    et.ElementTree(xml).write("addons.xml", encoding="utf8")


  def _get_addon_xml(self, path):
    try:        
      return et.parse( path ).getroot()
    except Exception as e:
      print ("Excluding %s due to error: %s" % ( path, e))
      return None
    
    
  def generate_md5_file( self ):
    try:
      md5sum = hashlib.md5()
      md5sum.update(open( "addons.xml", "r", encoding="utf8" ).read().encode('utf-8') )
      newmd5sum = md5sum.hexdigest()
      print ("new md5 sum: %s" % newmd5sum)
      with open ("addons.xml.md5", "w", encoding="utf8") as file:
        file.write(newmd5sum)
    except Exception as e:
      print("An error occurred creating addons.xml.md5 file: %s" % e)