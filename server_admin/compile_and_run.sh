mkdir tmp
cd tmp
svn export --username zzz --password zzz --force svn://zzz/yacht_booking_app .
rm -fr .settings .project .pydevproject
svn export --username zzz --password zzz --force svn://zzz/server_admin/configs/app/pysmart.ini
python -m compileall .
rm -f *.py
rm -f */*.py
chmod +x yourapplication.fcgi
cd ..
sudo chown -R www-data:www-data tmp
sudo mv /srv/yacht_booking_app/static/boat_images tmp/static
sudo rm -fr /srv/yacht_booking_app
sudo mv tmp /srv/yacht_booking_app
sudo service apache2 restart

