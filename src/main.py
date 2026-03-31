import json
import os
import subprocess
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango


class AppRow(Gtk.Box):
    def __init__(self, app_data):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.app_data = app_data

        self.add_css_class("app-card")
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.START)

        icon_name = app_data.get("icon", "application-x-executable")
        self.image = Gtk.Image.new_from_icon_name(icon_name)
        self.image.set_pixel_size(80)
        self.image.add_css_class("card-icon")
        self.append(self.image)

        title_label = Gtk.Label(label=app_data["name"])
        title_label.add_css_class("card-title")
        title_label.set_justify(Gtk.Justification.CENTER)
        self.append(title_label)

        subtitle_label = Gtk.Label(label=app_data.get("description", ""))
        subtitle_label.add_css_class("card-subtitle")
        subtitle_label.set_wrap(True)
        subtitle_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        subtitle_label.set_lines(3)
        subtitle_label.set_ellipsize(Pango.EllipsizeMode.END)
        subtitle_label.set_justify(Gtk.Justification.CENTER)
        self.append(subtitle_label)

        # Spacer to push button to bottom
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        self.append(spacer)

        self.button = Gtk.Button()
        self.spinner = Gtk.Spinner()
        self.button.set_halign(Gtk.Align.FILL)
        self.button.connect("clicked", self.on_button_clicked)
        self.append(self.button)
        self.update_button_state()

    def is_installed(self):
        pkg = self.app_data.get("package_name")
        if not pkg:
            return False
        res = subprocess.run(["rpm", "-q", pkg], capture_output=True)
        return res.returncode == 0

    def is_repo_enabled(self):
        repo_id = self.app_data.get("repo_id")
        if not repo_id:
            return True
            
        # Tenta o nome exato
        if os.path.exists(f"/etc/yum.repos.d/{repo_id}"):
            return True
            
        # Tenta o formato estendido do Fedora COPR
        if repo_id.startswith("_copr:"):
            parts = repo_id.split(":", 1)
            if len(parts) == 2:
                expanded_id = f"_copr:copr.fedorainfracloud.org:{parts[1]}"
                if os.path.exists(f"/etc/yum.repos.d/{expanded_id}"):
                    return True
                    
        return False

    def update_button_state(self, processing=False):
        self.button.remove_css_class("destructive-action")
        self.button.remove_css_class("suggested-action")
        self.button.remove_css_class("accent")
        self.button.set_sensitive(not processing)

        if processing:
            overlay_box = Gtk.Box(spacing=8, halign=Gtk.Align.CENTER)
            overlay_box.append(self.spinner)
            overlay_box.append(Gtk.Label(label="Aguarde..."))
            self.button.set_child(overlay_box)
            self.spinner.start()
            return

        self.spinner.stop()
        label_text = ""
        if self.is_installed():
            label_text = "Remover"
            self.button.add_css_class("destructive-action")
        elif not self.is_repo_enabled():
            label_text = "Habilitar Repo"
            self.button.add_css_class("accent")
        else:
            label_text = "Instalar"
            self.button.add_css_class("suggested-action")

        self.button.set_label(label_text)

    def on_button_clicked(self, button):
        if self.is_installed():
            raw_cmd = f"dnf remove -y {self.app_data['package_name']}"
        elif not self.is_repo_enabled():
            raw_cmd = self.app_data.get("repo_cmd")
        else:
            raw_cmd = self.app_data.get(
                "cmd", f"dnf install -y {self.app_data['package_name']}"
            )

        full_cmd = ["pkexec", "sh", "-c", f"{raw_cmd}"]

        self.update_button_state(processing=True)

        def run_task():
            try:
                subprocess.run(
                    full_cmd,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    check=False,
                    capture_output=True,
                )
            except Exception as e:
                print(f"[ERRO] {e}")

            GLib.idle_add(self.update_button_state, False)

        threading.Thread(target=run_task, daemon=True).start()


