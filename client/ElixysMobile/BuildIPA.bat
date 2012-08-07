@echo off

REM *** This BATCH file is used to build an iOS IPA
REM ***
REM *** Make sure you have both Flash Builder and Java installed and the following paths are correct:

SET FLEXSDK=C:\Program Files\Adobe\Adobe Flash Builder 4.5\sdks\4.6.0
SET ADT="%FLEXSDK%\bin\adt"
SET AMXMLC="%FLEXSDK%\bin\amxmlc"
SET DEVCERTS=C:\AppleDevCerts

echo *** Creating SWF
cmd /C %AMXMLC% +configname=airmobile -load-config+=src/ElixysMobile.config -source-path+=../Elixys/src,../ElixysAIR/src -library-path+=../Elixys/libs/elixys_parts.swc,../Elixys/libs/as3corelib.swc,../Elixys/VideoANE/com.AppTouch.Video.swc -output=bin-debug/ElixysMobile.swf src/ElixysMobile.as

echo *** Creating IPA
cd bin-debug
cmd /C %ADT% -package -target ipa-ad-hoc -storetype PKCS12 -keystore %DEVCERTS%\ShaneDeveloperCertificates.p12 -storepass devel -provisioning-profile %DEVCERTS%\Elixys_ShaneiPad.mobileprovision ..\Elixys.ipa ElixysMobile-app.xml ElixysIcon29.png ElixysIcon48.png ElixysIcon57.png ElixysIcon72.png ElixysIcon512.png ElixysMobile.swf -extdir ..\..\Elixys\VideoANE
cd ..
