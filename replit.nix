{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.tkinter
    pkgs.xorg.xvfb
  ];
}
