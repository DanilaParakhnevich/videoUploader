Name:          	BuxarVideoUploader
Version:        1.0.0
Release:        0
Summary:        Application for video downloading/uploading
License:	-
Source0:        BuxarVideoUploader.tar.gz
Group:		Development/Other
AutoReq:	no
Requires:       bash

%description
Application for video downloading/uploading

%install
install -m 755 -d %{buildroot}/usr/share/
tar -xf %{SOURCE0} -C %{buildroot}/usr/share/

%files
/usr/share/BuxarVideoUploader/

%post
sudo bash -c "echo '[Desktop Entry]
Version=1.0.0.0
GenericName[ru]=BuxarVideoUploader
Name=BuxarVideoUploader
Comment=BuxarVideoUploader
Icon=/usr/share/BuxarVideoUploader/dist/Application/icon.ico
Exec=sh -c \"cd /usr/share/BuxarVideoUploader/dist/Application && ./Application\"
Terminal=false
StartupWMClass=Application
Categories=Network;FileTransfer;
Type=Application' > /usr/share/applications/BuxarVideoUploader.desktop"

sudo chmod -R 777 /usr/share/BuxarVideoUploader
sudo chmod a+x /usr/share/BuxarVideoUploader/dist/Application/Application

%clean
rm -rf $RPM_BUILD_ROOT/usr/share

%postun
sudo rm /usr/share/applications/BuxarVideoUploader.desktop