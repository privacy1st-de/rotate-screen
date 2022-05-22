# Maintainer: Daniel Langbein <daniel@systemli.org>
_pkgname=rotate-screen
_reponame="$_pkgname"
pkgname="$_pkgname"
pkgver=0.1.1
pkgrel=1
pkgdesc="Script to rotate screen and devices such as touchscreen and pen input"
arch=('any')
url="https://codeberg.org/privacy1st/${_reponame}"
license=('CC0')
makedepends=('git')  # to fetch source(s) via git
source=("git+${url}.git")
sha256sums=('SKIP') # 'SKIP' for git sources

package() {
  cd "${_reponame}"
  make DESTDIR="$pkgdir/" install
}
