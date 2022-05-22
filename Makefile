# To be overwritten by user
PKGNAME=
DESTDIR=/

# Constants
BINDIR=/usr/bin/
LIBDIR=/usr/lib/
CFGDIR=/etc/

.PHONY: all
all: install

.PHONY: install
install:
	install -Dm0555 rotate-screen.py '$(DESTDIR)$(BINDIR)'rotate-screen
	install -Dm0644 -o0 example.cfg  '$(DESTDIR)$(CFGDIR)'rotate-screen.cfg

.PHONY: check-pkgname
check-pkgname:
	[ '$(PKGNAME)' != '' ]  # Variable PKGNAME must not be empty

# This does not remove the launcher from xfce4
.PHONY: clean
clean:
	rm -rf '$(DESTDIR)$(BINDIR)'rotate-screen
	rm -rf '$(DESTDIR)$(CFGDIR)'rotate-screen.cfg
