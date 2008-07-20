# TODO:
# - verify build with FHS-compliant libexecdir (=%{_libdir})
# - chkconfig
Summary:	A web-based user account administration interface
Summary(pl.UTF-8):	Oparty na WWW interfejs do administrowania kontami użytkowników
Name:		usermin
Version:	1.300
Release:	0.1
License:	Freeware
Group:		System/Tools
Source0:	http://www.webmin.com/download/%{name}-%{version}.tar.gz
# Source0-md5:	d5da4ecbf388b740edc1f25b15ddd39a
Requires:	webserver
Requires:	/bin/rm
Requires:	/bin/sh
Requires:	/usr/bin/perl
BuildArch:      noarch
BuildRoot:      %{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_libdir}

%description
A web-based user account administration interface for Unix systems.

After installation, enter the URL http://localhost:20000/ into your
browser and login as any user on your system.

%description -l pl.UTF-8
Oparty na WWW interfejs do administrowania kontami użytkowników.

Po zainstalowaniu wystarczy w przeglądarce wpisać URL
http://localhost:20000/ i zalogować jako dowolny użytkownik.

%prep
%setup -q

%build
(find . -name '*.cgi' ; find . -name '*.pl') | perl perlpath.pl %{__perl} -
rm -f mount/freebsd-mounts-*
rm -f mount/openbsd-mounts-*
chmod -R og-w .

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_libexecdir}/usermin,/var/lib/usermin}
install -d $RPM_BUILD_ROOT/etc/sysconfig
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT/etc/pam.d

cp -rp * $RPM_BUILD_ROOT%{_libexecdir}/usermin
cp usermin-daemon $RPM_BUILD_ROOT/etc/sysconfig/usermin
cp usermin-init $RPM_BUILD_ROOT/etc/rc.d/init.d/usermin
cp usermin-pam $RPM_BUILD_ROOT/etc/pam.d/usermin
echo rpm >$RPM_BUILD_ROOT%{_libexecdir}/usermin/install-type
echo usermin >$RPM_BUILD_ROOT%{_libexecdir}/usermin/rpm-name

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_libexecdir}/usermin
%attr(754,root,root) /etc/rc.d/init.d/usermin
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/usermin
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/usermin

%post
inetd=`grep "^inetd=" %{_sysconfdir}/usermin/miniserv.conf 2>/dev/null | sed -e 's/inetd=//g'`
if [ "$1" != 1 ]; then
	# Upgrading the RPM, so stop the old usermin properly
	if [ "" != "1" ]; then
		/etc/rc.d/init.d/usermin stop >/dev/null 2>&1
	fi
fi
cd %{_libexecdir}/usermin
config_dir=%{_sysconfdir}/usermin
var_dir=/var/lib/usermin
perl=%{__perl}
autoos=3
port=20000
host=`hostname`
ssl=1
atboot=1
nochown=1
autothird=1
noperlpath=1
nouninstall=1
nostart=1
export config_dir var_dir perl autoos port ssl nochown autothird noperlpath nouninstall nostart allow
./setup.sh >/var/lib/usermin/usermin-setup.out 2>&1
rm -f /var/lock/subsys/usermin
if [ "" != "1" ]; then
	# XXX: only if it was running before upgrade!
	#/etc/rc.d/init.d/usermin start >/dev/null 2>&1 </dev/null
fi
cat >%{_sysconfdir}/usermin/uninstall.sh <<EOFF
#!/bin/sh
printf "Are you sure you want to uninstall Usermin? (y/n) : "
read answer
printf "\n"
if [ "\$answer" = "y" ]; then
	echo "Removing usermin RPM .."
	rpm -e usermin
	echo "Done!"
fi
EOFF
chmod +x %{_sysconfdir}/usermin/uninstall.sh
port=`grep "^port=" %{_sysconfdir}/usermin/miniserv.conf | sed -e 's/port=//g'`
perl -e 'use Net::SSLeay' >/dev/null 2>/dev/null
sslmode=0
if [ "$?" = "0" ]; then
	grep ssl=1 %{_sysconfdir}/usermin/miniserv.conf >/dev/null 2>/dev/null
	if [ "$?" = "0" ]; then
		sslmode=1
	fi
fi
if [ "$sslmode" = "1" ]; then
	echo "Usermin install complete. You can now login to https://$host:$port/"
else
	echo "Usermin install complete. You can now login to http://$host:$port/"
fi
echo "as any user on your system."

%preun
if [ "$1" = 0 ]; then
	grep root=%{_libexecdir}/usermin %{_sysconfdir}/usermin/miniserv.conf >/dev/null 2>&1
	if [ "$?" = 0 ]; then
		# RPM is being removed, and no new version of usermin
		# has taken it's place. Stop the server
		/etc/rc.d/init.d/usermin stop >/dev/null 2>&1
		/bin/true
	fi
fi

%postun
if [ "$1" = 0 ]; then
	grep root=%{_libexecdir}/usermin %{_sysconfdir}/usermin/miniserv.conf >/dev/null 2>&1
	if [ "$?" = 0 ]; then
		# RPM is being removed, and no new version of usermin
		# has taken it's place. Delete the config files
		# XXX: wrong
		#rm -rf %{_sysconfdir}/usermin /var/lib/usermin
	fi
fi
