# /etc/nixos/home.nix
{ config, pkgs, ... }:

{
  home.username = "krist";
  home.homeDirectory = "/home/krist";
  home.stateVersion = "26.05";

  # ---------- Dev: языки и тулчейны ----------
  home.packages = with pkgs; [
    # --- C / C++ ---
    gcc
    clang
    clang-tools       # clangd, clang-format, clang-tidy
    cmake
    gnumake
    gdb
    valgrind
    ninja
    pkg-config

    # --- Ассемблер ---
    nasm
    yasm
    binutils          # objdump, readelf, as, ld и пр.

    # --- Java / Kotlin ---
    jdk21             # современный LTS JDK
    kotlin
    gradle
    maven

    # --- Go ---
    go
    gopls             # go language server
    golangci-lint

    # --- Python ---
    python3
    python3Packages.pip
    python3Packages.virtualenv
    pyright           # python language server

    # --- Редакторы / IDE ---
    vim
    vscode
    neovim
    jetbrains.idea  # IntelliJ IDEA Community (Java/Kotlin)

    # --- Системные dev-утилиты ---
    git
    gh
    direnv
    docker-compose
    strace
    ltrace
    htop
    btop

    # --- CLI-инструменты общего назначения ---
    ripgrep
    fzf
    fd
    jq
    tree
    bat
    eza
    unzip
    zip
    wget
    curl
    tmux

    # --- Повседневное: офис, медиа, архивы ---
    libreoffice
    vlc
    gimp
    flameshot          # скриншоты
    qbittorrent
    p7zip
    file-roller        # GUI-архиватор для GNOME
    #xfce.thunar
    #xfce.thunar-volman
    #xfce.thunar-archive-plugin
    #xfce.thunar-media-tags-plugin
    #xfce.tumbler

    # --- Файловый менеджер / утилиты GNOME-окружения ---
    nautilus
    nautilus-open-any-terminal
    sushi
    gnome-tweaks
    gnome-extension-manager
  ];

  programs.git = {
    enable = true;
    userName = "kristall268";
    userEmail = "kristall268@outlook.com";
    extraConfig = {
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
    extensions = with pkgs.vscode-extensions; [
      llvm-vs-code-extensions.vscode-clangd
      ms-vscode.cpptools
      golang.go
      ms-python.python
    ];
  };

  home.sessionVariables = {
    EDITOR = "nvim";
  };
}
