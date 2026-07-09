{ config, pkgs, ... }:

{
  home.username = "krist";
  home.homeDirectory = "/home/krist";
  home.stateVersion = "26.05";

  # ---------- Dev: языки, тулчейны и пользовательский софт ----------
  home.packages = with pkgs; [
    # --- C / C++ ---
    gcc
    clang
    clang-tools
    cmake
    gnumake
    gdb
    valgrind
    ninja
    pkg-config

    # --- Ассемблер ---
    nasm
    yasm
    binutils

    # --- Java / Kotlin ---
    jdk21
    kotlin
    gradle
    maven

    # --- Go ---
    go
    gopls
    golangci-lint

    # --- Python ---
    python3
    python3Packages.pip
    python3Packages.virtualenv
    pyright

    # --- Редакторы / IDE ---
    jetbrains.idea

    # --- Системные dev-утилиты ---
    gh
    docker-compose
    strace
    ltrace

    # --- CLI-инструменты общего назначения ---
    ripgrep
    fzf
    fd
    jq
    tree
    bat
    eza
    tmux

    # --- Повседневное: офис, медиа, архивы ---
    libreoffice
    gimp
    flameshot
    qbittorrent
    vlc

    # =================================================================
    # === Пакеты GNOME ================================================
    # =================================================================
    # nautilus
    # nautilus-open-any-terminal
    # sushi
    # gnome-tweaks
    # gnome-extension-manager
    # file-roller
    # =================================================================
    # === конец пакетов GNOME ==========================================
    # =================================================================

    # =================================================================
    # === Пакеты KDE Plasma ============================================
    # =================================================================
    kdePackages.dolphin                # файловый менеджер (аналог nautilus)
    kdePackages.dolphin-plugins
    kdePackages.ark                    # архивы (аналог file-roller)
    kdePackages.kate                   # текстовый редактор
    kdePackages.konsole                # терминал
    kdePackages.spectacle              # скриншоты (аналог flameshot, но можно оставить оба)
    kdePackages.kcalc
    kdePackages.kcolorchooser
    kdePackages.filelight              # визуализация занятого места на диске
    kdePackages.partitionmanager
    kdePackages.plasma-systemmonitor
    kdePackages.kwalletmanager         # менеджер паролей/секретов KDE
    kdePackages.qtstyleplugin-kvantum  # движок тем для Qt-приложений
    # =================================================================
    # === конец пакетов KDE Plasma ======================================
    # =================================================================
  ];

  # Настройка Git
  programs.git = {
    enable = true;
    settings = {
      user.name = "kristall268";
      user.email = "kristall268@outlook.com";
      init.defaultBranch = "main";
      pull.rebase = false;
    };
  };

  programs.direnv = {
    enable = true;
    nix-direnv.enable = true;
  };

  programs.bash = {
    enable = true;
    shellAliases = {
      ll = "eza -la";
      gs = "git status";
      gp = "git pull";
      gc = "git commit";
      gco = "git checkout";
    };
  };

  programs.vscode = {
    enable = true;
  };

  # =================================================================
  # === Пакеты GNOME: dconf-настройки ================================
  # =================================================================
  # dconf.settings = {
  #   "org/gnome/desktop/interface" = {
  #     color-scheme = "prefer-dark";
  #   };
  # };
  # =================================================================
  # === конец GNOME dconf-настроек ====================================
  # =================================================================

  # =================================================================
  # === KDE Plasma: декларативная настройка через plasma-manager =====
  # =================================================================
  # Требует добавить вход plasma-manager в flake.nix и подключить
  # его как home-manager.sharedModules, иначе programs.plasma не появится.
  #
  # programs.plasma = {
  #   enable = true;
  #   workspace.theme = "breeze-dark";
  #   panels = [
  #     {
  #       location = "bottom";
  #       widgets = [ "org.kde.plasma.kickoff" "org.kde.plasma.taskmanager" "org.kde.plasma.systemtray" "org.kde.plasma.digitalclock" ];
  #     }
  #   ];
  # };
  # =================================================================
  # === конец KDE Plasma настроек ======================================
  # =================================================================

  home.sessionVariables = {
    EDITOR = "nvim";
    NIXOS_OZONE_WAYLAND = "1";
    MOZ_ENABLE_WAYLAND = "1";
  };
}
