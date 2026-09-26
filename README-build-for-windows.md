Step 1.
-------
cd to the project folder.
pip freeze > requirements.txt
pyinstaller --onefile yfsp_analyzer.pyw yfsp_collect.py display_data.py
rename dist\yfsp_analyzer.exe to dist\ to yfsp_analyzer_X.X.X.exe   

Step 2.
-------
Install the Inno Compiler. This is easily found with a Google search.
Execute Inno-Install\Setup-X.X.X.iss. 
Update Inno-Install\Setup-X.X.X.iss as required. The app version appears in 3 places.
Click on Build -> Compile (A.K.A. Ctrl-F9).
Use WinZip to Zip the Inno-Install\Setup-YF-Analyzer-X.X.X.exe to Inno-Install\Setup-YF-Analyzer-X.X.X.zip
Delete Inno-Install\Setup-YF-Analyzer-X.X.X.exe

Step 3.
-------
git add .
git commit -m "<your comment here>"
git push
