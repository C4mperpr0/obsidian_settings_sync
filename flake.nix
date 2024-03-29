{
  description = "Nix flake for obsidiansettingssync";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
      };
    in {
      packages.obsidiansettingssync = pkgs.callPackage ./derivation.nix {};
      packages.default = self.packages.${system}.obsidiansettingssync;
      devShells.default = let
        pythonPackages = with pkgs.python3Packages; [setuptools];
      in
        pkgs.mkShell
        {
          nativeBuildInputs = with pkgs;
            [
              python3
            ]
            ++ pythonPackages;
        };
    });
}