class FedoraAppStore(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.raell.FedoraAppStore",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.category_icons = {
            "navegadores": "network-browser-symbolic",
            "criadores": "camera-video-symbolic",
            "editores": "accessories-text-editor-symbolic",
            "terminal": "utilities-terminal-symbolic",
            "downloads": "folder-download-symbolic",
            "jogos": "input-gaming-symbolic",
            "performance": "utilities-system-monitor-symbolic",
            "shell": "terminal-symbolic",
            "media": "video-x-generic-symbolic",
            "comunicação": "chat-mixed-symbolic",
            "customização": "preferences-desktop-wallpaper-symbolic",
            "sistema": "emblem-system-symbolic",
        }

    def do_activate(self):
        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_default_size(1000, 700)
        self.win.set_title("Fedora App Store")

        # Configurar caminho dos dados (testes locais vs empacotamento RPM)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(base_path, "data")
        if not os.path.exists(os.path.join(self.data_path, "style.css")):
            self.data_path = "/usr/share/fedora-app-store/data"

        css_provider = Gtk.CssProvider()
        css_path = os.path.join(self.data_path, "style.css")
        try:
            css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                self.win.get_display(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
        except Exception as e:
            print(f"Erro ao carregar CSS: {e}")

        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

        self.load_apps_data()

        self.split_view = Adw.NavigationSplitView()
        sidebar_page = Adw.NavigationPage.new(self.create_sidebar(), "Categorias")
        self.split_view.set_sidebar(sidebar_page)

        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.content_stack.set_transition_duration(400)

        # Content area with ToolbarView
        self.toolbar_view = Adw.ToolbarView()
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)
        self.toolbar_view.set_content(self.content_stack)

        content_page = Adw.NavigationPage.new(self.toolbar_view, "Loja")
        self.split_view.set_content(content_page)

        self.win.set_content(self.split_view)
        self.build_ui_pages()
        self.win.present()

    def load_apps_data(self):
        json_path = os.path.join(self.data_path, "apps.json")
        try:
            with open(json_path, "r") as f:
                self.apps_db = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar JSON: {e}")
            self.apps_db = {}

    def create_sidebar(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_show_end_title_buttons(False)
        box.append(sidebar_header)

        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh_btn.set_tooltip_text("Atualizar Status")
        refresh_btn.connect("clicked", lambda x: self.refresh_all_buttons())
        sidebar_header.pack_start(refresh_btn)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.add_css_class("navigation-sidebar")
        self.sidebar_list.connect("row-selected", self.on_sidebar_changed)

        self.add_sidebar_item("inicio", "Início", "go-home-symbolic")

        for cat_key in self.apps_db.keys():
            icon = self.category_icons.get(cat_key, "folder-symbolic")
            self.add_sidebar_item(cat_key, cat_key.capitalize(), icon)

        scrolled.set_child(self.sidebar_list)
        box.append(scrolled)
        return box

    def add_sidebar_item(self, id, title, icon):
        row = Adw.ActionRow(title=title)
        row.add_prefix(Gtk.Image.new_from_icon_name(icon))
        row.id = id
        self.sidebar_list.append(row)

    def on_sidebar_changed(self, listbox, row):
        if row:
            self.content_stack.set_visible_child_name(row.id)
            # Smoothly hide sidebar on mobile if needed
            if self.split_view.get_collapsed():
                self.split_view.set_show_content(True)

    def build_ui_pages(self):
        # Início (StatusPage)
        status_page = Adw.StatusPage()
        status_page.set_title("Fedora App Store")
        status_page.set_description("Habilite repositórios e instale softwares nativos com facilidade.")
        
        # Carregar a logo personalizada a partir do caminho absoluto
        logo_path = os.path.join(self.data_path, "fedora-app-store.png")
        if os.path.exists(logo_path):
            try:
                texture = Gdk.Texture.new_from_filename(logo_path)
                status_page.set_paintable(texture)
            except Exception as e:
                print(f"Erro ao carregar a logo: {e}")
                status_page.set_icon_name("software-store-symbolic")
        else:
            status_page.set_icon_name("software-store-symbolic")
            
        status_page.add_css_class("welcome-page")

        welcome_clamp = Adw.Clamp()
        welcome_clamp.set_maximum_size(600)
        
        welcome_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        
        # Action Group for Repos
        repo_group = Adw.PreferencesGroup()
        repo_group.set_title("Configuração Inicial")
        repo_group.set_description("Prepare seu sistema para o melhor ecossistema de apps.")
        
        prepare_row = Adw.ActionRow(title="Habilitar Ecossistema")
        prepare_row.set_subtitle("RPM Fusion, Chrome e Steam")
        
        btn_prepare = Gtk.Button(label="🔓 Habilitar")
        btn_prepare.add_css_class("suggested-action")
        btn_prepare.set_valign(Gtk.Align.CENTER)
        btn_prepare.connect("clicked", self.on_prepare_clicked)
        prepare_row.add_suffix(btn_prepare)
        repo_group.add(prepare_row)
        
        # Papirus Row
        papirus_row = Adw.ActionRow(title="Instalar Tema Papirus")
        papirus_row.set_subtitle("Recomendado para ícones mais bonitos")
        
        btn_papirus = Gtk.Button(label="Instalar")
        btn_papirus.add_css_class("outline")
        btn_papirus.set_valign(Gtk.Align.CENTER)
        btn_papirus.connect("clicked", self.on_install_papirus_clicked)
        papirus_row.add_suffix(btn_papirus)
        repo_group.add(papirus_row)

        welcome_content.append(repo_group)
        welcome_clamp.set_child(welcome_content)
        
        # Add everything to a box inside StatusPage child? 
        # Actually StatusPage.set_child is for extra content.
        status_page.set_child(welcome_clamp)

        self.content_stack.add_named(status_page, "inicio")

        # App Pages
        self.app_rows = []
        for cat_key, apps in self.apps_db.items():
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

            clamp = Adw.Clamp()
            clamp.set_maximum_size(1100)
            clamp.set_margin_top(24)
            clamp.set_margin_bottom(24)
            scroll.set_child(clamp)

            flow_box = Gtk.FlowBox()
            flow_box.set_valign(Gtk.Align.START)
            flow_box.set_homogeneous(True)
            flow_box.set_selection_mode(Gtk.SelectionMode.NONE)
            flow_box.set_row_spacing(24)
            flow_box.set_column_spacing(24)

            clamp.set_child(flow_box)

            for app_data in apps:
                row = AppRow(app_data)
                flow_box.append(row)
                self.app_rows.append(row)

            self.content_stack.add_named(scroll, cat_key)

    def refresh_all_buttons(self):
        for row in self.app_rows:
            row.update_button_state()

    def on_prepare_clicked(self, btn):
        script = "dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm && dnf config-manager --set-enabled fedora-workstation-repositories && dnf config-manager addrepo --from-repofile=https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome.repo"

        full_cmd = ["pkexec", "sh", "-c", script]
        subprocess.Popen(full_cmd, stdin=subprocess.DEVNULL, start_new_session=True)

    def on_install_papirus_clicked(self, btn):
        full_cmd = ["pkexec", "dnf", "install", "-y", "papirus-icon-theme"]
        subprocess.Popen(full_cmd, stdin=subprocess.DEVNULL, start_new_session=True)


if __name__ == "__main__":
    app = FedoraAppStore()
    app.run(None)
