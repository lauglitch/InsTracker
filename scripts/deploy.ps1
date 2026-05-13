$version = Get-Content version.txt

butler push "dist/free" lauglitch/instracker:free-windows --userversion $version
butler push "dist/pro" lauglitch/instracker:pro-windows --userversion $version