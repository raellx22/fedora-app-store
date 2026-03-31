Name:           fedora-app-store
Version:        1.0.0
Release:        1%{?dist}
Summary:        Uma loja de aplicativos simples para Fedora

License:        GPLv3+
URL:            https://github.com/raell/fedora-app-store
BuildArch:      noarch

Requires:       python3
Requires:       python3-gobject
Requires:       gtk4
Requires:       libadwaita
Requires:       polkit

%description
Uma loja de aplicativos moderna escrita em GTK4 e Libadwaita para facilitar
a instalação de softwares e a habilitação de repositórios no Fedora Linux.

%prep
# Não há nada para preparar, os arquivos já estão aqui

%build
# Aplicativo Python, sem etapa de compilação necessária

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/fedora-app-store/src
mkdir -p %{buildroot}%{_datadir}/fedora-app-store/data
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/512x512/apps

# Instalar o executável
install -p -m 755 %{_sourcedir}/fedora-app-store.sh %{buildroot}%{_bindir}/fedora-app-store

# Instalar código fonte e dados
install -p -m 644 %{_sourcedir}/src/main.py %{buildroot}%{_datadir}/fedora-app-store/src/
install -p -m 644 %{_sourcedir}/data/style.css %{buildroot}%{_datadir}/fedora-app-store/data/
install -p -m 644 %{_sourcedir}/data/apps.json %{buildroot}%{_datadir}/fedora-app-store/data/
install -p -m 644 %{_sourcedir}/data/fedora-app-store.png %{buildroot}%{_datadir}/fedora-app-store/data/

# Instalar o arquivo desktop
install -p -m 644 %{_sourcedir}/data/fedora-app-store.desktop %{buildroot}%{_datadir}/applications/

# Instalar o ícone do sistema para o menu
install -p -m 644 %{_sourcedir}/data/fedora-app-store.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/

%files
%{_bindir}/fedora-app-store
%{_datadir}/fedora-app-store/
%{_datadir}/applications/fedora-app-store.desktop
%{_datadir}/icons/hicolor/512x512/apps/fedora-app-store.png

%changelog
* Mon Mar 30 2026 Raell <raell@example.com> - 1.0.0-1
- Versão inicial com interface moderna GTK4/Libadwaita e logo personalizada.
