%define __spec_install_post %{nil}

Summary:	A web-based user account administration interface
Name:		usermin
Version:	1.300
Release:	1
License:	Freeware
Group:		System/Tools
Requires:	webserver
Requires:	/bin/rm
Requires:	/bin/sh
Requires:	/usr/bin/perl
Provides:	%{name}-%{version}
Source0:	http://www.webmin.com/download/%{name}-%{version}.tar.gz
# Source0-md5:	d5da4ecbf388b740edc1f25b15ddd39a
BuildArch:      noarch
BuildRoot:      %{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A web-based user account administration interface for Unix systems.

After installation, enter the URL http://localhost:20000/ into your
browser and login as any user on your system.

%prep
%setup -q

%build
(find . -name '*.cgi' ; find . -name '*.pl') | perl perlpath.pl %{__perl} -
rm -f mount/freebsd-mounts-*
rm -f mount/openbsd-mounts-*
chmod -R og-w .

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_prefix}/libexec/usermin
install -d $RPM_BUILD_ROOT/etc/sysconfig/daemons
install -d $RPM_BUILD_ROOT/etc/rc.d/{rc0.d,rc1.d,rc2.d,rc3.d,rc5.d,rc6.d}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
install -d $RPM_BUILD_ROOT/etc/pam.d
cp -rp * $RPM_BUILD_ROOT%{_prefix}/libexec/usermin
cp usermin-daemon $RPM_BUILD_ROOT/etc/sysconfig/daemons/usermin
cp usermin-init $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/usermin
cp usermin-pam $RPM_BUILD_ROOT/etc/pam.d/usermin
ln -s %{_sysconfdir}/init.d/usermin $RPM_BUILD_ROOT/etc/rc.d/rc2.d/S99usermin
ln -s %{_sysconfdir}/init.d/usermin $RPM_BUILD_ROOT/etc/rc.d/rc3.d/S99usermin
ln -s %{_sysconfdir}/init.d/usermin $RPM_BUILD_ROOT/etc/rc.d/rc5.d/S99usermin
ln -s %{_sysconfdir}/init.d/usermin $RPM_BUILD_ROOT/etc/rc.d/rc0.d/K10usermin
ln -s %{_sysconfdir}/init.d/usermin $RPM_BUILD_ROOT/etc/rc.d/rc1.d/K10usermin
ln -s %{_sysconfdir}/init.d/usermin $RPM_BUILD_ROOT/etc/rc.d/rc6.d/K10usermin
echo rpm >$RPM_BUILD_ROOT%{_prefix}/libexec/usermin/install-type
echo usermin >$RPM_BUILD_ROOT%{_prefix}/libexec/usermin/rpm-name

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_prefix}/libexec/usermin
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/daemons/usermin
%attr(754,root,root) /etc/rc.d/init.d/usermin
%config /etc/pam.d/usermin

%pre
perl <<EOD;
# maketemp.pl
# Create the /tmp/.webmin directory if needed

\$tmp_dir = \$ENV{'tempdir'} || "/tmp/.webmin";

