#! /bin/bash

cp ./Procfile ../desonity-login/Procfile
cp ./requirements.txt ../desonity-login/requirements.txt
cp ./runtime.txt ../desonity-login/runtime.txt
cp ./wsgi.py ../desonity-login/wsgi.py
cp ./app.py ../desonity-login/app.py
cp ./.gitignore ../desonity-login/.gitignore

rm -rf ../desonity-login/static
rm -rf ../desonity-login/templates
cp -r ./static ../desonity-login/
cp -r ./templates ../desonity-login/

echo "Done!"
