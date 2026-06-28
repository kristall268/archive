# Edit this configuration file to define what should be installed on
# your system. Help is available in the configuration.nix(5) man page, on
# https://search.nixos.org/options and in the NixOS manual (`nixos-help`).

{ config, lib, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Use the systemd-boot EFI boot loader.
  #boot.loader.systemd-boot.enable = true;
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
  networking.hostName = "rog-zephyrus"; # Define your hostname

  # Set your time zone.
  time.timeZone = "Asia/Almaty";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";
  console = {
     font = "Lat2-Terminus16";
     keyMap = "us";
     #useXkbConfig = true; # use xkb.options in tty.
  };

  # Enable the X11 windowing system.
  services.xserver.enable = true;
  services.displayManager.gdm.enable = true;
  services.desktopManager.gnome.enable = true;
  services.gvfs.enable = true;
  services.udisks2.enable = true;
  #nixpkgs.file-roller.enable = true;

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
  # Enable sound.
  services.pulseaudio.enable = false;
  # OR
  security.rtkit.enable = true;
  services.pipewire = {
        enable = true;
	alsa.enable = true;
	alsa.support32Bit = true;
        pulse.enable = true;
};
  

  # ------------------- Bluetooth ----------------------------------
  hardware.bluetooth.enable = true;
  hardware.bluetooth.powerOnBoot = true;


  # Enable touchpad support (enabled default in most desktopManager).
  services.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.krist = {	
        isNormalUser = true;
        extraGroups = [ "wheel" "networkmanager" "video" "audio" "docker" ]; # Enable ‘sudo’ for the user.
	shell = pkgs.bash;
        packages = with pkgs; [	
                tree
    	];
};
 # List packages installed in system profile.
 # You can use https://search.nixos.org/ to find more packages (and options).
  environment.systemPackages = with pkgs; [
	git
	wget
	curl
	htop
	btop
	nvtopPackages.full
	asusctl
	supergfxctl
];
  services.asusd.enable = true;
  services.supergfxd.enable = true;
  virtualisation.docker.enable = true;
    
  hardware.cpu.amd.updateMicrocode = true;
  hardware.enableRedistributableFirmware = true;

  nix.settings.experimental-features = ["nix-command" "flakes"];
  nixpkgs.config.allowUnfree = true; 

  programs.firefox.enable = true;

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # Copy the NixOS configuration file and link it from the resulting system
  # (/run/current-system/configuration.nix). This is useful in case you
  # accdentally delete configuration.nix.
  # system.copySystemConfiguration = true;

  # This option defines the first version of NixOS you have installed on this particular machine,
  # and is used to maintain compatibility with application data (e.g. databases) created on older NixOS versions.
  #
  # Most users should NEVER change this value after the initial install, for any reason,
  # even if you've upgraded your system to a new NixOS release.
  #
  # This value does NOT affect the Nixpkgs version your packages and OS are pulled from,
  # so changing it will NOT upgrade your system - see https://nixos.org/manual/nixos/stable/#sec-upgrading for how
  # to actually do that.
  #
  # This value being lower than the current NixOS release does NOT mean your system is
  # out of date, out of support, or vulnerable.
  #
  # Do NOT change this value unless you have manually inspected all the changes it would make to your configuration,
  # and migrated your data accordingly.
  #
  # For more information, see `man configuration.nix` or https://nixos.org/manual/nixos/stable/options#opt-system.stateVersion .
  system.stateVersion = "26.05"; # Did you read the comment?

}

