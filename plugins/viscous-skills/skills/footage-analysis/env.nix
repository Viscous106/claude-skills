# Tool environment for the vlog pipeline: `./run <cmd>` enters it.
let pkgs = import (builtins.getFlake "nixpkgs") { };
in pkgs.buildEnv {
  name = "vlog-env";
  paths = [
    pkgs.ffmpeg-full
    (pkgs.python3.withPackages (p: [ p.faster-whisper p.numpy p.pillow p.opencv4 p.librosa p.scenedetect ]))
  ];
}
