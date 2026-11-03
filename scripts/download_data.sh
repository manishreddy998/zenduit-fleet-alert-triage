#!/usr/bin/env bash
# Downloads the Driver Behavior Dataset (Ferreira et al., PLOS ONE 2017) into data/driverBehavior
set -euo pipefail
cd "$(dirname "$0")/.."
B=https://raw.githubusercontent.com/jair-jr/driverBehaviorDataset/master/data
for t in 16 17 20 21; do
  mkdir -p data/driverBehavior/$t
  for f in aceleracaoLinear_terra.csv giroscopio_terra.csv groundTruth.csv viagem.json; do
    [ -s data/driverBehavior/$t/$f ] || curl -fsSL "$B/$t/$f" -o data/driverBehavior/$t/$f
  done
done
echo done