while(\$tries++ < 10) {
	local @st = lstat(\$tmp_dir);
	exit(0) if (\$st[4] == \$< && (-d _) && (\$st[2] & 0777) == 0755);
	if (@st) {
		unlink(\$tmp_dir) || rmdir(\$tmp_dir) ||
			system("/bin/rm -rf ".quotemeta(\$tmp_dir));
		}
	mkdir(\$tmp_dir, 0755) || next;
	chown(\$<, \$(, \$tmp_dir);
	chmod(0755, \$tmp_dir);
	}
exit(1);

EOD
if [ "$?" != "0" ]; then
	echo "Failed to create or check temp files directory /tmp/.webmin"
	exit 1
fi
perl >/tmp/.webmin/$$.check <<EOD;
if (-r "/etc/.issue") {
	\$etc_issue = \`cat /etc/.issue\`;
	}
elsif (-r "/etc/issue") {
	\$etc_issue = \`cat /etc/issue\`;
	}
\$uname = \`uname -a\`;
if (\$uname =~ /SunOS.*\\s5\\.5\\.1\\s/i) {
	print "oscheck='Sun Solaris'\\n";
	}
elsif (\$uname =~ /SunOS.*\\s5\\.6\\s/i) {
	print "oscheck='Sun Solaris'\\n";
	}
elsif (\$uname =~ /SunOS.*\\s5\\.(\\S+)\\s/i) {
	print "oscheck='Sun Solaris'\\n";
	}
elsif (\$etc_issue =~ /Lycoris Desktop/i) {
	print "oscheck='Lycoris Desktop/LX'\\n";
	}
elsif (\$etc_issue =~ /OpenLinux.*eServer.*\\n.*\\s2\\.3\\s/i) {
	print "oscheck='Caldera OpenLinux eServer'\\n";
	}
elsif (\$etc_issue =~ /OpenLinux.*\\n.*\\s2\\.3\\s/i) {
	print "oscheck='Caldera OpenLinux'\\n";
	}
elsif (\$etc_issue =~ /OpenLinux.*\\n.*\\s2\\.4\\s/i) {
	print "oscheck='Caldera OpenLinux'\\n";
	}
elsif (\$etc_issue =~ /OpenLinux.*\\n.*\\s2\\.5\\s/i || \$etc_issue =~ /Caldera.*2000/i) {
	print "oscheck='Caldera OpenLinux'\\n";
	}
elsif (\$etc_issue =~ /OpenLinux.*3\\.1/i) {
	print "oscheck='Caldera OpenLinux'\\n";
	}
elsif (\$etc_issue =~ /OpenLinux.*3\\.2/i) {
	print "oscheck='Caldera OpenLinux'\\n";
	}
elsif (\`cat /etc/whitebox-release 2>/dev/null\` =~ /White\\s+Box\\s+Enterprise\\s+Linux\\s+release\\s+(\\S+)/i) {
	print "oscheck='Whitebox Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /Tao\\s+Linux\\s+release\\s+(\\S+)/i) {
	print "oscheck='Tao Linux'\\n";
	}
elsif (\`cat /etc/centos-release /etc/redhat-release 2>/dev/null\` =~ /CentOS\\s+release\\s+(\\S+)/i && \$1 < 4) {
	print "oscheck='CentOS Linux'\\n";
	}
elsif (\`cat /etc/centos-release /etc/redhat-release 2>/dev/null\` =~ /CentOS\\s+release\\s+(\\S+)/i && \$1 >= 4) {
	print "oscheck='CentOS Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /Scientific\\s+Linux.*\\s+release\\s+(\\S+)/i && \$1 < 4) {
	print "oscheck='Scientific Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /Scientific\\s+Linux.*\\s+release\\s+(\\S+)/i && \$1 >= 4) {
	print "oscheck='Scientific Linux'\\n";
	}
elsif (\`cat /etc/redhtat-release 2>/dev/null\` =~ /Gralinux\\s+(ES|AS|WS)\\s+release\\s+(\\d+)/i) {
	print "oscheck='Gralinux'\\n";
	}
elsif (\`cat /etc/neoshine-release 2>/dev/null\` =~ /NeoShine\\s+Linux.*release\\s+(\\d+)/i) {
	print "oscheck='NeoShine Linux'\\n";
	}
elsif (\`cat /etc/endian-release 2>/dev/null\` =~ /release\\s+(\\S+)/) {
	print "oscheck='Endian Firewall Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /(Advanced\\s+Server.*2\\.1)|(AS.*2\\.1)/i) {
	print "oscheck='Redhat Enterprise Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /ES.*2\\.1/) {
	print "oscheck='Redhat Enterprise Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /WS.*2\\.1/) {
	print "oscheck='Redhat Enterprise Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /(3\\.0AS)|(2\\.9\\.5AS)|(AS\\s+release\\s+3)/i) {
	print "oscheck='Redhat Enterprise Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /(ES|AS|WS)\\s+release\\s+(\\S+)/) {
	print "oscheck='Redhat Enterprise Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /Red.*Hat\\s+Enterprise\\s+Linux\\s+Server\\s+release\\s+(\\d+)/) {
	print "oscheck='Redhat Enterprise Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /Desktop\\s+release\\s+(\\S+)/i || \`cat /etc/redhat-release 2>/dev/null\` =~ /ES\\s+release\\s+(\\S+)/i) {
	print "oscheck='Redhat Linux Desktop'\\n";
	}
elsif (\`cat /etc/alphacore-release 2>/dev/null\` =~ /Alpha\\s*Core\\s+release\\s+(\\S+)\\s/i) {
	print "oscheck='AlphaCore Linux'\\n";
	}
elsif (\`cat /etc/redhat-release /etc/fedora-release 2>/dev/null\` =~ /X\\/OS.*release\\s(\\S+)\\s/i) {
	print "oscheck='X/OS Linux'\\n";
	}
elsif (\`cat /etc/release /etc/asianux-release 2>/dev/null\` =~ /Asianux\\s+release\\s+(\\S+)/i) {
	print "oscheck='Asianux'\\n";
	}
elsif (\`cat /etc/Haansoft-release 2>/dev/null\` =~ /Haansoft\\s+Linux\\s+OS\\s+release\\s+(\\S+)/i) {
	print "oscheck='Haansoft Linux'\\n";
	}
elsif (\`cat /etc/caos-release 2>/dev/null\` =~ /release\\s+(\\S+)/i) {
	print "oscheck='cAos Linux'\\n";
	}
elsif (\`cat /etc/redhat-release 2>/dev/null\` =~ /red.*hat.*release\\s+(\\S+)/i && \`cat /etc/redhat-release 2>/dev/null\` !~ /[eE]nterprise|AS|ES|WS|[aA]dvanced/) {
	print "oscheck='Redhat Linux'\\n";
	}
elsif (\`cat /etc/redhat-release /etc/fedora-release 2>/dev/null\` =~ /Fedora.*\\s([0-9\\.]+)\\s/i || \`cat /etc/redhat-release /etc/fedora-release 2>/dev/null\` =~ /Fedora.*\\sFC(\\S+)\\s/i) {
	print "oscheck='Redhat Linux'\\n";
	}
elsif (\`cat /tmp/wd/version 2>/dev/null\` =~ /2\\.1\\.0/) {
	print "oscheck='White Dwarf Linux'\\n";
	}
elsif (\`cat /etc/slamd64-version 2>/dev/null\` =~ /\\s([0-9\\.]+)/) {
	print "oscheck='Slamd64 Linux'\\n";
	}
elsif (\`cat /etc/slackware-version 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='Slackware Linux'\\n";
	}
elsif (\$etc_issue =~ /Xandros.*\\s2\\.0/i) {
	print "oscheck='Xandros Linux'\\n";
	}
elsif (\$etc_issue =~ /Xandros.*\\s3\\.0/i) {
	print "oscheck='Xandros Linux'\\n";
	}
elsif (\$etc_issue =~ /Xandros.*\\s(4\\.\\d+)/i) {
	print "oscheck='Xandros Linux'\\n";
	}
elsif (\$etc_issue =~ /APLINUX.*1\\.3/i) {
	print "oscheck='APLINUX'\\n";
	}
elsif (\`cat /etc/bigblock-revision 2>/dev/null\` =~ /Version:\\s(1[0-9\\.-]+)\\s/i) {
	print "oscheck='BigBlock'\\n";
	}
elsif (\`cat /etc/bigblock-revision 2>/dev/null\` =~ /Version:\\s(2[0-9\\.-]+)\\s/i) {
	print "oscheck='BigBlock'\\n";
	}
elsif (\$etc_issue =~ /Ubuntu.*\\sgutsy/i) {
	print "oscheck='Ubuntu Linux'\\n";
	}
elsif (\$etc_issue =~ /Ubuntu.*\\s(7\\.[0-9\\.]+)\\s/i) {
	print "oscheck='Ubuntu Linux'\\n";
	}
elsif (\$etc_issue =~ /Ubuntu.*\\s([0-9\\.]+)\\s/i) {
	print "oscheck='Ubuntu Linux'\\n";
	}
elsif (\$etc_issue =~ /MEPIS/ && \`cat /etc/debian_version 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='Mepis Linux'\\n";
	}
elsif (\$etc_issue =~ /MEPIS/ && \`cat /etc/debian_version 2>/dev/null\` =~ /(stable)/) {
	print "oscheck='Mepis Linux'\\n";
	}
elsif (\$etc_issue =~ /Debian.*\\s([0-9\\.]+)\\s/i || \`cat /etc/debian_version 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='Debian Linux'\\n";
	}
elsif (\$etc_issue =~ /Debian.*\\stesting\\/unstable\\s/i) {
	print "oscheck='Debian Linux'\\n";
	}
elsif (\$etc_issue =~ /Debian.*lenny\\/sid\\s/i) {
	print "oscheck='Debian Linux'\\n";
	}
elsif (\`cat /etc/SLOX-release 2>/dev/null\` =~ /VERSION\\s+=\\s+(\\S+)/i) {
	print "oscheck='SuSE OpenExchange Linux'\\n";
	}
elsif (\$etc_issue =~ /SuSE\\s+SLES-(\\S+)/i) {
	print "oscheck='SuSE SLES Linux'\\n";
	}
elsif (\`cat /etc/SuSE-release 2>/dev/null\` =~ /([0-9\\.]+)/ || \$etc_issue =~ /SuSE\\s+Linux\\s+(\\S+)\\s/i) {
	print "oscheck='SuSE Linux'\\n";
	}
elsif (\`cat /etc/UnitedLinux-release 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='United Linux'\\n";
	}
elsif (\$etc_issue =~ /Corel\\s+LINUX\\s+(\\S+)/i) {
	print "oscheck='Corel Linux'\\n";
	}
elsif (\`cat /etc/turbolinux-release 2>/dev/null\` =~ /([0-9\\.]+)/i) {
	print "oscheck='TurboLinux'\\n";
	}
elsif (\$etc_issue =~ /Cobalt\\s+Linux\\s+release\\s+(\\S+)/i || \`cat /etc/cobalt-release 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='Cobalt Linux'\\n";
	}
elsif (\`uname -r\` =~ /2.2.16/ && -r "/etc/cobalt-release") {
	print "oscheck='Cobalt Linux'\\n";
	}
elsif (\$etc_issue =~ /Mandrake\\s+Corporate\\s+Server\\s+release\\s+1\\.0/i) {
	print "oscheck='Mandrake Linux Corporate Server'\\n";
	}
elsif (\`cat /etc/mandrake-release 2>/dev/null\` =~ /pclinuxos\\s+Linux\\s+release\\s+2005/i) {
	print "oscheck='pclinuxos Linux'\\n";
	}
elsif (\`cat /etc/mandrake-release 2>/dev/null\` =~ /pclinuxos\\s+Linux\\s+release\\s+2006/i) {
	print "oscheck='pclinuxos Linux'\\n";
	}
elsif (\`cat /etc/mandrake-release 2>/dev/null\` =~ /PCLinuxOS\\s+release\\s+2007/i) {
	print "oscheck='pclinuxos Linux'\\n";
	}
elsif (\$etc_issue =~ /Mandrake\\s+release\\s+5\\.3/i) {
	print "oscheck='Mandrake Linux'\\n";
	}
elsif (\$etc_issue =~ /Mandrake\\s+release\\s+6\\.0/i) {
	print "oscheck='Mandrake Linux'\\n";
	}
elsif (\$etc_issue =~ /Mandrake\\s+release\\s+6\\.1/i) {
	print "oscheck='Mandrake Linux'\\n";
	}
elsif (\$etc_issue =~ /Mandrake\\s+release\\s+7\\.0/i) {
	print "oscheck='Mandrake Linux'\\n";
	}
elsif (\$etc_issue =~ /Mandrake\\s+release\\s+7\\.1/i) {
	print "oscheck='Mandrake Linux'\\n";
	}
elsif (\`cat /etc/mandrake-release 2>/dev/null\` =~ /Mandrake.*?([0-9\\.]+)/i || \$etc_issue =~ /Mandrake\\s+release\\s+([0-9\\.]+)/i || \$etc_issue =~ /Mandrakelinux\\s+release\\s+([0-9\\.]+)/i) {
	print "oscheck='Mandrake Linux'\\n";
	}
elsif (\$etc_issue =~ /(Mandrakelinux|Mandriva).*(2006\\.\\d+)/i || \`cat /etc/mandrake-release 2>/dev/null\` =~ /(Mandrakelinux|Mandriva).*(2007\\.\\d+)/i) {
	print "oscheck='Mandriva Linux'\\n";
	}
elsif (\$etc_issue =~ /(Mandrakelinux|Mandriva).*(2007\\.\\d+)/i || \`cat /etc/mandrake-release 2>/dev/null\` =~ /(Mandrakelinux|Mandriva).*(2007\\.\\d+)/i) {
	print "oscheck='Mandriva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*3\\.0/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*4\\.0/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*4\\.1/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*4\\.2/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*5\\.0/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*5\\.1/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*6\\.0/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*7\\.0/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*\\s8/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*\\s9/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Conectiva.*Linux.*\\s10\\s/i) {
	print "oscheck='Conectiva Linux'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*Linux.*\\s5\\.0/i) {
	print "oscheck='ThizLinux Desktop'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*Linux.*\\s6\\.0/i) {
	print "oscheck='ThizLinux Desktop'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*Linux.*\\s6\\.2/i) {
	print "oscheck='ThizLinux Desktop'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*Linux.*\\s7\\.0/i) {
	print "oscheck='ThizLinux Desktop'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*\\s?Server.*\\s4\\.3/i) {
	print "oscheck='ThizServer'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*\\s?Server.*\\s6\\.0/i) {
	print "oscheck='ThizServer'\\n";
	}
elsif (\$etc_issue =~ /Thiz.*\\s?Server.*\\s7\\.0/i) {
	print "oscheck='ThizServer'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2001.*January/i || \$etc_issue =~ /2001.*January/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2001.*February/i || \$etc_issue =~ /2001.*February/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2001.*May/i || \$etc_issue =~ /2001.*May/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2001.*June/i || \$etc_issue =~ /2001.*June/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2001.*August/i || \$etc_issue =~ /2001.*August/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2002.*February/i || \$etc_issue =~ /2002.*February/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2002.*March/i || \$etc_issue =~ /2002.*March/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2002.*May/i || \$etc_issue =~ /2002.*May/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2002.*July/i || \$etc_issue =~ /2002.*July/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/msclinux-release 2>/dev/null\` =~ /2002.*Nov/i || \$etc_issue =~ /2002.*Nov/i) {
	print "oscheck='MSC Linux'\\n";
	}
elsif (\`cat /etc/scilinux-relase 2>/dev/null\` =~ /2003.*Summer/i) {
	print "oscheck='SCI Linux'\\n";
	}
elsif (\`cat /etc/scilinux-relase 2>/dev/null\` =~ /2004.*Summer/i) {
	print "oscheck='SCI Linux'\\n";
	}
elsif (\`cat /etc/scilinux-relase 2>/dev/null\` =~ /2005.*Summer/i) {
	print "oscheck='SCI Linux'\\n";
	}
elsif (\$etc_issue =~ /LinuxPPC\\s+2000/i) {
	print "oscheck='LinuxPPC'\\n";
	}
elsif (\$etc_issue =~ /Trustix.*Enterprise.*([0-9\\.]+)/i) {
	print "oscheck='Trustix SE'\\n";
	}
elsif (\$etc_issue =~ /Trustix.*1\\.1/i) {
	print "oscheck='Trustix'\\n";
	}
elsif (\$etc_issue =~ /Trustix.*1\\.2/i) {
	print "oscheck='Trustix'\\n";
	}
elsif (\$etc_issue =~ /Trustix.*1\\.5/i) {
	print "oscheck='Trustix'\\n";
	}
elsif (\$etc_issue =~ /Trustix.*\\s([0-9\\.]+)/i) {
	print "oscheck='Trustix'\\n";
	}
elsif (\$etc_issue =~ /Tawie\\s+Server\\s+Linux.*([0-9\\.]+)/i) {
	print "oscheck='Tawie Server Linux'\\n";
	}
elsif (\$etc_issue =~ /tinysofa.*release\\s+1\\.0/i) {
	print "oscheck='TinySofa Linux'\\n";
	}
elsif (\`cat /etc/tinysofa-release 2>/dev/null\` =~ /classic.*release\\s+2\\.0/i) {
	print "oscheck='TinySofa Linux'\\n";
	}
elsif (\`cat /etc/tinysofa-release 2>/dev/null\` =~ /enterprise.*release\\s+2\\.0/i) {
	print "oscheck='TinySofa Linux'\\n";
	}
elsif (\$etc_issue =~ /Cendio\\s*LBS.*\\s3\\.1/i || \`cat /etc/lbs-release 2>/dev/null\` =~ /3\\.1/) {
	print "oscheck='Cendio LBS Linux'\\n";
	}
elsif (\$etc_issue =~ /Cendio\\s*LBS.*\\s3\\.2/i || \`cat /etc/lbs-release 2>/dev/null\` =~ /3\\.2/) {
	print "oscheck='Cendio LBS Linux'\\n";
	}
elsif (\$etc_issue =~ /Cendio\\s*LBS.*\\s3\\.3/i || \`cat /etc/lbs-release 2>/dev/null\` =~ /3\\.3/) {
	print "oscheck='Cendio LBS Linux'\\n";
	}
elsif (\$etc_issue =~ /Cendio\\s*LBS.*\\s4\\.0/i || \`cat /etc/lbs-release 2>/dev/null\` =~ /4\\.0/) {
	print "oscheck='Cendio LBS Linux'\\n";
	}
elsif (\$etc_issue =~ /Cendio\\s*LBS.*\\s4\\.1/i || \`cat /etc/lbs-release 2>/dev/null\` =~ /4\\.1/) {
	print "oscheck='Cendio LBS Linux'\\n";
	}
elsif (\`cat /etc/ute-release 2>/dev/null\` =~ /Ute\\s+Linux\\s+release\\s+1\\.0/i) {
	print "oscheck='Ute Linux'\\n";
	}
elsif (\$etc_issue =~ /Lanthan\\s+Linux\\s+release\\s+1\\.0/i || \`cat /etc/lanthan-release 2>/dev/null\` =~ /1\\.0/) {
	print "oscheck='Lanthan Linux'\\n";
	}
elsif (\$etc_issue =~ /Lanthan\\s+Linux\\s+release\\s+2\\.0/i || \`cat /etc/lanthan-release 2>/dev/null\` =~ /2\\.0/) {
	print "oscheck='Lanthan Linux'\\n";
	}
elsif (\$etc_issue =~ /Lanthan\\s+Linux\\s+release\\s+3\\.0/i || \`cat /etc/lanthan-release 2>/dev/null\` =~ /3\\.0/) {
	print "oscheck='Lanthan Linux'\\n";
	}
elsif (\$etc_issue =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.0\\s+/i || \`cat /etc/yellowdog-release 2>/dev/null\` =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.0\\s+/i) {
	print "oscheck='Yellow Dog Linux'\\n";
	}
elsif (\$etc_issue =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.1\\s+/i || \`cat /etc/yellowdog-release 2>/dev/null\` =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.1\\s+/i) {
	print "oscheck='Yellow Dog Linux'\\n";
	}
elsif (\$etc_issue =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.2\\s+/i || \`cat /etc/yellowdog-release 2>/dev/null\` =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.2\\s+/i) {
	print "oscheck='Yellow Dog Linux'\\n";
	}
elsif (\$etc_issue =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.3\\s+/i || \`cat /etc/yellowdog-release 2>/dev/null\` =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+2\\.3\\s+/i) {
	print "oscheck='Yellow Dog Linux'\\n";
	}
elsif (\$etc_issue =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+3\\.0\\s+/i || \`cat /etc/yellowdog-release 2>/dev/null\` =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+3\\.0\\s+/i) {
	print "oscheck='Yellow Dog Linux'\\n";
	}
elsif (\$etc_issue =~ /Yellow\\s+Dog\\s+Linux\\s+release\\s+4\\.0\\s+/i || \`cat /etc/yellowdog-release 2>/dev/null\` =~ /\\s4\\.0\\s/i) {
	print "oscheck='Yellow Dog Linux'\\n";
	}
elsif (\`cat /etc/latinux-release 2>/dev/null\` =~ /Latinux\\s+8\\s/i) {
	print "oscheck='Corvus Latinux'\\n";
	}
elsif (\$etc_issue =~ /Immunix.*\\s([0-9\\.]+)/i || \`cat /etc/immunix-release 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='Immunix Linux'\\n";
	}
elsif (-d "/usr/portage") {
	print "oscheck='Gentoo Linux'\\n";
	}
elsif (\`cat /etc/securelinux-release 2>/dev/null\` =~ /SecureLinux.*1\\.0/i) {
	print "oscheck='Secure Linux'\\n";
	}
elsif (\`cat /etc/openna-release 2>/dev/null\` =~ /release\\s+1\\.0\\s/i) {
	print "oscheck='OpenNA Linux'\\n";
	}
elsif (\`cat /etc/openna-release 2>/dev/null\` =~ /release\\s+2\\.0\\s/i) {
	print "oscheck='OpenNA Linux'\\n";
	}
elsif (-r "/etc/antitachyon-distribution" && \`uname -r\` =~ /2\\.4\\./) {
	print "oscheck='SoL Linux'\\n";
	}
elsif (-r "/etc/antitachyon-distribution" && \`uname -r\` =~ /2\\.6\\./) {
	print "oscheck='SoL Linux'\\n";
	}
elsif (\$etc_issue =~ /coherent\\s*technology.*\\s([0-9\\.]+)/i || \`cat /etc/coherent-release 2>/dev/null\` =~ /([0-9\\.]+)/ ) {
	print "oscheck='Coherent Technology Linux'\\n";
	}
elsif (\$etc_issue =~ /PS2\\s+Linux\\s+release\\s+1.0/i) {
	print "oscheck='Playstation Linux'\\n";
	}
elsif (\`cat /etc/startcom-release 2>/dev/null\` =~ /([0-9\\.]+)/) {
	print "oscheck='StartCom Linux'\\n";
	}
elsif (\`cat /etc/yoper-release 2>/dev/null\` =~ /Yoper\\s+Linux\\s+2.0/i) {
	print "oscheck='Yoper Linux'\\n";
	}
elsif (\`cat /etc/yoper-release 2>/dev/null\` =~ /Yoper\\s+Linux\\s+2.1/i) {
	print "oscheck='Yoper Linux'\\n";
	}
elsif (\`cat /etc/yoper-release 2>/dev/null\` =~ /Yoper\\s+Linux\\s+2.2/i) {
	print "oscheck='Yoper Linux'\\n";
	}
elsif (\`cat /etc/CxM-release 2>/dev/null\` =~ /8\\.1/ || \$etc_issue =~ /Caixa\\s+8\\.1\\s/i) {
	print "oscheck='Caixa Magica'\\n";
	}
elsif (\`cat /etc/CxM-release 2>/dev/null\` =~ /10\\.0/ || \$etc_issue =~ /Caixa\\s+10\\.0\\s/i) {
	print "oscheck='Caixa Magica'\\n";
	}
elsif (\`cat /etc/openmamba-release 2>/dev/null\` =~ /openmamba\\s+release\\s+(\\S+)/i) {
	print "oscheck='openmamba Linux'\\n";
	}
elsif (\$uname =~ /FreeBSD.*?\\s([0-9]+\\.[0-9\\.]+)/i) {
	print "oscheck='FreeBSD'\\n";
	}
elsif (\$uname =~ /DragonFly.*?\\s1\\.0A/i) {
	print "oscheck='DragonFly BSD'\\n";
	}
elsif (\$uname =~ /DragonFly.*?\\s1\\.2A/i) {
	print "oscheck='DragonFly BSD'\\n";
	}
elsif (\$uname =~ /OpenBSD.*?\\s([0-9\\.]+)/i) {
	print "oscheck='OpenBSD'\\n";
	}
elsif (\$uname =~ /NetBSD.*1\\.5/i) {
	print "oscheck='NetBSD'\\n";
	}
elsif (\$uname =~ /NetBSD.*1\\.6/i) {
	print "oscheck='NetBSD'\\n";
	}
elsif (\$uname =~ /NetBSD.*2\\.0/i) {
	print "oscheck='NetBSD'\\n";
	}
elsif (\$uname =~ /NetBSD.*3\\.0/i) {
	print "oscheck='NetBSD'\\n";
	}
elsif (\$uname =~ /BSDI.*\\s([0-9\\.]+)/i) {
	print "oscheck='BSDI'\\n";
	}
elsif (\$uname =~ /HP-UX.*(1[01]\\.[0-9\\.]+)/) {
	print "oscheck='HP/UX'\\n";
	}
elsif (\$uname =~ /IRIX.*([0-9]+\\.[0-9]+)/i) {
	print "oscheck='SGI Irix'\\n";
	}
elsif (\$uname =~ /OSF1.*4\\.0/) {
	print "oscheck='DEC/Compaq OSF/1'\\n";
	}
elsif (\$uname =~ /OSF1.*V5.1/) {
	print "oscheck='DEC/Compaq OSF/1'\\n";
	}
elsif (\$uname =~ /AIX\\s+\\S+\\s+(\\d+)\\s+(\\d+)\\s+/i) {
	print "oscheck='IBM AIX'\\n";
	}
elsif (\$uname =~ /SCO_SV.*\\s5\\./i) {
	print "oscheck='SCO OpenServer'\\n";
	}
elsif (\$uname =~ /SCO_SV.*\\s6\\./i) {
	print "oscheck='SCO OpenServer'\\n";
	}
elsif (\`sw_vers 2>/dev/null\` =~ /ProductVersion:\\s+10\\.0/i) {
	print "oscheck='Mac OS X'\\n";
	}
elsif (\`sw_vers 2>/dev/null\` =~ /ProductVersion:\\s+10\\.1/i) {
	print "oscheck='Mac OS X'\\n";
	}
elsif (\`sw_vers 2>/dev/null\` =~ /ProductVersion:\\s+10\\.2/i) {
	print "oscheck='Mac OS X'\\n";
	}
elsif (\`sw_vers 2>/dev/null\` =~ /ProductVersion:\\s+10\\.3/i) {
	print "oscheck='Mac OS X'\\n";
	}
elsif (\`sw_vers 2>/dev/null\` =~ /ProductVersion:\\s+10\\.4/i) {
	print "oscheck='Mac OS X'\\n";
	}
elsif (\$uname =~ /Darwin.*\\s([0-9\\.]+)/) {
	print "oscheck='Darwin'\\n";
	}
elsif (\`cat /etc/SuSE-release 2>/dev/null\` =~ /Java Desktop System.*\\nVERSION = 1\\.0/i) {
	print "oscheck='Sun Java Desktop System'\\n";
	}
elsif (\`cat /etc/SuSE-release 2>/dev/null\` =~ /Java Desktop System.*\\nVERSION = 2\\.0/i) {
	print "oscheck='Sun Java Desktop System'\\n";
	}
elsif (\`cat /etc/SuSE-release 2>/dev/null\` =~ /Java Desktop System.*\\nVERSION = 3\\.0/i) {
	print "oscheck='Sun Java Desktop System'\\n";
	}
elsif (\$uname =~ /SunOS.*\\s5\\.9\\s/i && \`cat /etc/sun-release 2>/dev/null\` =~ /Sun\\s+Java\\s+Desktop/) {
	print "oscheck='Sun Java Desktop System'\\n";
	}
elsif (\`uname -r\` =~ /2\\.0\\./) {
	print "oscheck='Generic Linux'\\n";
	}
elsif (\`uname -r\` =~ /2\\.2\\./) {
	print "oscheck='Generic Linux'\\n";
	}
elsif (\`uname -r\` =~ /2\\.4\\./) {
	print "oscheck='Generic Linux'\\n";
	}
elsif (\`uname -r\` =~ /2\\.4\\./) {
	print "oscheck='Generic Linux'\\n";
	}
elsif (\`uname -r\` =~ /2\\.6\\./) {
	print "oscheck='Generic Linux'\\n";
	}
elsif (\`uname -r\` =~ /2\\.7\\./) {
	print "oscheck='Generic Linux'\\n";
	}
elsif ((-d "c:/windows" || -d "c:/winnt") && \`ver\` =~ /XP/) {
	print "oscheck='Windows'\\n";
	}
elsif ((-d "c:/windows" || -d "c:/winnt") && \`ver\` =~ /2000/) {
	print "oscheck='Windows'\\n";
	}
elsif ((-d "c:/windows" || -d "c:/winnt") && \`ver\` =~ /2003|\\s5\\.2/) {
	print "oscheck='Windows'\\n";
	}

EOD
. /tmp/.webmin/$$.check
rm -f /tmp/.webmin/$$.check
if [ ! -r /etc/usermin/config ]; then
	if [ "$oscheck" = "" ]; then
		echo Unable to identify operating system
		exit 2
	fi
	echo Operating system is $oscheck
	if [ "$USERMIN_PORT" != "" ]; then
		port=$USERMIN_PORT
	else
		port=20000
	fi
	perl -e 'use Socket; socket(FOO, PF_INET, SOCK_STREAM, getprotobyname("tcp")); setsockopt(FOO, SOL_SOCKET, SO_REUSEADDR, pack("l", 1)); bind(FOO, pack_sockaddr_in($ARGV[0], INADDR_ANY)) || exit(1); exit(0);' $port
	if [ "$?" != "0" ]; then
		echo Port $port is already in use
		exit 3
	fi
fi

%post
inetd=`grep "^inetd=" %{_sysconfdir}/usermin/miniserv.conf 2>/dev/null | sed -e 's/inetd=//g'`
if [ "$1" != 1 ]; then
	# Upgrading the RPM, so stop the old usermin properly
	if [ "" != "1" ]; then
%{_sysconfdir}/init.d/usermin stop >/dev/null 2>&1
	fi
fi
cd %{_prefix}/libexec/usermin
config_dir=%{_sysconfdir}/usermin
var_dir=/var/usermin
perl=%{__perl}
autoos=3
if [ "$USERMIN_PORT" != "" ]; then
	port=$USERMIN_PORT
else
	port=20000
fi
host=`hostname`
ssl=1
atboot=1
nochown=1
autothird=1
noperlpath=1
nouninstall=1
nostart=1
export config_dir var_dir perl autoos port ssl nochown autothird noperlpath nouninstall nostart allow
./setup.sh >/tmp/.webmin/usermin-setup.out 2>&1
rm -f /var/lock/subsys/usermin
if [ "" != "1" ]; then
%{_sysconfdir}/init.d/usermin start >/dev/null 2>&1 </dev/null
fi
cat >%{_sysconfdir}/usermin/uninstall.sh <<EOFF
#!/bin/sh
printf "Are you sure you want to uninstall Usermin? (y/n) : "
read answer
printf "\n"
if [ "\$answer" = "y" ]; then
	echo "Removing usermin RPM .."
	rpm -e --nodeps usermin
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
grep root=%{_prefix}/libexec/usermin %{_sysconfdir}/usermin/miniserv.conf >/dev/null 2>&1
	if [ "$?" = 0 ]; then
		# RPM is being removed, and no new version of usermin
		# has taken it's place. Stop the server
%{_sysconfdir}/init.d/usermin stop >/dev/null 2>&1
		/bin/true
	fi
fi

%postun
if [ "$1" = 0 ]; then
grep root=%{_prefix}/libexec/usermin %{_sysconfdir}/usermin/miniserv.conf >/dev/null 2>&1
	if [ "$?" = 0 ]; then
		# RPM is being removed, and no new version of usermin
		# has taken it's place. Delete the config files
rm -rf %{_sysconfdir}/usermin /var/usermin
	fi
fi
