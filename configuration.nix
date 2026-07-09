# https://search.nixos.org/options and in the NixOS manual (`nixos-help`).

{ config, lib, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.grub = {
    enable = true;
    device = "nodev";
    efiSupport = true;
    efiInstallAsRemovable = false;
    useOSProber = true;
  };
  boot.loader.efi.efiSysMountPoint = "/boot/efi";
  
  # Use latest kernel.
  boot.kernelPackages = pkgs.linuxPackages_latest;

  # Configure network connections interactively with nmcli or nmtui.
  networking.networkmanager.enable = true;
  networking.hostName = "rog-zephyrus";

  # Set your time zone.
  time.timeZone = "Asia/Almaty";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";
  console = {
     font = "Lat2-Terminus16";
     keyMap = "us";
  };

  # Enable the X11 windowing system and GNOME.
  services.xserver.enable = true;
  services.displayManager.gdm.enable = true;
  services.desktopManager.gnome.enable = true;
  services.gvfs.enable = true;
  services.udisks2.enable = true;

  # Graphic settings
  hardware.graphics = {
    enable = true;
    enable32Bit = true;
  };

  hardware.nvidia = {
    modesetting.enable = true;
    powerManagement.enable = true;
    powerManagement.finegrained = true;
    open = false;
    nvidiaSettings = true;
    package = config.boot.kernelPackages.nvidiaPackages.stable;

    prime = {
      offload = {
        enable = true;
        enableOffloadCmd = true;
      };
      amdgpuBusId = "PCI:101:0:0";
      nvidiaBusId = "PCI:1:0:0";
    };
  };
  services.xserver.videoDrivers = ["nvidia"];

  # Enable sound with Pipewire.
  services.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  # Bluetooth
  hardware.bluetooth.enable = true;
  hardware.bluetooth.powerOnBoot = true;

  # Enable touchpad support.
  services.libinput.enable = true;

  # Define a user account.
  users.users.krist = {
    isNormalUser = true;
    extraGroups = [ "wheel" "networkmanager" "video" "audio" "docker" ];
    shell = pkgs.bash;
    packages = [];
  };

  # Системные пакеты (доступны всем пользователям и root) —
  # только то, что реально нужно на уровне root/системы
  environment.systemPackages = with pkgs; [
    # Системные dev/админ инструменты
    git
    wget
    curl
    htop
    btop
    nvtopPackages.full

    # Текстовые редакторы
    vim
    neovim

    # Утилиты ASUS
    asusctl
    supergfxctl

    # Сетевая диагностика
    dnsutils      # утилиты dig, nslookup
    traceroute

    # Диагностика железа
    lm_sensors    # команда sensors для температур
    pciutils      # команда lspci
    usbutils      # команда lsusb

    # Базовые системные архиваторы (чтобы root мог распаковать что угодно)
    unzip
    zip
    p7zip
  ];

  services.asusd.enable = true;
  services.supergfxd.enable = true;
  virtualisation.docker.enable = true;

  hardware.cpu.amd.updateMicrocode = true;
  hardware.enableRedistributableFirmware = true;

  nix.settings.experimental-features = ["nix-command" "flakes"];
  nixpkgs.config.allowUnfree = true;

  programs.firefox.enable = true;
  services.openssh.enable = true;

  system.stateVersion = "26.05";
}
