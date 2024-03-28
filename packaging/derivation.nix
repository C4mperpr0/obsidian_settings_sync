{ lib, python3Packages }:
with python3Packages;
buildPythonApplication rec {
  pname = "obsidiansettingssync";
  version = "1.2.5";
  pyproject = true;

  src = ./src/.;

  nativeBuildInputs = [
    setuptools
    wheel
    # added Packages
    # json
    #  os
    #  argparse
    #  copy
    #  subprocess
  ];

  propagatedBuildInputs = [
    python-daemon
  ];

  postInstall = "
    mv -v $out/bin/main.py $out/bin/obsidiansettingssync
  ";

  meta = with lib; {
    # ...
  };
}
