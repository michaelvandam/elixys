@echo off

REM *** This BATCH file is used to manually build an iPhone App deployment file (.ipa)
REM *** from the Flex source files until Adobe adds this functionality to Flash Builder
REM ***
REM *** Make sure you have both Flash Builder 4.5 and Java installed and the following paths are correct:

SET FLEXSDK=C:\Program Files\Adobe\Adobe Flash Builder 4.5\sdks\4.5.0
SET APPLEDEVCERTS=C:\AppleDevCerts
SET PATH=%PATH%;%FLEXSDK%\bin

echo (1) Cleaning output directory
IF NOT EXIST bin-iOS GOTO CREATEDIR
del /S /F /Q bin-iOS
GOTO CONTINUE1
:CREATEDIR
mkdir bin-iOS
:CONTINUE1

echo.
echo (2) Compiling SWF
mxmlc -load-config "%FLEXSDK%\frameworks\airmobile-config.xml" -library-path+=libs -compiler.source-path ..\Elixys\src -sp -compiler.include-libraries "%FLEXSDK%\frameworks\libs\mx\mx.swc" -compiler.theme "%FLEXSDK%\frameworks\themes\Spark\spark.css" -o bin-iOS\ElixysMobile.swf src\ElixysMobile.mxml
REM mxmlc -debug -load-config "%FLEXSDK%\frameworks\airmobile-config.xml" -library-path+=libs -compiler.source-path ..\Elixys\src -sp -compiler.include-libraries "%FLEXSDK%\frameworks\libs\mx\mx.swc" -compiler.theme "%FLEXSDK%\frameworks\themes\Spark\spark.css" -o bin-iOS\ElixysMobile.swf src\ElixysMobile.mxml

echo.
echo (3) Creating IPA (be patient, this will take some time)
cd bin-iOS
adt -package -target ipa-test -provisioning-profile %APPLEDEVCERTS%\Elixys_ShaneiPad.mobileprovision -storetype pkcs12 -keystore %APPLEDEVCERTS%\ShaneDeveloperCertificates.p12 -storepass devel Elixys.ipa ..\src\ElixysMobile-app.xml ElixysMobile.swf
REM adt -package -target ipa-debug -connect 192.168.1.102 -provisioning-profile %APPLEDEVCERTS%\Elixys_ShaneiPad.mobileprovision -storetype pkcs12 -keystore %APPLEDEVCERTS%\ShaneDeveloperCertificates.p12 -storepass devel Elixys.ipa ..\src\ElixysMobile-app.xml ElixysMobile.swf
echo.
